"""Small fictional PDFs required by F's existing browser test; no real CV input.

The scan analogue contains only a generated grayscale image, with no text layer.
Use the existing runtime Python/pypdf and an ignored private output directory.
"""
from pathlib import Path
import sys
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, NumberObject, DecodedStreamObject


def make(output):
    output.mkdir(parents=True, exist_ok=True)
    for filename, text in [('text-resume.pdf', True), ('scanned-cv.pdf', False)]:
        writer = PdfWriter()
        page = writer.add_blank_page(width=612, height=792)
        stream = DecodedStreamObject()
        if text:
            font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                NameObject('/Subtype'): NameObject('/Type1'), NameObject('/BaseFont'): NameObject('/Helvetica')})
            page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'):
                DictionaryObject({NameObject('/F1'): writer._add_object(font)})})
            stream.set_data(b'BT /F1 12 Tf 50 700 Td (Fictional Resume Education and Experience) Tj ET')
        else:
            image = DecodedStreamObject()
            image.update({NameObject('/Type'): NameObject('/XObject'), NameObject('/Subtype'): NameObject('/Image'),
                NameObject('/Width'): NumberObject(32), NameObject('/Height'): NumberObject(32),
                NameObject('/ColorSpace'): NameObject('/DeviceGray'), NameObject('/BitsPerComponent'): NumberObject(8)})
            image.set_data(bytes(40 if 3 < y < 28 and y % 5 == 0 and 4 < x < 27 else 255
                for y in range(32) for x in range(32)))
            page[NameObject('/Resources')] = DictionaryObject({NameObject('/XObject'):
                DictionaryObject({NameObject('/Im0'): writer._add_object(image)})})
            stream.set_data(b'q 200 0 0 200 50 500 cm /Im0 Do Q')
        page[NameObject('/Contents')] = writer._add_object(stream)
        with (output / filename).open('wb') as handle:
            writer.write(handle)


if __name__ == '__main__':
    make(Path(sys.argv[1]))
