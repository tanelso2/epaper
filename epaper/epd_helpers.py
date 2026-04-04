from PIL import Image

from waveshare_epd import epd7in5_V2 as epd


def display_Partial(epd: epd.EPD, img: Image.Image):
    epd.display_Partial(epd.getbuffer(img), 0, 0, epd.width, epd.height)


def display_image(epd: epd.EPD, img: Image.Image):
    epd.display(epd.getbuffer(img))


def display_filesystem_image(epd: epd.EPD, s: str):
    img = Image.open(s)
    display_image(epd, img)


def reset_screen(epd: epd.EPD, color=0xFF):
    image = Image.new("1", (epd.height, epd.width), color)
    display_image(epd, image)


def epd_module():
    return epd


_instance_cache = None


def epd_instance():
    global _instance_cache
    if _instance_cache is None:
        _instance_cache = epd.EPD()
    return _instance_cache
