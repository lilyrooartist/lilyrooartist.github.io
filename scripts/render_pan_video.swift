import AppKit
import AVFoundation
import CoreImage
import CoreMedia
import Foundation

struct RenderConfig {
    let imageURL: URL
    let audioURL: URL
    let outputURL: URL
    let width: Int
    let height: Int
    let fps: Int32
    let zoom: CGFloat
}

enum RenderError: Error, CustomStringConvertible {
    case usage
    case invalidImage(URL)
    case invalidAudio(URL)
    case assetWriter(String)
    case pixelBufferPool
    case appendFailed
    case exportFailed(String)

    var description: String {
        switch self {
        case .usage:
            return "Usage: swift render_pan_video.swift <image> <audio.wav> <output.mp4>"
        case .invalidImage(let url):
            return "Could not open image at \(url.path)"
        case .invalidAudio(let url):
            return "Could not read audio duration at \(url.path)"
        case .assetWriter(let message):
            return "Asset writer failed: \(message)"
        case .pixelBufferPool:
            return "Could not create a pixel buffer from the writer pool"
        case .appendFailed:
            return "Could not append a rendered frame"
        case .exportFailed(let message):
            return "Export failed: \(message)"
        }
    }
}

func waitForWriter(_ writer: AVAssetWriter) throws {
    let semaphore = DispatchSemaphore(value: 0)
    writer.finishWriting {
        semaphore.signal()
    }
    semaphore.wait()
    if writer.status != .completed {
        throw RenderError.assetWriter(writer.error?.localizedDescription ?? "unknown writer error")
    }
}

func waitForExport(_ export: AVAssetExportSession) throws {
    let semaphore = DispatchSemaphore(value: 0)
    export.exportAsynchronously {
        semaphore.signal()
    }
    semaphore.wait()
    if export.status != .completed {
        throw RenderError.exportFailed(export.error?.localizedDescription ?? "unknown export error")
    }
}

func renderSilentPan(config: RenderConfig, duration: CMTime, tempVideoURL: URL) throws {
    try? FileManager.default.removeItem(at: tempVideoURL)

    guard let sourceImage = CIImage(contentsOf: config.imageURL) else {
        throw RenderError.invalidImage(config.imageURL)
    }

    let writer = try AVAssetWriter(outputURL: tempVideoURL, fileType: .mp4)
    let videoSettings: [String: Any] = [
        AVVideoCodecKey: AVVideoCodecType.h264,
        AVVideoWidthKey: config.width,
        AVVideoHeightKey: config.height,
        AVVideoCompressionPropertiesKey: [
            AVVideoAverageBitRateKey: 7_000_000,
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
        throw RenderError.assetWriter("video input could not be added")
    }
    writer.add(input)

    guard writer.startWriting() else {
        throw RenderError.assetWriter(writer.error?.localizedDescription ?? "could not start writer")
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

    let durationSeconds = CMTimeGetSeconds(duration)
    let frameCount = max(1, Int(ceil(durationSeconds * Double(config.fps))))

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

        let progress = frameCount <= 1 ? 1 : CGFloat(frameIndex) / CGFloat(frameCount - 1)
        let cropY = verticalTravel * progress
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

        if frameIndex > 0 && frameIndex % Int(config.fps * 10) == 0 {
            let seconds = Double(frameIndex) / Double(config.fps)
            print(String(format: "rendered %.0f / %.2f seconds", seconds, durationSeconds))
        }
    }

    input.markAsFinished()
    try waitForWriter(writer)
}

func combine(videoURL: URL, audioURL: URL, outputURL: URL, duration: CMTime) throws {
    try? FileManager.default.removeItem(at: outputURL)

    let composition = AVMutableComposition()
    let videoAsset = AVURLAsset(url: videoURL)
    let audioAsset = AVURLAsset(url: audioURL)

    guard let sourceVideoTrack = videoAsset.tracks(withMediaType: .video).first else {
        throw RenderError.assetWriter("temporary video has no video track")
    }
    guard let sourceAudioTrack = audioAsset.tracks(withMediaType: .audio).first else {
        throw RenderError.invalidAudio(audioURL)
    }

    guard let videoTrack = composition.addMutableTrack(
        withMediaType: .video,
        preferredTrackID: kCMPersistentTrackID_Invalid
    ) else {
        throw RenderError.assetWriter("could not create composition video track")
    }
    try videoTrack.insertTimeRange(
        CMTimeRange(start: .zero, duration: duration),
        of: sourceVideoTrack,
        at: .zero
    )
    videoTrack.preferredTransform = sourceVideoTrack.preferredTransform

    guard let audioTrack = composition.addMutableTrack(
        withMediaType: .audio,
        preferredTrackID: kCMPersistentTrackID_Invalid
    ) else {
        throw RenderError.assetWriter("could not create composition audio track")
    }
    try audioTrack.insertTimeRange(
        CMTimeRange(start: .zero, duration: duration),
        of: sourceAudioTrack,
        at: .zero
    )

    guard let export = AVAssetExportSession(
        asset: composition,
        presetName: AVAssetExportPresetHighestQuality
    ) else {
        throw RenderError.exportFailed("could not create export session")
    }

    export.outputURL = outputURL
    export.outputFileType = .mp4
    export.shouldOptimizeForNetworkUse = true
    export.timeRange = CMTimeRange(start: .zero, duration: duration)
    try waitForExport(export)
}

func main() throws {
    guard CommandLine.arguments.count == 4 else {
        throw RenderError.usage
    }

    let config = RenderConfig(
        imageURL: URL(fileURLWithPath: CommandLine.arguments[1]),
        audioURL: URL(fileURLWithPath: CommandLine.arguments[2]),
        outputURL: URL(fileURLWithPath: CommandLine.arguments[3]),
        width: 1920,
        height: 1080,
        fps: 30,
        zoom: 1.0
    )

    let audioAsset = AVURLAsset(url: config.audioURL)
    let duration = audioAsset.duration
    guard duration.isNumeric && CMTimeGetSeconds(duration) > 0 else {
        throw RenderError.invalidAudio(config.audioURL)
    }

    let tempVideoURL = config.outputURL
        .deletingLastPathComponent()
        .appendingPathComponent(".\(config.outputURL.deletingPathExtension().lastPathComponent).silent-pan.mp4")

    print(String(format: "rendering %.2f seconds at %d fps", CMTimeGetSeconds(duration), config.fps))
    try renderSilentPan(config: config, duration: duration, tempVideoURL: tempVideoURL)
    print("combining audio")
    try combine(videoURL: tempVideoURL, audioURL: config.audioURL, outputURL: config.outputURL, duration: duration)
    try? FileManager.default.removeItem(at: tempVideoURL)
    print("wrote \(config.outputURL.path)")
}

do {
    try main()
} catch {
    fputs("\(error)\n", stderr)
    exit(1)
}
