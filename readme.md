# Bulk Image Watermarker

A Python tool for adding watermarks to multiple images in bulk. Supports both image-based and text-based watermarks with customizable positioning, scaling, and transparency.

## Features

- Bulk process multiple images in a directory
- Support for both image and text watermarks
- Customizable watermark positioning (top-left, top-right, bottom-left, bottom-right, center)
- Adjustable watermark size and transparency
- Detailed logging of processing operations
- Supports multiple image formats (PNG, JPG, JPEG, BMP, WebP)

## Requirements

- Python 3.6+
- Pillow (PIL)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/bulk-image-watermarker.git
    cd bulk-image-watermarker
    ```

2. Install dependencies:
    ```bash
    pip install Pillow
    ```

## Usage

Basic usage with text watermark:
    ```bash
    python watermark-v0.1.py --input-dir "path/to/images" --watermark-text "My Watermark"
    ```

Using an image as watermark:
    ```bash
    python watermark-v0.1.py --input-dir "path/to/images" --logo-path "path/to/logo.png"
    ```

### Command Line Arguments

- `--input-dir`: (Required) Directory containing images to watermark
- `--output-dir`: Output directory for watermarked images (default: creates 'watermarked' subdirectory in input directory)
- `--logo-path`: Path to watermark image (if not provided, uses text watermark)
- `--watermark-text`: Text to use for watermark (default: "Watermark")
- `--scale`: Watermark size relative to image size (default: 0.1)
- `--position`: Watermark position (choices: top-left, top-right, bottom-left, bottom-right, center; default: top-right)
- `--transparency`: Watermark transparency (0-255, default: 128)

### Examples

Add a text watermark in the bottom-right corner:
    ```bash
    python watermark-v0.1.py --input-dir "photos" --watermark-text "Copyright 2024" --position "bottom-right"
    ```

Add a logo watermark with custom transparency:
    ```bash
    python watermark-v0.1.py --input-dir "photos" --logo-path "logo.png" --transparency 100
    ```

## Output

- Watermarked images are saved to the specified output directory (or 'watermarked' subdirectory by default)
- A log file is created in the output directory with processing details

## License

MIT License - See [LICENSE](LICENSE) file for details
