from PIL import Image

from epaper.display.protocol import EPDDisplay
import epaper.drawing.colors as colors


def reset_screen(e: EPDDisplay):
    img = Image.new("1", (e.width, e.height), color=colors.WHITE)
    display_image(e, img)


def display_image(e: EPDDisplay, img: Image.Image):
    e.display(e.getbuffer(img))


def display_full_Partial(e: EPDDisplay, img: Image.Image):
    e.display_Partial(e.getbuffer(img), 0, 0, e.width, e.height)
