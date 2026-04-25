#!/usr/bin/env swift
import AppKit
import AVFoundation
import Foundation

let root = URL(fileURLWithPath: CommandLine.arguments.dropFirst().first ?? FileManager.default.currentDirectoryPath)
let exports = root.appendingPathComponent("exports", isDirectory: true)
try FileManager.default.createDirectory(at: exports, withIntermediateDirectories: true)

let outputURL = exports.appendingPathComponent("tiktok-app-review-demo.mp4")
try? FileManager.default.removeItem(at: outputURL)

let width = 1280
let height = 720
let fps = 30
let durationSeconds = 14
let totalFrames = fps * durationSeconds

let writer = try AVAssetWriter(outputURL: outputURL, fileType: .mp4)
let settings: [String: Any] = [
  AVVideoCodecKey: AVVideoCodecType.h264,
  AVVideoWidthKey: width,
  AVVideoHeightKey: height,
  AVVideoCompressionPropertiesKey: [
    AVVideoAverageBitRateKey: 4_000_000,
    AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel
  ]
]

let input = AVAssetWriterInput(mediaType: .video, outputSettings: settings)
input.expectsMediaDataInRealTime = false
let attributes: [String: Any] = [
  kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
  kCVPixelBufferWidthKey as String: width,
  kCVPixelBufferHeightKey as String: height
]
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: attributes)

guard writer.canAdd(input) else {
  fatalError("Cannot add video input")
}
writer.add(input)
writer.startWriting()
writer.startSession(atSourceTime: .zero)

let logo = NSImage(contentsOf: root.appendingPathComponent("assets/img/LR_logo_transparent.png"))
let homeShot = NSImage(contentsOf: exports.appendingPathComponent("tiktok-demo-home.png"))
let adminShot = NSImage(contentsOf: exports.appendingPathComponent("tiktok-demo-admin.png"))
let privacyShot = NSImage(contentsOf: exports.appendingPathComponent("tiktok-demo-privacy.png"))

func color(_ r: CGFloat, _ g: CGFloat, _ b: CGFloat, _ a: CGFloat = 1) -> NSColor {
  NSColor(calibratedRed: r / 255, green: g / 255, blue: b / 255, alpha: a)
}

let background = color(7, 7, 9)
let panel = color(18, 18, 25)
let gold = color(203, 168, 111)
let text = color(246, 244, 240)
let muted = color(182, 177, 169)
let red = color(139, 28, 43)

func drawText(_ value: String, x: CGFloat, y: CGFloat, w: CGFloat, size: CGFloat, weight: NSFont.Weight = .regular, foreground: NSColor = text, align: NSTextAlignment = .left) {
  let paragraph = NSMutableParagraphStyle()
  paragraph.alignment = align
  paragraph.lineBreakMode = .byWordWrapping
  let font = NSFont.systemFont(ofSize: size, weight: weight)
  let attrs: [NSAttributedString.Key: Any] = [
    .font: font,
    .foregroundColor: foreground,
    .paragraphStyle: paragraph
  ]
  let rect = NSRect(x: x, y: y, width: w, height: 220)
  (value as NSString).draw(with: rect, options: [.usesLineFragmentOrigin, .usesFontLeading], attributes: attrs)
}

func drawPill(_ value: String, x: CGFloat, y: CGFloat, w: CGFloat) {
  let path = NSBezierPath(roundedRect: NSRect(x: x, y: y, width: w, height: 42), xRadius: 21, yRadius: 21)
  color(42, 57, 103).setFill()
  path.fill()
  drawText(value, x: x, y: y + 10, w: w, size: 17, weight: .semibold, foreground: text, align: .center)
}

func drawImage(_ image: NSImage?, in rect: NSRect) {
  guard let image else { return }
  image.draw(in: rect, from: .zero, operation: .sourceOver, fraction: 1, respectFlipped: true, hints: [.interpolation: NSImageInterpolation.high])
}

func drawCard(_ rect: NSRect) {
  let path = NSBezierPath(roundedRect: rect, xRadius: 20, yRadius: 20)
  panel.setFill()
  path.fill()
  color(246, 244, 240, 0.16).setStroke()
  path.lineWidth = 1
  path.stroke()
}

func makePixelBuffer() -> CVPixelBuffer {
  var pixelBuffer: CVPixelBuffer?
  let status = CVPixelBufferCreate(kCFAllocatorDefault, width, height, kCVPixelFormatType_32ARGB, nil, &pixelBuffer)
  guard status == kCVReturnSuccess, let buffer = pixelBuffer else {
    fatalError("Could not create pixel buffer")
  }
  return buffer
}

func drawFrame(_ index: Int, into buffer: CVPixelBuffer) {
  CVPixelBufferLockBaseAddress(buffer, [])
  defer { CVPixelBufferUnlockBaseAddress(buffer, []) }

  guard let base = CVPixelBufferGetBaseAddress(buffer) else { return }
  let bytesPerRow = CVPixelBufferGetBytesPerRow(buffer)
  guard let context = CGContext(data: base, width: width, height: height, bitsPerComponent: 8, bytesPerRow: bytesPerRow, space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue) else { return }

  context.setFillColor(background.cgColor)
  context.fill(CGRect(x: 0, y: 0, width: width, height: height))
  context.setFillColor(red.withAlphaComponent(0.32).cgColor)
  context.fillEllipse(in: CGRect(x: -170, y: -110, width: 520, height: 520))
  context.setFillColor(gold.withAlphaComponent(0.22).cgColor)
  context.fillEllipse(in: CGRect(x: 930, y: -100, width: 460, height: 460))

  context.translateBy(x: 0, y: CGFloat(height))
  context.scaleBy(x: 1, y: -1)
  NSGraphicsContext.saveGraphicsState()
  NSGraphicsContext.current = NSGraphicsContext(cgContext: context, flipped: false)

  let seconds = Double(index) / Double(fps)
  drawText("LILY ROO WEBSITE", x: 52, y: 42, w: 520, size: 24, weight: .bold, foreground: gold)
  drawText("TikTok Content Posting API review demo", x: 52, y: 74, w: 760, size: 18, foreground: muted)
  drawImage(logo, in: NSRect(x: 1082, y: 36, width: 126, height: 126))

  if seconds < 3.2 {
    drawText("1. Public artist site", x: 64, y: 190, w: 480, size: 52, weight: .bold)
    drawText("The public site hosts release pages, videos, contact, Terms, and Privacy pages for Lily Roo.", x: 68, y: 272, w: 460, size: 24, foreground: muted)
    drawCard(NSRect(x: 590, y: 158, width: 600, height: 406))
    drawImage(homeShot, in: NSRect(x: 610, y: 178, width: 560, height: 366))
  } else if seconds < 6.4 {
    drawText("2. Admin queue", x: 64, y: 190, w: 480, size: 52, weight: .bold)
    drawText("The protected admin dashboard lists queued social posts and provides an Execute now action.", x: 68, y: 272, w: 460, size: 24, foreground: muted)
    drawPill("Execute now", x: 78, y: 382, w: 190)
    drawCard(NSRect(x: 590, y: 138, width: 600, height: 456))
    drawImage(adminShot, in: NSRect(x: 610, y: 158, width: 560, height: 416))
  } else if seconds < 9.6 {
    drawText("3. Server-side execution", x: 64, y: 170, w: 560, size: 50, weight: .bold)
    drawText("The browser sends the selected post to the Cloudflare Worker route. Social credentials stay server-side.", x: 68, y: 252, w: 520, size: 24, foreground: muted)
    drawCard(NSRect(x: 650, y: 174, width: 450, height: 118))
    drawText("/api/social/execute", x: 690, y: 216, w: 370, size: 28, weight: .semibold)
    drawCard(NSRect(x: 650, y: 354, width: 450, height: 118))
    drawText("TikTok video.publish", x: 690, y: 396, w: 370, size: 28, weight: .semibold)
    context.setStrokeColor(gold.cgColor)
    context.setLineWidth(5)
    context.move(to: CGPoint(x: 875, y: 305))
    context.addLine(to: CGPoint(x: 875, y: 342))
    context.strokePath()
  } else if seconds < 12.2 {
    drawText("4. App review materials", x: 64, y: 170, w: 560, size: 50, weight: .bold)
    drawText("The integration uses Login Kit and Content Posting API with user.info.basic, video.upload, and video.publish scopes.", x: 68, y: 252, w: 560, size: 24, foreground: muted)
    drawPill("Login Kit", x: 680, y: 220, w: 172)
    drawPill("Content Posting API", x: 876, y: 220, w: 266)
    drawPill("video.publish", x: 740, y: 300, w: 202)
    drawPill("video.upload", x: 966, y: 300, w: 186)
  } else {
    drawText("5. Legal and privacy pages", x: 64, y: 190, w: 560, size: 50, weight: .bold)
    drawText("Terms and Privacy URLs are public and linked from the site footer for review.", x: 68, y: 272, w: 520, size: 24, foreground: muted)
    drawCard(NSRect(x: 650, y: 146, width: 460, height: 420))
    drawImage(privacyShot, in: NSRect(x: 670, y: 166, width: 420, height: 380))
  }

  let progressWidth = CGFloat(index) / CGFloat(totalFrames - 1) * 1120
  color(246, 244, 240, 0.18).setFill()
  NSBezierPath(roundedRect: NSRect(x: 80, y: 650, width: 1120, height: 8), xRadius: 4, yRadius: 4).fill()
  gold.setFill()
  NSBezierPath(roundedRect: NSRect(x: 80, y: 650, width: progressWidth, height: 8), xRadius: 4, yRadius: 4).fill()

  NSGraphicsContext.restoreGraphicsState()
}

for frame in 0..<totalFrames {
  while !input.isReadyForMoreMediaData {
    Thread.sleep(forTimeInterval: 0.01)
  }
  let buffer = makePixelBuffer()
  drawFrame(frame, into: buffer)
  let time = CMTime(value: CMTimeValue(frame), timescale: CMTimeScale(fps))
  adaptor.append(buffer, withPresentationTime: time)
}

input.markAsFinished()
let group = DispatchGroup()
group.enter()
writer.finishWriting {
  group.leave()
}
group.wait()

if writer.status != .completed {
  fatalError("Video export failed: \(writer.error?.localizedDescription ?? "unknown error")")
}

print(outputURL.path)
