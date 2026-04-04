import os

from PIL import ImageFont


def list_font_families() -> list[str]:
    font_dir = "/usr/share/fonts/truetype"
    return [f for f in os.listdir(font_dir) if os.path.isdir(os.path.join(font_dir, f))]


def list_fonts(family: str = "dejavu") -> list[str]:
    font_dir = "/usr/share/fonts/truetype"
    family_dir = os.path.join(font_dir, family)
    if not os.path.isdir(family_dir):
        raise ValueError(f"Font family '{family}' not found in {font_dir}")
    return [f for f in os.listdir(family_dir) if f.endswith(".ttf")]


def get_font_path(family: str = "dejavu", font_name: str = "DejaVuSerif.ttf") -> str:
    family_dir = os.path.join("/usr/share/fonts/truetype", family)
    if not os.path.isdir(family_dir):
        raise ValueError(
            f"Font family '{family}' not found in /usr/share/fonts/truetype"
        )
    font_path = os.path.join(family_dir, font_name)
    if not os.path.isfile(font_path):
        raise ValueError(f"Font '{font_name}' not found in family '{family}'")
    return font_path


def font(
    family: str = "dejavu", font_name: str = "DejaVuSerif.ttf", size: int = 24
) -> ImageFont.ImageFont:
    font_path = get_font_path(family, font_name)
    return ImageFont.truetype(font_path, size=size)
