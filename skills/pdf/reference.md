# PDF Processing Advanced Reference

This document contains advanced PDF processing features, detailed examples, and additional libraries.

## pypdfium2 Library

### Render PDF to Images

```python
import pypdfium2 as pdfium
from PIL import Image

pdf = pdfium.PdfDocument("document.pdf")
page = pdf[0]
bitmap = page.render(scale=2.0, rotation=0)
img = bitmap.to_pil()
img.save("page_1.png", "PNG")
```

## JavaScript Libraries

### pdf-lib (MIT License)

```javascript
import { PDFDocument } from "pdf-lib";
import fs from "fs";

async function manipulatePDF() {
  const existingPdfBytes = fs.readFileSync("input.pdf");
  const pdfDoc = await PDFDocument.load(existingPdfBytes);

  const newPage = pdfDoc.addPage([600, 400]);
  newPage.drawText("Added by pdf-lib", { x: 100, y: 300, size: 16 });

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync("modified.pdf", pdfBytes);
}
```

## Command-Line Tools

### poppler-utils Advanced Features

```bash
# Extract text with bounding box coordinates
pdftotext -bbox-layout document.pdf output.xml

# Convert to PNG with high resolution
pdftoppm -png -r 300 document.pdf output_prefix

# Extract all embedded images
pdfimages -j -p document.pdf page_images
```

### qpdf Advanced Features

```bash
# Split PDF into groups of pages
qpdf --split-pages=3 input.pdf output_group_%02d.pdf

# Optimize PDF for web (linearize)
qpdf --linearize input.pdf optimized.pdf

# Add password protection
qpdf --encrypt user_pass owner_pass 256 --print=none --modify=none -- input.pdf encrypted.pdf
```

## Advanced Python Techniques

### pdfplumber Advanced Features

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]

    # Extract text with coordinates
    chars = page.chars
    for char in chars[:10]:
        print(f"Char: '{char['text']}' at x:{char['x0']:.1f} y:{char['y0']:.1f}")

    # Extract text by bounding box
    bbox_text = page.within_bbox((100, 100, 400, 200)).extract_text()
```

## Performance Tips

1. **For Large PDFs**: Use streaming approaches
2. **For Text Extraction**: `pdftotext -bbox-layout` is fastest
3. **For Image Extraction**: `pdfimages` is faster than rendering pages
4. **For Form Filling**: pdf-lib maintains form structure better

## Troubleshooting

### Encrypted PDFs

```python
from pypdf import PdfReader

reader = PdfReader("encrypted.pdf")
if reader.is_encrypted:
    reader.decrypt("password")
```

### Corrupted PDFs

```bash
qpdf --check corrupted.pdf
qpdf --replace-input corrupted.pdf
```

### Text Extraction Issues (Scanned PDFs)

```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path(pdf_path)
text = ""
for image in images:
    text += pytesseract.image_to_string(image)
```
