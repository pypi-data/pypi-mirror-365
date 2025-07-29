"""
This module contains functions to get the ANSI code for a color

Writen by: professionsalincpp
"""
from .colors import RGBColor

class ColorMode:
    MODE_FG = 38
    MODE_BG = 48

def get_rgb_color_ansicode(color: RGBColor, mode: ColorMode = 38) -> str:
    """
    Returns the ANSI code for the given color (Only for RGBColor)
    """
    if not mode in [ColorMode.MODE_FG, ColorMode.MODE_BG]:
        raise ValueError(
            f"Mode must be either ColorMode.MODE_FG or ColorMode.MODE_BG, got {mode}"
        )
    return f"\033[{mode};2;{color.r};{color.g};{color.b}m"

def get_reset_ansicode() -> str:
    """
    Returns the ANSI code to reset the color
    """
    return "\033[0m"

def get_ansicode(color: RGBColor, mode: ColorMode = 38) -> str:
    """
    Returns the ANSI code for the given color
    """
    if isinstance(color, RGBColor):
        return get_rgb_color_ansicode(color, mode)
    else:
        raise ValueError(
            f"Color must be either AnsiColor or RGBColor, got {type(color)}"
        )
    
def set_cursor_position_ansicode(row: int, col: int) -> str:
    return f"\033[{row};{col}H"