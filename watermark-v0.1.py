import os
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from datetime import datetime
import logging
from typing import Tuple, Optional

def clean_path(path: str) -> str:
    """Clean path string by removing newlines and extra whitespace."""
    return path.strip().replace('\n', '').replace('\r', '')

class ImageWatermarker:
    def __init__(self, input_dir: str, output_dir: str, logo_path: str = None, watermark_text: str = "Watermark"):
        """Initialize the watermarker with directory paths and settings."""
        self.input_dir = clean_path(input_dir)
        self.output_dir = self._create_output_dir(clean_path(output_dir))
        self.logo_path = clean_path(logo_path) if logo_path else None
        self.watermark_text = watermark_text
        self.setup_logging()
        self.watermark_img = self._load_watermark()
        
    def setup_logging(self):
        """Set up logging configuration."""
        log_file = os.path.join(self.output_dir, f'watermark_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def _create_output_dir(self, output_dir: str) -> str:
        """Create output directory if it doesn't exist."""
        if not output_dir:
            output_dir = os.path.join(self.input_dir, 'watermarked')
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
        
    def _load_watermark(self) -> Image.Image:
        """Load watermark image or create text-based watermark."""
        try:
            if self.logo_path:
                watermark = Image.open(self.logo_path)
                logging.info(f"Watermark loaded: {watermark.size}, {watermark.mode}")
                return watermark
        except (FileNotFoundError, AttributeError):
            logging.warning("Logo not found. Using text watermark instead.")
            
        # Create text-based watermark
        watermark = Image.new('RGBA', (150, 50), (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark)
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except OSError:
            font = ImageFont.load_default()
        draw.text((10, 10), self.watermark_text, font=font, fill=(0, 0, 0, 128))
        return watermark
        
    def resize_watermark(self, watermark: Image.Image, base_image: Image.Image, scale: float = 0.1) -> Image.Image:
        """Resize watermark proportionally based on base image size."""
        new_width = int(base_image.width * scale)
        new_height = int(watermark.height * (new_width / watermark.width))
        return watermark.resize((new_width, new_height), Image.LANCZOS)
        
    def calculate_position(self, image: Image.Image, watermark: Image.Image, position: str = 'top-right', padding: int = 10) -> Tuple[int, int]:
        """Calculate watermark position based on specified location."""
        positions = {
            'top-left': (padding, padding),
            'top-right': (image.width - watermark.width - padding, padding),
            'bottom-left': (padding, image.height - watermark.height - padding),
            'bottom-right': (image.width - watermark.width - padding, image.height - watermark.height - padding),
            'center': ((image.width - watermark.width) // 2, (image.height - watermark.height) // 2)
        }
        return positions.get(position, positions['top-right'])
        
    def add_watermark(self, image: Image.Image, watermark: Image.Image, position: Tuple[int, int], 
                      transparency: int = 128) -> Image.Image:
        """Add watermark to image with specified transparency."""
        if watermark.mode != 'RGBA':
            watermark = watermark.convert('RGBA')
            
        # Adjust transparency
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(transparency / 255)
        watermark.putalpha(alpha)
        
        # Create transparent overlay
        transparent = Image.new('RGBA', image.size, (0, 0, 0, 0))
        transparent.paste(image, (0, 0))
        transparent.paste(watermark, position, mask=watermark)
        return transparent.convert('RGB')
        
    def process_image(self, filename: str, scale: float = 0.1, position: str = 'top-right',
                     transparency: int = 128) -> Optional[str]:
        """Process a single image with watermark."""
        img_path = os.path.join(self.input_dir, filename)
        try:
            img = Image.open(img_path)
            logging.info(f"Processing {filename}: {img.size}, {img.mode}")
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            scaled_watermark = self.resize_watermark(self.watermark_img, img, scale)
            watermark_position = self.calculate_position(img, scaled_watermark, position)
            watermarked_img = self.add_watermark(img, scaled_watermark, watermark_position, transparency)
            
            output_path = os.path.join(self.output_dir, filename)
            watermarked_img.save(output_path, quality=95)
            logging.info(f"Successfully processed: {filename}")
            return output_path
            
        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")
            return None
            
    def process_directory(self, scale: float = 0.1, position: str = 'top-right',
                         transparency: int = 128) -> Tuple[int, int]:
        """Process all compatible images in the input directory."""
        supported_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.webp'}
        successful = 0
        failed = 0
        
        for filename in os.listdir(self.input_dir):
            if os.path.splitext(filename)[1].lower() in supported_formats:
                result = self.process_image(filename, scale, position, transparency)
                if result:
                    successful += 1
                else:
                    failed += 1
                    
        return successful, failed

def main():
    parser = argparse.ArgumentParser(description='Bulk Image Watermarking Tool')
    parser.add_argument('--input-dir', required=True, help='Input directory containing images')
    parser.add_argument('--output-dir', help='Output directory for watermarked images')
    parser.add_argument('--logo-path', help='Path to watermark image')
    parser.add_argument('--watermark-text', default='Watermark', help='Text to use when creating text watermark')
    parser.add_argument('--scale', type=float, default=0.1, help='Watermark scale relative to image size')
    parser.add_argument('--position', default='top-right',
                      choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
                      help='Watermark position')
    parser.add_argument('--transparency', type=int, default=128,
                      help='Watermark transparency (0-255)')
    
    args = parser.parse_args()
    
    watermarker = ImageWatermarker(args.input_dir, args.output_dir, args.logo_path, args.watermark_text)
    successful, failed = watermarker.process_directory(args.scale, args.position, args.transparency)
    
    logging.info(f"Processing complete. Successful: {successful}, Failed: {failed}")

if __name__ == "__main__":
    main()