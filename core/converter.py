"""File conversion core logic."""

import os
from pathlib import Path
from typing import List, Optional

import numpy as np
from PIL import Image
from astropy.io import fits
import tifffile
from pypdf import PdfWriter


# Supported formats
IMAGE_FORMATS = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'webp', 'tiff', 'tif'}
ASTRO_FORMATS = {'fit', 'fits'}
ALL_FORMATS = IMAGE_FORMATS | ASTRO_FORMATS | {'pdf'}


def get_file_extension(filepath: str) -> str:
    """Get lowercase file extension without dot."""
    return Path(filepath).suffix.lower().lstrip('.')


def normalize_format(fmt: str) -> str:
    """Normalize format string."""
    fmt = fmt.lower().lstrip('.')
    if fmt in ('jpeg', 'jpg'):
        return 'jpeg'
    if fmt in ('tif', 'tiff'):
        return 'tiff'
    if fmt in ('fit', 'fits'):
        return 'fits'
    return fmt


def load_fits_as_image(filepath: str) -> Image.Image:
    """Load FITS file and convert to PIL Image."""
    with fits.open(filepath) as hdul:
        data = hdul[0].data  # type: ignore
    
    if data is None:
        raise ValueError(f"No image data in FITS file: {filepath}")
    
    # Normalize to 0-255 range
    data = data.astype(np.float64)
    min_val, max_val = np.nanmin(data), np.nanmax(data)
    if max_val > min_val:
        data = ((data - min_val) / (max_val - min_val) * 255)
    data = np.nan_to_num(data, nan=0).astype(np.uint8)
    
    # Handle multi-dimensional FITS (take first 2D slice or RGB)
    if data.ndim == 3:
        if data.shape[0] <= 4:
            data = np.moveaxis(data, 0, -1)
        if data.shape[2] > 4:
            data = data[:, :, 0]
    
    if data.ndim == 2:
        return Image.fromarray(data, mode='L')
    elif data.shape[2] == 3:
        return Image.fromarray(data, mode='RGB')
    elif data.shape[2] == 4:
        return Image.fromarray(data, mode='RGBA')
    else:
        return Image.fromarray(data[:, :, 0], mode='L')


def save_image_as_fits(img: Image.Image, filepath: str):
    """Convert PIL Image to FITS and save."""
    if img.mode != 'L':
        img = img.convert('L')
    
    data = np.array(img)
    hdu = fits.PrimaryHDU(data)
    hdu.writeto(filepath, overwrite=True)


def load_image(filepath: str) -> Image.Image:
    """Load image file, handling FITS specially."""
    ext = get_file_extension(filepath)
    if ext in ASTRO_FORMATS:
        return load_fits_as_image(filepath)
    return Image.open(filepath)


def save_image(img: Image.Image, filepath: str, fmt: str):
    """Save image in specified format."""
    fmt = normalize_format(fmt)
    
    if fmt in ASTRO_FORMATS:
        save_image_as_fits(img, filepath)
    else:
        if fmt == 'jpeg' and img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        img.save(filepath, format=fmt.upper())


def convert_file(input_path: str, output_path: str, target_fmt: str) -> str:
    """Convert a single file to target format. Returns output path."""
    target_fmt = normalize_format(target_fmt)
    img = load_image(input_path)
    save_image(img, output_path, target_fmt)
    return output_path


def convert_to_pdf(image_paths: List[str], output_path: str) -> str:
    """Convert multiple images to a single PDF."""
    images = []
    for path in image_paths:
        img = load_image(path)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)
    
    if not images:
        raise ValueError("No images to convert")
    
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        format='PDF'
    )
    return output_path


def batch_convert(
    input_files: List[str],
    output_dir: str,
    target_fmt: str,
    progress_callback=None
) -> List[str]:
    """Convert multiple files to target format."""
    target_fmt = normalize_format(target_fmt)
    os.makedirs(output_dir, exist_ok=True)
    results = []
    
    # Special case: all images to single PDF
    if target_fmt == 'pdf' and len(input_files) > 1:
        output_path = os.path.join(output_dir, 'converted.pdf')
        convert_to_pdf(input_files, output_path)
        if progress_callback:
            progress_callback(len(input_files))
        return [output_path]
    
    for i, input_path in enumerate(input_files):
        stem = Path(input_path).stem
        ext = 'jpeg' if target_fmt == 'jpeg' else target_fmt
        if ext == 'fits':
            ext = 'fit'
        output_path = os.path.join(output_dir, f"{stem}.{ext}")
        
        try:
            convert_file(input_path, output_path, target_fmt)
            results.append(output_path)
        except Exception as e:
            print(f"Error converting {input_path}: {e}")
        
        if progress_callback:
            progress_callback(i + 1)
    
    return results
