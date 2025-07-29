"""
Color representation:
    r: int
    g: int
    b: int

Color names:
    BLACK,
    WHITE,
    RED,
    GREEN,
    BLUE,
    YELLOW,
    PURPLE,
    CYAN,
    ORANGE,
    PINK

Writen by: professionsalincpp
"""
from enum import Enum


class RGBColor:
    def __init__(self, r: int, g: int, b: int) -> None:
        """
        Represents an RGB color
        """
        self.r: int = r
        self.g: int = g
        self.b: int = b
        if (r < 0 or r > 255) or (g < 0 or g > 255) or (b < 0 or b > 255):
            raise ValueError(
                f"Color values must be between 0 and 255, got {r}, {g}, {b}"
            )

class RGBAColor:
    def __init__(self, r: int, g: int, b: int, a: int) -> None:
        """
        Represents an RGBA color
        """
        self.r: int = r
        self.g: int = g
        self.b: int = b
        self.a: int = a
        if (a < 0 or a > 255) or (r < 0 or r > 255) or (g < 0 or g > 255) or (b < 0 or b > 255):
            raise ValueError(
                f"Color values must be between 0 and 255, got {r}, {g}, {b}, {a}"
            )


class ColorBlendMode(Enum):
    MIX = 0,
    ADD = 1
    SUB = 2,
    MIN = 3,
    MAX = 4

class Colors:
    NONE = 0
    BLACK = RGBColor(0, 0, 0)
    WHITE = RGBColor(255, 255, 255)
    RED = RGBColor(255, 0, 0)
    GREEN = RGBColor(0, 255, 0)
    BLUE = RGBColor(0, 0, 255)
    YELLOW = RGBColor(255, 255, 0)
    PURPLE = RGBColor(128, 0, 128)
    CYAN = RGBColor(0, 255, 255)
    ORANGE = RGBColor(255, 165, 0)
    PINK = RGBColor(255, 192, 203)
    GREY = RGBColor(128, 128, 128)

    @classmethod
    def get_color(cls, color_name):
        return getattr(cls, color_name.upper())

    @classmethod
    def get_all_colors(cls):
        return [attr for attr in dir(cls) if not attr.startswith('__')]
    
    @classmethod
    def to_rgba(cls, color: RGBColor, alpha: int = 255) -> RGBAColor:
        if isinstance(color, RGBColor):
            return RGBAColor(color.r, color.g, color.b, alpha)
        elif isinstance(color, RGBAColor):
            return RGBAColor(color.r, color.g, color.b, color.a)
        elif isinstance(color, AnsiColor):
            return RGBAColor(0, 0, 0, alpha)
        else:
            raise ValueError("Color must be an RGBColor object")
        
    @classmethod
    def to_rgb(cls, color: RGBAColor) -> RGBColor:
        if isinstance(color, RGBAColor) or isinstance(color, RGBColor):
            return RGBColor(color.r, color.g, color.b)
        else:
            raise ValueError("Color must be an RGBAColor object")
    
    @classmethod
    def blend_mix(cls, priority_color: RGBAColor, background_color: RGBAColor) -> RGBColor:
        """
        Blends the priority color with the background color
        e.g if priority color alpha is 255, then color will be as priority color instead of mixing
        """
        ratio = priority_color.a / 255
        bg_ratio = (255 - priority_color.a) / 255
        r = int(priority_color.r * ratio)
        g = int(priority_color.g * ratio)
        b = int(priority_color.b * ratio)
        r += int(background_color.r * bg_ratio)
        g += int(background_color.g * bg_ratio)
        b += int(background_color.b * bg_ratio)
        return RGBColor(r, g, b)
    
    @classmethod
    def blend_add(cls, priority_color: RGBAColor, background_color: RGBAColor) -> RGBColor:
        r = int(priority_color.r + background_color.r)
        g = int(priority_color.g + background_color.g)
        b = int(priority_color.b + background_color.b)
        r = min(r, 255)
        g = min(g, 255)
        b = min(b, 255)

        return RGBColor(r, g, b)
    
    @classmethod
    def blend_sub(cls, priority_color: RGBAColor, background_color: RGBAColor) -> RGBColor:
        r = int(priority_color.r - background_color.r)
        g = int(priority_color.g - background_color.g)
        b = int(priority_color.b - background_color.b)
        r = max(r, 0)
        g = max(g, 0)
        b = max(b, 0)

        return RGBColor(r, g, b)
    
    @classmethod
    def blend_min(cls, priority_color: RGBAColor, background_color: RGBAColor) -> RGBColor:
        r = min(priority_color.r, background_color.r)
        g = min(priority_color.g, background_color.g)
        b = min(priority_color.b, background_color.b)

        return RGBColor(r, g, b)
    
    @classmethod
    def blend_max(cls, priority_color: RGBAColor, background_color: RGBAColor) -> RGBColor:
        r = max(priority_color.r, background_color.r)
        g = max(priority_color.g, background_color.g)
        b = max(priority_color.b, background_color.b)

        return RGBColor(r, g, b)
    
    @classmethod
    def blend(cls, priority_color: RGBAColor, background_color: RGBAColor, mode: ColorBlendMode) -> RGBColor:
        if mode == ColorBlendMode.MIX:
            return cls.blend_mix(priority_color, background_color)
        elif mode == ColorBlendMode.ADD:
            return cls.blend_add(priority_color, background_color)
        elif mode == ColorBlendMode.SUB:
            return cls.blend_sub(priority_color, background_color)
        elif mode == ColorBlendMode.MIN:
            return cls.blend_min(priority_color, background_color)
        if mode == ColorBlendMode.MAX:
            return cls.blend_max(priority_color, background_color)
        else:
            raise ValueError("Mode must be either ColorBlendMode.MIX or ColorBlendMode.ADD")

