# File Converter

A clean, minimal PyQt6 application for converting files between formats.

## Features

- Drag & drop or file picker for multiple files
- Convert between image formats (PNG, JPG, TIFF, BMP, GIF, WEBP)
- Convert astronomical FITS files to/from images
- Convert multiple images to a single PDF
- Batch conversion with progress tracking

## Supported Formats

- **Images:** PNG, JPG, JPEG, TIFF, BMP, GIF, WEBP
- **Astronomical:** FIT, FITS
- **Documents:** PDF (from images)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Conversion Capabilities

| From | To |
|------|-----|
| PNG/JPG/TIFF/BMP/GIF/WEBP | PNG, JPG, TIFF, BMP, GIF, WEBP, PDF, FIT |
| FIT/FITS | PNG, JPG, TIFF, BMP, GIF, WEBP, PDF |
| Multiple images | Single PDF |

## Requirements

- Python 3.10+
- PyQt6
- Pillow
- astropy
- tifffile
- pypdf
- numpy
