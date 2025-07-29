"""
Painter module

This module contains functions to paint on a canvas

Writen by: professionsalincpp
"""

from .colors import Colors, RGBAColor, RGBColor
from .canvas import Canvas
from PIL import Image, ImageDraw

class Painter:
    def paint_rectangle(self, canvas: Canvas, x1: int, y1: int, x2: int, y2: int, color: RGBAColor | RGBColor):
        """
        Paints a rectangle on a canvas

        Args:
            canvas (Canvas): Canvas to draw on
            x1 (int): X coordinate of the top left corner of the rectangle
            y1 (int): Y coordinate of the top left corner of the rectangle
            x2 (int): X coordinate of the bottom right corner of the rectangle
            y2 (int): Y coordinate of the bottom right corner of the rectangle
            color (RGBAColor | RGBColor): Color of the rectangle
        """
        for i in range(x1, x2):
            for j in range(y1, y2):
                canvas.set_pixel(i, j, color)

    def fill(self, canvas: Canvas, color: RGBColor | RGBAColor):
        """
        Paints the entire canvas with a single color

        Args:
            canvas (Canvas): Canvas to draw on
            color (RGBAColor | RGBColor): Color to paint the canvas with
        """
        if isinstance(color, RGBColor):
            color = Colors.to_rgba(color)
        for i in range(canvas.size[0]):
            for j in range(canvas.size[1]):
                canvas.set_pixel(i, j, color)

    def paint_image(self, canvas: Canvas, x: int, y: int, image: Image.Image):
        """
        Paints an image on a canvas

        Args:
            canvas (Canvas): Canvas to draw on
            x (int): X coordinate of the top left corner of the image
            y (int): Y coordinate of the top left corner of the image
            image (Image.Image): Image to draw
        """
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        for i in range(image.size[0]):
            for j in range(image.size[1]):
                original_color = image.getpixel((i, j))
                rgba_color = RGBAColor(original_color[0], original_color[1], original_color[2], original_color[3])
                canvas.set_pixel(i + x, j + y, rgba_color)

    def paint_circle(self, canvas: Canvas, x: int, y: int, radius: int, color: RGBAColor | RGBColor):
        """
        Paints a circle on a canvas

        Args:
            canvas (Canvas): Canvas to draw on
            x (int): X coordinate of the center of the circle
            y (int): Y coordinate of the center of the circle
            radius (int): Radius of the circle
            color (RGBAColor | RGBColor): Color of the circle
        """
        
        color = Colors.to_rgba(color)
        image = Image.new('RGBA', (radius * 2 + 1, radius * 2 + 1), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((0, 0, radius * 2, radius * 2), fill=(color.r, color.g, color.b, color.a))
        self.paint_image(canvas, x - radius, y - radius, image)

    def paint_line(self, canvas: Canvas, x1: int, y1: int, x2: int, y2: int, color: RGBAColor | RGBColor):
        """
        Paints a line on a canvas

        Args:
            canvas (Canvas): Canvas to draw on
            x1 (int): X coordinate of the start of the line
            y1 (int): Y coordinate of the start of the line
            x2 (int): X coordinate of the end of the line
            y2 (int): Y coordinate of the end of the line
            color (RGBAColor | RGBColor): Color of the line
        """
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        for x in range(x1, x2):
            y = int(m * x + b)
            canvas.set_pixel(x, y, color)

    def paint_text(self, canvas: Canvas, x, y, text, color):
        """
        Paints text on a canvas

        Args:
            canvas (Canvas): Canvas to draw on
            x (int): X coordinate of the start of the text
            y (int): Y coordinate of the start of the text
            text (str): Text to draw
            color (RGBAColor | RGBColor): Color of the text
        """
        for i, char in enumerate(text):
            canvas.set_char(x + i + 1, y, char, color)

    def paint_pieslice(self, canvas: Canvas, x: int, y: int, radius: int, start_angle: float, end_angle: float, color: RGBAColor | RGBColor):
        """
        Paints a pie slice on a canvas

        Args:
            canvas (Canvas): Canvas to draw on
            x (int): X coordinate of the center of the pie slice
            y (int): Y coordinate of the center of the pie slice
            radius (int): Radius of the pie slice
            start_angle (float): Start angle of the pie slice
            end_angle (float): End angle of the pie slice
            color (RGBAColor | RGBColor): Color of the pie slice
        """
        color = Colors.to_rgba(color)
        image = Image.new('RGBA', (radius * 2 + 1, radius * 2 + 1), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.pieslice((0, 0, radius * 2, radius * 2), start_angle, end_angle, fill=(color.r, color.g, color.b, color.a))
        self.paint_image(canvas, x - radius, y - radius, image)