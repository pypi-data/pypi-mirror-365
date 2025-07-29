import sys
from typing import Tuple
from .colors import Colors, ColorBlendMode, RGBAColor
from .ansi import *

class Canvas:
    """
    Canvas class
    """
    LOWER_SQUARE = "\u2584"
    UPPER_SQUARE = "\u2580"

    def __init__(self, size: Tuple[int, int], use_absolute_position: bool = False) -> None:
        """
        Initialize the canvas

        :param size: The size of the canvas
        :param use_absolute_position: Whether to use absolute position or not
        """
        self.size = size
        self.map = []
        self._blend_mode = ColorBlendMode.MIX
        self.text_map = []
        self.use_absolute_position = use_absolute_position
        self.resize(size)

    def resize(self, size: Tuple[int, int]) -> None:
        """
        Resize the canvas

        :param size: The new size of the canvas
        :return: None
        """
        self.size = size
        for _ in range(self.size[1]):
            self.map.append([Colors.NONE] * self.size[0])
        for _ in range(self.size[1] // 2 + 1):
            self.text_map.append([])
            for _ in range(self.size[0] + 1):
                self.text_map[-1].append((" ", Colors.NONE))

    @property
    def blend_mode(self) -> ColorBlendMode:
        return self._blend_mode
    
    @blend_mode.setter
    def blend_mode(self, value: ColorBlendMode) -> None:
        self._blend_mode = value

    def clear(self) -> None:
        """
        Clear the canvas
        - Clear the map
        - Clear the text map
        :Warning:
            This function does not clear console, it only clear the map.
        """
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                self.map[y][x] = Colors.NONE
        for y in range(self.size[1] // 2 + 1):
            for x in range(self.size[0] + 1):
                self.text_map[y][x] = (" ", Colors.NONE)

    def set_pixel(self, x: int, y: int, color: RGBColor | RGBAColor) -> None:
        """
        Set the pixel at the given position

        :param x: The x position of the pixel
        :param y: The y position of the pixel
        :param color: The color of the pixel
        """
        if isinstance(color, RGBColor):
            color = Colors.to_rgba(color)
        if color.a == 0:
            return
        if x > self.size[0] - 1 or y > self.size[1] - 1:
            return
        if x < 0 or y < 0:
            return
        result_color = RGBColor(color.r, color.g, color.b)
        if self.map[y][x] != Colors.NONE:
            result_color = Colors.blend(color, self.map[y][x], self.blend_mode)
        self.map[y][x] = result_color

    def set_char(self, x: int, y: int, char: str, color: Colors) -> None:
        """
        Set the character at the given position

        :param x: The x position of the character
        :param y: The y position of the character
        :param char: The character to set
        :param color: The color of the character
        """
        self.text_map[y][x] = (char, color)

    def get_pixel(self, x: int, y: int) -> str:
        """
        Get the color of the pixel at the given position
        
        :param x: The x position of the pixel
        :param y: The y position of the pixel
        :return: The color of the pixel
        """
        return self.map[y][x]

    def fix_map(self) -> None:
        """
        Fix the map if the size is odd
        """
        if len(self.map) % 2 == 1:
            self.map.append([Colors.NONE] * self.size[0])

    def paint(self) -> None:
        """
        Paint the canvas to the console from the map
        """
        x, y = 0, 0
        self.fix_map()
        while y < self.size[1]:
            while x < self.size[0]:
                color_top = self.map[y][x]
                color_bottom = self.map[y + 1][x]
                x += 1
                if self.use_absolute_position:
                    sys.stdout.write(set_cursor_position_ansicode(y // 2 + 1, x))
                if self.text_map[y // 2][x][0] != " ":
                    if color_top != Colors.NONE and color_bottom != Colors.NONE:
                        blended_color = Colors.blend(Colors.to_rgba(color_top), Colors.to_rgba(color_bottom), self.blend_mode)
                        sys.stdout.write(get_ansicode(Colors.to_rgb(blended_color), ColorMode.MODE_BG))
                    elif color_top != Colors.NONE:
                        sys.stdout.write(get_ansicode(color_top, ColorMode.MODE_FG))
                    elif color_bottom != Colors.NONE:
                        sys.stdout.write(get_ansicode(color_bottom, ColorMode.MODE_FG))
                    sys.stdout.write(get_ansicode(self.text_map[y // 2][x][1], ColorMode.MODE_FG))
                    sys.stdout.write(self.text_map[y // 2][x][0])
                    continue
                if color_top != Colors.NONE and color_bottom != Colors.NONE:
                    sys.stdout.write(get_ansicode(color_top, ColorMode.MODE_BG))
                if color_top == Colors.NONE and color_bottom == Colors.NONE:
                    sys.stdout.write(" ")
                if color_top != Colors.NONE and color_bottom == Colors.NONE:
                    sys.stdout.write(get_ansicode(color_top, ColorMode.MODE_FG))
                    sys.stdout.write(self.UPPER_SQUARE)
                if color_bottom != Colors.NONE:
                    sys.stdout.write(get_ansicode(color_bottom, ColorMode.MODE_FG))
                    sys.stdout.write(self.LOWER_SQUARE)
                sys.stdout.write(get_reset_ansicode())
            if not self.use_absolute_position:
                sys.stdout.write("\n")
            x = 0
            y += 2