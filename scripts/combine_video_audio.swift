import AVFoundation
import CoreMedia
import Foundation

enum CombineError: Error, CustomStringConvertible {
    case usage
    case noVideoTrack
    case noAudioTrack
    case composition(String)
    case export(String)

    var description: String {
        switch self {
        case .usage:
            return "Usage: swift combine_video_audio.swift <video.mp4> <audio.wav> <output.mp4>"
        case .noVideoTrack:
            return "Input video has no video track"
        case .noAudioTrack:
            return "Input audio has no audio track"
        case .composition(let message):
            return "Composition failed: \(message)"
        case .export(let message):
            return "Export failed: \(message)"
        }
    }
}

func waitForExport(_ export: AVAssetExportSession) throws {
    let semaphore = DispatchSemaphore(value: 0)
    export.exportAsynchronously { semaphore.signal() }
    semaphore.wait()
    if export.status != .completed {
        throw CombineError.export(export.error?.localizedDescription ?? "unknown export error")
    }
}

func main() throws {
    guard CommandLine.arguments.count == 4 else {
        throw CombineError.usage
    }

    let videoURL = URL(fileURLWithPath: CommandLine.arguments[1])
    let audioURL = URL(fileURLWithPath: CommandLine.arguments[2])
    let outputURL = URL(fileURLWithPath: CommandLine.arguments[3])

    try? FileManager.default.removeItem(at: outputURL)

    let videoAsset = AVURLAsset(url: videoURL)
    let audioAsset = AVURLAsset(url: audioURL)
    let duration = min(videoAsset.duration, audioAsset.duration)

    let composition = AVMutableComposition()
    guard let sourceVideoTrack = videoAsset.tracks(withMediaType: .video).first else {
        throw CombineError.noVideoTrack
    }
    guard let sourceAudioTrack = audioAsset.tracks(withMediaType: .audio).first else {
        throw CombineError.noAudioTrack
    }

    guard let videoTrack = composition.addMutableTrack(
        withMediaType: .video,
        preferredTrackID: kCMPersistentTrackID_Invalid
    ) else {
        throw CombineError.composition("could not create video track")
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
        throw CombineError.composition("could not create audio track")
    }
    try audioTrack.insertTimeRange(
        CMTimeRange(start: .zero, duration: duration),
        of: sourceAudioTrack,
        at: .zero
    )

    guard let export = AVAssetExportSession(asset: composition, presetName: AVAssetExportPresetHighestQuality) else {
        throw CombineError.export("could not create export session")
    }
    export.outputURL = outputURL
    export.outputFileType = .mp4
    export.shouldOptimizeForNetworkUse = true
    export.timeRange = CMTimeRange(start: .zero, duration: duration)

    try waitForExport(export)
    print("wrote \(outputURL.path)")
}

do {
    try main()
} catch {
    fputs("\(error)\n", stderr)
    exit(1)
}
