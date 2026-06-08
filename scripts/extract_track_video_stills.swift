import AVFoundation
import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

enum StillError: Error, CustomStringConvertible {
    case usage
    case imageDestination(URL)
    case imageGeneration(String)

    var description: String {
        switch self {
        case .usage:
            return "Usage: swift extract_track_video_stills.swift <video.mp4> <output-dir> <prefix>"
        case .imageDestination(let url):
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
        throw StillError.imageDestination(url)
    }
    CGImageDestinationAddImage(destination, image, [
        kCGImageDestinationLossyCompressionQuality: 0.92
    ] as CFDictionary)
    if !CGImageDestinationFinalize(destination) {
        throw StillError.imageDestination(url)
    }
}

func main() throws {
    guard CommandLine.arguments.count == 4 else {
        throw StillError.usage
    }
    let videoURL = URL(fileURLWithPath: CommandLine.arguments[1])
    let outputDir = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
    let prefix = CommandLine.arguments[3]
    try FileManager.default.createDirectory(at: outputDir, withIntermediateDirectories: true)

    let asset = AVURLAsset(url: videoURL)
    let duration = CMTimeGetSeconds(asset.duration)
    let generator = AVAssetImageGenerator(asset: asset)
    generator.appliesPreferredTrackTransform = true
    generator.requestedTimeToleranceBefore = .zero
    generator.requestedTimeToleranceAfter = .zero
    generator.maximumSize = CGSize(width: 960, height: 540)

    for (label, seconds) in [
        ("start", 0.5),
        ("middle", max(0.5, duration / 2)),
        ("end", max(0.5, duration - 0.5))
    ] {
        do {
            let image = try generator.copyCGImage(
                at: CMTime(seconds: seconds, preferredTimescale: 600),
                actualTime: nil
            )
            let outputURL = outputDir.appendingPathComponent("\(prefix)-\(label).jpg")
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
