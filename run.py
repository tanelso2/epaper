#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import logging
import sys
import time

import click
from PIL import Image

from epaper.image import EPaperImage
from epaper.display.helpers import reset_screen, display_full_Partial
from epaper.display.wrapper import get_display_instance, get_display_wrapper


logger = logging.getLogger(__name__)


DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 480

UPDATE_DELAY = 15.0

using_mock_display = False


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option(
    "--use-mock-display",
    is_flag=True,
    help="Allow using the mock display driver. Will exit with an error code if this is not set and it fails to load the display drivers",
)
def cli(debug, use_mock_display):
    global using_mock_display
    using_mock_display = use_mock_display
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def update_loop():
    e = get_display_instance(use_mock=using_mock_display)
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
                display_full_Partial(e, img)
        time.sleep(UPDATE_DELAY)


async def async_update_loop():
    e = get_display_wrapper(use_mock=using_mock_display)
    await e.init()
    await e.blank_screen()
    while True:
        img = EPaperImage(e.width, e.height).generate()
        match img:
            case Exception() as err:
                logger.error("Error generating image", exc_info=err)
            case Image.Image():
                logger.info("Writing new image")
                await e.display_full_partial(img)
        await asyncio.sleep(UPDATE_DELAY)


@cli.command()
def run():
    update_loop()


@cli.command()
def run_async():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(async_update_loop())


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
