"""Test script for file converter."""

import os
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.converter import convert_file, convert_to_pdf, batch_convert

# Create test directory
test_dir = Path(__file__).parent / "test_files"
test_dir.mkdir(exist_ok=True)

# Create a test PNG image
print("Creating test image...")
img = Image.new('RGB', (100, 100), color='red')
test_png = str(test_dir / "test_red.png")
img.save(test_png)
print(f"Created: {test_png}")

# Test 1: PNG to JPG
print("\nTest 1: PNG to JPG")
output_jpg = str(test_dir / "test_red.jpg")
try:
    convert_file(test_png, output_jpg, 'jpg')
    print(f"[OK] Converted to: {output_jpg}")
except Exception as e:
    print(f"[FAIL] Failed: {e}")

# Test 2: PNG to TIFF
print("\nTest 2: PNG to TIFF")
output_tiff = str(test_dir / "test_red.tiff")
try:
    convert_file(test_png, output_tiff, 'tiff')
    print(f"[OK] Converted to: {output_tiff}")
except Exception as e:
    print(f"[FAIL] Failed: {e}")

# Test 3: PNG to FITS
print("\nTest 3: PNG to FITS")
output_fit = str(test_dir / "test_red.fit")
try:
    convert_file(test_png, output_fit, 'fits')
    print(f"[OK] Converted to: {output_fit}")
except Exception as e:
    print(f"[FAIL] Failed: {e}")

# Test 4: FITS to PNG
print("\nTest 4: FITS to PNG")
output_from_fit = str(test_dir / "from_fit.png")
try:
    convert_file(output_fit, output_from_fit, 'png')
    print(f"[OK] Converted to: {output_from_fit}")
except Exception as e:
    print(f"[FAIL] Failed: {e}")

# Test 5: Multiple images to PDF
print("\nTest 5: Multiple images to PDF")
# Create another test image
img2 = Image.new('RGB', (100, 100), color='blue')
test_png2 = str(test_dir / "test_blue.png")
img2.save(test_png2)

output_pdf = str(test_dir / "combined.pdf")
try:
    convert_to_pdf([test_png, test_png2], output_pdf)
    print(f"[OK] Created PDF: {output_pdf}")
except Exception as e:
    print(f"[FAIL] Failed: {e}")

# Test 6: Batch convert
print("\nTest 6: Batch convert to BMP")
batch_output = str(test_dir / "batch")
try:
    results = batch_convert([test_png, test_png2], batch_output, 'bmp')
    print(f"[OK] Batch converted {len(results)} files")
    for r in results:
        print(f"  - {r}")
except Exception as e:
    print(f"[FAIL] Failed: {e}")

print("\n" + "="*50)
print("All tests completed!")
print(f"Test files in: {test_dir}")
