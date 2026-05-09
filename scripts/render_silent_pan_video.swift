import AVFoundation
import CoreImage
import CoreMedia
import Foundation

struct Config {
    let imageURL: URL
    let outputURL: URL
    let duration: Double
    let width: Int
    let height: Int
    let fps: Int32
    let zoom: CGFloat
}

enum RenderError: Error, CustomStringConvertible {
    case usage
    case invalidImage(URL)
    case writer(String)
    case pixelBufferPool
    case appendFailed

    var description: String {
        switch self {
        case .usage:
            return "Usage: swift render_silent_pan_video.swift <image> <output.mp4> <duration_seconds> [width height fps zoom]"
        case .invalidImage(let url):
            return "Could not open image at \(url.path)"
        case .writer(let message):
            return "Asset writer failed: \(message)"
        case .pixelBufferPool:
            return "Could not create a pixel buffer from the writer pool"
        case .appendFailed:
            return "Could not append a rendered frame"
        }
    }
}

func waitForWriter(_ writer: AVAssetWriter) throws {
    let semaphore = DispatchSemaphore(value: 0)
    writer.finishWriting { semaphore.signal() }
    semaphore.wait()
    if writer.status != .completed {
        throw RenderError.writer(writer.error?.localizedDescription ?? "unknown writer error")
    }
}

func smoothstep(_ x: CGFloat) -> CGFloat {
    let clamped = min(1, max(0, x))
    return clamped * clamped * (3 - 2 * clamped)
}

func panProgress(_ t: CGFloat) -> CGFloat {
    if t < 0.52 {
        return smoothstep(t / 0.52) * 0.10
    }
    return 0.10 + smoothstep((t - 0.52) / 0.48) * 0.52
}

func render(config: Config) throws {
    try? FileManager.default.removeItem(at: config.outputURL)

    guard let sourceImage = CIImage(contentsOf: config.imageURL) else {
        throw RenderError.invalidImage(config.imageURL)
    }

    let writer = try AVAssetWriter(outputURL: config.outputURL, fileType: .mp4)
    let videoSettings: [String: Any] = [
        AVVideoCodecKey: AVVideoCodecType.h264,
        AVVideoWidthKey: config.width,
        AVVideoHeightKey: config.height,
        AVVideoCompressionPropertiesKey: [
            AVVideoAverageBitRateKey: 8_000_000,
            AVVideoExpectedSourceFrameRateKey: config.fps,
            AVVideoMaxKeyFrameIntervalKey: config.fps * 2,
            AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel
        ]
    ]

    let input = AVAssetWriterInput(mediaType: .video, outputSettings: videoSettings)
    input.expectsMediaDataInRealTime = false

    let pixelAttributes: [String: Any] = [
        kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
        kCVPixelBufferWidthKey as String: config.width,
        kCVPixelBufferHeightKey as String: config.height,
        kCVPixelBufferIOSurfacePropertiesKey as String: [:]
    ]
    let adaptor = AVAssetWriterInputPixelBufferAdaptor(
        assetWriterInput: input,
        sourcePixelBufferAttributes: pixelAttributes
    )

    guard writer.canAdd(input) else {
        throw RenderError.writer("video input could not be added")
    }
    writer.add(input)

    guard writer.startWriting() else {
        throw RenderError.writer(writer.error?.localizedDescription ?? "could not start writer")
    }
    writer.startSession(atSourceTime: .zero)

    let ciContext = CIContext(options: [
        .workingColorSpace: CGColorSpaceCreateDeviceRGB(),
        .outputColorSpace: CGColorSpaceCreateDeviceRGB()
    ])
    let outputSize = CGSize(width: config.width, height: config.height)
    let coverScale = max(
        outputSize.width / sourceImage.extent.width,
        outputSize.height / sourceImage.extent.height
    )
    let renderScale = coverScale * config.zoom
    let scaled = sourceImage.transformed(by: CGAffineTransform(scaleX: renderScale, y: renderScale))
    let scaledExtent = scaled.extent
    let cropX = max(0, (scaledExtent.width - outputSize.width) / 2)
    let verticalTravel = max(0, scaledExtent.height - outputSize.height)
    let frameCount = max(1, Int(ceil(config.duration * Double(config.fps))))

    for frameIndex in 0..<frameCount {
        while !input.isReadyForMoreMediaData {
            Thread.sleep(forTimeInterval: 0.002)
        }

        guard let pool = adaptor.pixelBufferPool else {
            throw RenderError.pixelBufferPool
        }
        var maybeBuffer: CVPixelBuffer?
        CVPixelBufferPoolCreatePixelBuffer(nil, pool, &maybeBuffer)
        guard let pixelBuffer = maybeBuffer else {
            throw RenderError.pixelBufferPool
        }

        let t = frameCount <= 1 ? CGFloat(1) : CGFloat(frameIndex) / CGFloat(frameCount - 1)
        let cropY = verticalTravel * panProgress(t)
        let cropRect = CGRect(x: cropX, y: cropY, width: outputSize.width, height: outputSize.height)
        let frame = scaled
            .cropped(to: cropRect)
            .transformed(by: CGAffineTransform(translationX: -cropRect.minX, y: -cropRect.minY))

        ciContext.render(
            frame,
            to: pixelBuffer,
            bounds: CGRect(origin: .zero, size: outputSize),
            colorSpace: CGColorSpaceCreateDeviceRGB()
        )

        let presentationTime = CMTime(value: Int64(frameIndex), timescale: config.fps)
        guard adaptor.append(pixelBuffer, withPresentationTime: presentationTime) else {
            throw RenderError.appendFailed
        }
    }

    input.markAsFinished()
    try waitForWriter(writer)
}

func main() throws {
    guard CommandLine.arguments.count == 4 || CommandLine.arguments.count == 8 else {
        throw RenderError.usage
    }

    let duration = Double(CommandLine.arguments[3]) ?? 30
    let width = CommandLine.arguments.count == 8 ? (Int(CommandLine.arguments[4]) ?? 1920) : 1920
    let height = CommandLine.arguments.count == 8 ? (Int(CommandLine.arguments[5]) ?? 1080) : 1080
    let fps = CommandLine.arguments.count == 8 ? (Int32(CommandLine.arguments[6]) ?? 30) : 30
    let zoom = CommandLine.arguments.count == 8 ? CGFloat(Double(CommandLine.arguments[7]) ?? 1.0) : 1.0

    let config = Config(
        imageURL: URL(fileURLWithPath: CommandLine.arguments[1]),
        outputURL: URL(fileURLWithPath: CommandLine.arguments[2]),
        duration: duration,
        width: width,
        height: height,
        fps: fps,
        zoom: zoom
    )

    print(String(format: "rendering silent pan %.2fs at %dx%d %dfps", config.duration, config.width, config.height, config.fps))
    try render(config: config)
    print("wrote \(config.outputURL.path)")
}

do {
    try main()
} catch {
    fputs("\(error)\n", stderr)
    exit(1)
}
