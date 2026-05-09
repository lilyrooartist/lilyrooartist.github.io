import AVFoundation
import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

enum StillError: Error, CustomStringConvertible {
    case usage
    case noImageDestination(URL)
    case imageGeneration(String)

    var description: String {
        switch self {
        case .usage:
            return "Usage: swift extract_video_stills.swift <video.mp4> <output-dir>"
        case .noImageDestination(let url):
            return "Could not create image destination at \(url.path)"
        case .imageGeneration(let message):
            return "Could not extract still: \(message)"
        }
    }
}

func write(_ image: CGImage, to url: URL) throws {
    guard let destination = CGImageDestinationCreateWithURL(
        url as CFURL,
        UTType.jpeg.identifier as CFString,
        1,
        nil
    ) else {
        throw StillError.noImageDestination(url)
    }
    CGImageDestinationAddImage(destination, image, [
        kCGImageDestinationLossyCompressionQuality: 0.92
    ] as CFDictionary)
    if !CGImageDestinationFinalize(destination) {
        throw StillError.noImageDestination(url)
    }
}

func main() throws {
    guard CommandLine.arguments.count == 3 else {
        throw StillError.usage
    }

    let videoURL = URL(fileURLWithPath: CommandLine.arguments[1])
    let outputDir = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
    try FileManager.default.createDirectory(at: outputDir, withIntermediateDirectories: true)

    let asset = AVURLAsset(url: videoURL)
    let duration = CMTimeGetSeconds(asset.duration)
    let generator = AVAssetImageGenerator(asset: asset)
    generator.appliesPreferredTrackTransform = true
    generator.requestedTimeToleranceBefore = .zero
    generator.requestedTimeToleranceAfter = .zero
    generator.maximumSize = CGSize(width: 540, height: 960)

    let samples: [(String, Double)] = [
        ("start", 0.5),
        ("middle", max(0.5, duration / 2)),
        ("end", max(0.5, duration - 0.5))
    ]

    for (label, seconds) in samples {
        do {
            let image = try generator.copyCGImage(
                at: CMTime(seconds: seconds, preferredTimescale: 600),
                actualTime: nil
            )
            let outputURL = outputDir.appendingPathComponent("spilling-the-tea-pan-\(label).jpg")
            try write(image, to: outputURL)
            print(outputURL.path)
        } catch {
            throw StillError.imageGeneration(error.localizedDescription)
        }
    }
}

do {
    try main()
} catch {
    fputs("\(error)\n", stderr)
    exit(1)
}
