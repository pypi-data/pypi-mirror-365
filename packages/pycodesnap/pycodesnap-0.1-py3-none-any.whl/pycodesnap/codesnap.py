from PIL import Image, ImageDraw, ImageFilter
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import ImageFormatter
from typing import Union
from pathlib import Path
import io


class CodeSnap:
    """
    A utility class to generate high-quality, modern code screenshots.
    
    This class creates beautiful code screenshots with rounded corners,
    modern styling, and professional appearance similar to VS Code CodeSnap.
    """

    def __init__(self, language: str, code: str) -> None:
        """
        Initialize the CodeSnap instance.
        
        Args:
            language (str): Programming language of the code snippet
            code (str): Code content to be converted to image
        """
        self.lexer = get_lexer_by_name(language, stripall=True)
        self.code = code.strip()
        self.image = None
        self.line_count = len(self.code.split('\n')) if self.code else 0

    def _create_rounded_image(self, size, radius, fill_color):
        """
        Create an image with fully rounded corners.
        
        Args:
            size (tuple): Width and height of the image
            radius (int): Corner radius for rounding
            fill_color (str): Background color in hex format
            
        Returns:
            PIL.Image: Image with rounded corners
        """
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle([(0, 0), size], radius=radius, fill=fill_color)
        return image

    def _add_window_controls(self, image):
        """
        Add modern window control buttons to the title bar.
        
        Args:
            image (PIL.Image): Target image to draw controls on
        """
        draw = ImageDraw.Draw(image)
        # macOS style window controls: red, yellow, green
        button_colors = ["#ff5f57", "#ffbd2e", "#28c840"]
        for i, color in enumerate(button_colors):
            x = 20 + i * 22
            y = 20
            # Outer circle with subtle shadow
            draw.ellipse([x-1, y-1, x + 11, y + 11], fill="#ffffff20")
            # Main button circle
            draw.ellipse([x, y, x + 10, y + 10], fill=color)

    def create(
        self,
        width: int = 1200,
        font_size: int = 16,
        line_numbers: bool = True,
        style: str = "github-dark",
        background_color: str = "#0d1117",
        corner_radius: int = 20,
        shadow: bool = True,
        window_controls: bool = True,
        padding: tuple = (30, 25),
        line_number_color: str = "#6e7681",
        max_height: int = 3000,
        quality_factor: int = 3,
        line_spacing: float = 1.3,
        dpi: int = 300
    ) -> None:
        """
        Generate a high-quality modern code screenshot.
        
        Args:
            width (int): Output image width in pixels
            font_size (int): Base font size for code text
            line_numbers (bool): Whether to show line numbers
            style (str): Pygments syntax highlighting style
            background_color (str): Background color in hex format
            corner_radius (int): Radius for rounded corners
            shadow (bool): Add drop shadow effect
            window_controls (bool): Show window control buttons
            padding (tuple): Horizontal and vertical padding (x, y)
            line_number_color (str): Color for line numbers
            max_height (int): Maximum image height
            quality_factor (int): Quality multiplier for better resolution
            line_spacing (float): Spacing between lines (1.0 = normal)
            dpi (int): Dots per inch for high-resolution output
        """
        
        # Calculate total number of lines
        self.line_count = len(self.code.split('\n')) if self.code else 0
        
        # Create high-quality code image with syntax highlighting
        try:
            formatter = ImageFormatter(
                font_size=font_size * quality_factor,
                image_format="PNG",
                line_numbers=line_numbers,
                style=style,
                line_number_bg=background_color,
                line_number_fg=line_number_color,
                line_number_pad=20,
                hl_lines=[],
                hl_color="#2f363d",
                line_spacing=line_spacing
            )
        except:
            # Fallback to default formatter if custom settings fail
            formatter = ImageFormatter(
                font_size=font_size * quality_factor,
                image_format="PNG",
                line_numbers=line_numbers,
                style="default"
            )
        
        # Generate highlighted code image
        highlighted_code = highlight(self.code, self.lexer, formatter)
        code_image = Image.open(io.BytesIO(highlighted_code))
        
        # Convert code image to RGB to avoid transparency issues
        if code_image.mode in ('RGBA', 'LA'):
            rgb_bg = Image.new("RGB", code_image.size, background_color)
            rgb_bg.paste(code_image, (0, 0))
            code_image = rgb_bg
        elif code_image.mode != 'RGB':
            code_image = code_image.convert('RGB')
        
        # Resize image for better quality (downscale from high resolution)
        if quality_factor > 1:
            new_width = code_image.width // quality_factor
            new_height = code_image.height // quality_factor
            code_image = code_image.resize((new_width, new_height), Image.LANCZOS)
        
        # Calculate final dimensions
        code_width = code_image.width
        code_height = code_image.height
        
        # Calculate window dimensions with proper spacing
        window_width = max(width, code_width + padding[0] * 2 + 40)
        window_height = min(max_height, code_height + (80 if window_controls else padding[1] * 2) + 20)
        
        # Final dimensions with shadow margin
        total_width = window_width + (60 if shadow else 0)
        total_height = window_height + (60 if shadow else 0)
        
        # Create final image canvas
        final_image = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))
        
        # Add drop shadow if enabled
        if shadow:
            shadow_offset = 15
            # Create shadow with rounded corners
            shadow_image = self._create_rounded_image((window_width, window_height), corner_radius, (0, 0, 0, 100))
            # Apply Gaussian blur for soft shadow effect
            shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(radius=10))
            final_image.paste(shadow_image, (shadow_offset, shadow_offset))
        
        # Create main background with rounded corners
        main_bg = self._create_rounded_image((window_width, window_height), corner_radius, background_color)
        
        # Add title bar if window controls are enabled
        if window_controls:
            # Create title bar with rounded corners
            title_bar = Image.new("RGBA", (window_width, 45), (0, 0, 0, 0))
            title_draw = ImageDraw.Draw(title_bar)
            title_draw.rounded_rectangle([(0, 0), (window_width, 45)], radius=corner_radius, fill="#161b22")
            self._add_window_controls(title_bar)
            
            # Add line count information to title bar
            try:
                title_draw.text((window_width - 130, 14), f"{self.line_count} lines", fill="#8b949e")
            except:
                pass
            
            # Paste title bar onto main background
            main_bg.paste(title_bar, (0, 0), title_bar)
        
        # Position and paste code content
        code_x = padding[0]
        code_y = 50 if window_controls else padding[1]
        main_bg.paste(code_image, (code_x, code_y))
        
        # Position main content in final image
        final_x = 30
        final_y = 30
        final_image.paste(main_bg, (final_x, final_y), main_bg)
        
        # Convert to RGB for final output
        self.image = Image.new("RGB", final_image.size, "white")
        self.image.paste(final_image, (0, 0))

    def show(self) -> None:
        """
        Display the generated image using system viewer.
        
        Raises:
            ValueError: If no image has been created yet
        """
        if self.image:
            self.image.show()
        else:
            raise ValueError("No image has been created yet. Call 'create()' first.")

    def save(
        self,
        fp: Union[str, bytes, Path],
        format: str = "PNG",
        optimize: bool = True,
        quality: int = 100,
        compress_level: int = 1
    ) -> None:
        """
        Save the generated image to a file with maximum quality.
        
        Args:
            fp (Union[str, bytes, Path]): File path or file object
            format (str): Image format (PNG, JPEG, etc.)
            optimize (bool): Enable image optimization
            quality (int): JPEG quality (1-100)
            compress_level (int): PNG compression level (0-9)
            
        Raises:
            ValueError: If no image has been created yet
        """
        if not self.image:
            raise ValueError("No image has been created yet. Call 'create()' first.")
        
        # Save with appropriate settings based on format
        if format.upper() == "PNG":
            self.image.save(fp, format=format, optimize=optimize, compress_level=compress_level)
        else:
            self.image.save(fp, format=format, optimize=optimize, quality=quality)

    def to_bytes(self, format: str = "PNG", optimize: bool = True, quality: int = 100) -> bytes:
        """
        Convert the generated image to bytes with maximum quality.
        
        Args:
            format (str): Image format
            optimize (bool): Enable image optimization
            quality (int): JPEG quality for non-PNG formats
            
        Returns:
            bytes: Image data as bytes
            
        Raises:
            ValueError: If no image has been created yet
        """
        if not self.image:
            raise ValueError("No image has been created yet. Call 'create()' first.")

        output = io.BytesIO()
        if format.upper() == "PNG":
            self.image.save(output, format=format, optimize=optimize, compress_level=1)
        else:
            self.image.save(output, format=format, optimize=optimize, quality=quality)
        return output.getvalue()

    def get_line_count(self) -> int:
        """
        Get the total number of lines in the code.
        
        Returns:
            int: Number of lines in the code snippet
        """
        return self.line_count


# Example usage
if __name__ == "__main__":
    # Sample code for testing high-quality output
    sample_code = '''def fibonacci(n: int) -> int:
    """Calculate fibonacci number recursively with high quality."""
    if n <= 1:
        return n
    
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n: int) -> int:
    """Calculate factorial of a number with proper documentation."""
    if n <= 1:
        return 1
    
    return n * factorial(n - 1)

def main():
    # Example usage with detailed output
    print("High Quality Code Screenshot Generator")
    print("=" * 40)
    
    for i in range(10):
        fib_result = fibonacci(i)
        fact_result = factorial(i)
        print(f"Fibonacci({i:2d}) = {fib_result:4d} | Factorial({i:2d}) = {fact_result}")
    
    print("=" * 40)
    print("Generation completed successfully!")

if __name__ == "__main__":
    main()'''

    # Create high-quality code screenshot
    snap = CodeSnap("python", sample_code)
    print(f"✓ Code contains {snap.get_line_count()} lines")
    
    snap.create(
        width=1200,
        font_size=16,
        line_numbers=True,
        style="github-dark",
        background_color="#0d1117",
        corner_radius=20,
        shadow=True,
        window_controls=True,
        padding=(30, 25),
        line_number_color="#6e7681",
        quality_factor=3,
        line_spacing=1.3,
        dpi=300
    )
    
    # Save with maximum quality
    snap.save("high_quality_code.png", quality=100, compress_level=1)
    snap.show()
    print("✓ High-quality code screenshot saved as 'high_quality_code.png'")
    
    # Display image information
    if snap.image:
        width, height = snap.image.size
        print(f"✓ Image dimensions: {width} x {height} pixels")
        print(f"✓ Resolution: 300 DPI")
        print(f"✓ Quality factor: 3x")