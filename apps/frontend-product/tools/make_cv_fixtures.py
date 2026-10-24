"""Synthetic text and blank PDF fixtures for the F browser extraction check."""
import sys
from pathlib import Path
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
root = Path(sys.argv[1]); root.mkdir(parents=True, exist_ok=True)
for name, blank in [('text-resume.pdf', False), ('scanned-cv.pdf', True)]:
    writer = PdfWriter(); page = writer.add_blank_page(width=612, height=792)
    if not blank:
        page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): DictionaryObject({NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'), NameObject('/BaseFont'): NameObject('/Helvetica')})})})
        stream = DecodedStreamObject(); stream.set_data(b'BT /F1 12 Tf 50 700 Td (Fictional Resume Education and Experience) Tj ET'); page[NameObject('/Contents')] = stream
    with (root/name).open('wb') as output: writer.write(output)
