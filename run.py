#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import sys
import time

import click
from PIL import Image

from epaper.image import EPaperImage


logger = logging.getLogger(__name__)


DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 480


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
def cli(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@cli.command()
def run():
    try:
        from epaper.epd_helpers import display_Partial, reset_screen, epd_instance
    except ImportError:
        logger.error(
            "This script only works on a Raspberry Pi with the proper gpio libraries"
        )
        return 1
    e = epd_instance()
    e.init()
    reset_screen(e)
    logger.info(f"{e.width=} {e.height=}")
    e.init_part()
    while True:
        img = EPaperImage(e.width, e.height).generate()
        match img:
            case Exception() as err:
                logger.error("Error generating image", exc_info=err)
            case Image.Image():
                logger.info("Writing new image")
                display_Partial(e, img)
        time.sleep(15)


@cli.command()
def generate():
    img = EPaperImage(DEFAULT_WIDTH, DEFAULT_HEIGHT).generate()
    match img:
        case Exception() as err:
            logger.error("Error generating image", exc_info=err)
            sys.exit(1)
        case Image.Image():
            img.save("output.bmp")


if __name__ == "__main__":
    cli()
