// Offline extraction for the acquired public aggregate MyCOL publication.
// Raw OCR stays in ignored B artifacts; only allowlisted aggregate facts ship.
import Foundation
import PDFKit
import Vision
import AppKit

struct Line: Codable {
    let text: String
    let x: Double
    let y: Double
    let width: Double
    let height: Double
}
struct PageResult: Codable { let pdf_page: Int; let lines: [Line] }
let args = CommandLine.arguments
guard args.count == 4, let document = PDFDocument(url: URL(fileURLWithPath: args[1])) else {
    fatalError("usage: extract_public_pdf PDF comma-separated-pages ignored-output.json")
}
let pages = args[2].split(separator: ",").compactMap { Int($0) }
guard pages.count <= 80, pages.allSatisfy({ $0 > 0 && $0 <= document.pageCount }) else {
    fatalError("bounded valid PDF page selection required")
}
var result: [PageResult] = []
for number in pages {
    try autoreleasepool {
        guard let page = document.page(at: number - 1) else { fatalError("missing page") }
        let bounds = page.bounds(for: .mediaBox)
        let width: CGFloat = 3200
        let size = NSSize(width: width, height: width * bounds.height / bounds.width)
        let image = page.thumbnail(of: size, for: .mediaBox)
        var rect = NSRect(origin: .zero, size: size)
        guard let cgImage = image.cgImage(forProposedRect: &rect, context: nil, hints: nil) else {
            fatalError("PDF rendering failed")
        }
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.recognitionLanguages = ["en-US"]
        request.usesLanguageCorrection = false
        try VNImageRequestHandler(cgImage: cgImage).perform([request])
        let lines = (request.results ?? []).compactMap { item -> Line? in
            guard let text = item.topCandidates(1).first?.string else { return nil }
            let b = item.boundingBox
            return Line(text: text, x: b.origin.x, y: b.origin.y, width: b.width, height: b.height)
        }
        result.append(PageResult(pdf_page: number, lines: lines))
        let encoded = try JSONEncoder().encode(result)
        try encoded.write(to: URL(fileURLWithPath: args[3]), options: .atomic)
    }
}
print("Extracted \(result.count) public publication pages; raw OCR retained locally.")
