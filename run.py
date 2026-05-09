#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import logging
import sys
import time

import click
from PIL import Image

import epaper.display.resets as resets
from epaper.drawing.components import ImagePlanner, ImagePlannerConstructor
from epaper.drawing.images.burn_in import BurnInImagePlanner
from epaper.drawing.images.epaper import EPaperImagePlanner
from epaper.display.helpers import reset_screen, display_full_Partial
from epaper.display.wrapper import get_display_instance, get_display_wrapper


logger = logging.getLogger(__name__)


DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 480

DEFAULT_UPDATE_DELAY = 15.0

using_mock_display = False
drawing_bounding_boxes = False
UPDATE_DELAY = DEFAULT_UPDATE_DELAY


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option(
    "--use-mock-display",
    is_flag=True,
    help="Allow using the mock display driver. Will exit with an error code if this is not set and it fails to load the display drivers",
)
@click.option(
    "--draw-bounding-boxes",
    is_flag=True,
    help="Draw the bounding boxes for all components",
)
@click.option("--update-delay", type=float, default=DEFAULT_UPDATE_DELAY)
def cli(debug, use_mock_display, draw_bounding_boxes, update_delay):
    global using_mock_display, drawing_bounding_boxes, UPDATE_DELAY
    using_mock_display = use_mock_display
    drawing_bounding_boxes = draw_bounding_boxes
    UPDATE_DELAY = update_delay
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def update_loop():
    e = get_display_instance(use_mock=using_mock_display)
    image_planner = EPaperImagePlanner(
        width=e.width, height=e.height, draw_outlines=drawing_bounding_boxes
    )
    e.init()
    reset_screen(e)
    logger.info(f"{e.width=} {e.height=}")
    e.init_part()
    while True:
        img = image_planner.generate()
        match img:
            case Exception() as err:
                logger.error("Error generating image", exc_info=err)
            case Image.Image():
                logger.info("Writing new image")
                display_full_Partial(e, img)
        logger.debug("Sleeping for %d seconds", UPDATE_DELAY)
        time.sleep(UPDATE_DELAY)


reset_strategy: resets.ResetStrategy = resets.ResetByReInit()


async def async_update_loop(
    image_planner_builder: ImagePlannerConstructor,
    update_delay: float,
    threaded: bool = False,
):
    e = get_display_wrapper(use_mock=using_mock_display, threaded=threaded)
    image_planner = image_planner_builder(
        e.width, e.height, draw_outlines=drawing_bounding_boxes
    )
    await e.init()
    await e.blank_screen()
    while True:
        img = image_planner.generate()
        match img:
            case Exception() as err:
                logger.error("Error generating image", exc_info=err)
            case Image.Image():
                logger.info("Resetting display")
                await reset_strategy.reset_display(e)
                logger.info("Writing new image")
                await e.display_full_partial(img)
        logger.debug("Sleeping for %d seconds", update_delay)
        await asyncio.sleep(update_delay)


@cli.command()
def run():
    update_loop()


@cli.command()
@click.option(
    "--threaded",
    is_flag=True,
    help="Use a threaded executor pool instead of the default process one",
)
def run_async(threaded: bool):
    loop = asyncio.new_event_loop()
    task = loop.create_task(
        async_update_loop(
            EPaperImagePlanner.construct, threaded=threaded, update_delay=UPDATE_DELAY
        )
    )
    loop.run_until_complete(task)


@cli.command()
@click.option("--output-file", type=str, default="output.bmp")
def generate(output_file: str):
    image_planner = EPaperImagePlanner(width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT)
    img = image_planner.generate()
    match img:
        case Exception() as err:
            logger.error("Error generating image", exc_info=err)
            sys.exit(1)
        case Image.Image():
            logger.info("Saving generated image to %s", output_file)
            img.save(output_file)


@cli.command()
def burn_in_test():
    update_delay = 0.25 if UPDATE_DELAY == DEFAULT_UPDATE_DELAY else UPDATE_DELAY
    loop = asyncio.new_event_loop()
    task = loop.create_task(
        async_update_loop(BurnInImagePlanner.construct, update_delay=update_delay)
    )
    loop.run_until_complete(task)


if __name__ == "__main__":
    cli()
