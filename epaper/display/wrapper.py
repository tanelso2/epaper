import logging
import sys
from typing import Optional

from PIL import Image

from epaper.display.mock import MockEPD
from epaper.display.protocol import EPDDisplay
import epaper.drawing.colors as colors
from epaper.utils.async_wrapper import SyncToAsyncWrapper

logger = logging.getLogger(__name__)


class AsyncEPDWrapper:
    def __init__(self, e: EPDDisplay, pool=None) -> None:
        self._inner = e
        self._async = SyncToAsyncWrapper(obj=self._inner, pool=pool)

    # Properties
    @property
    def height(self) -> int:
        return self._inner.height

    @property
    def width(self) -> int:
        return self._inner.width

    async def _buffer(self, img: Image.Image) -> bytearray | list[int]:
        return await self._async.getbuffer(img)

    async def display_image(self, img: Image.Image) -> None:
        buffer = await self._buffer(img)
        await self._async.display(buffer)

    async def display_full_partial(self, img: Image.Image) -> None:
        buffer = await self._buffer(img)
        await self._async.display_Partial(buffer, 0, 0, self.width, self.height)

    async def blank_screen(self, color=colors.WHITE):
        image = Image.new("1", (self.height, self.width), color)
        await self.display_image(image)

    async def init(self):
        await self._async.init()
        await self._async.init_part()

    async def clear(self):
        await self._async.Clear()


def get_display_wrapper(use_mock: bool = False) -> AsyncEPDWrapper:
    inst = get_display_instance(use_mock=use_mock)
    return AsyncEPDWrapper(inst)


def get_display_instance(use_mock: bool = False) -> EPDDisplay:
    e: Optional[EPDDisplay] = None
    if use_mock:
        e = MockEPD()
        logger.warning("Using the mock implementation of the display driver")
    else:
        try:
            from waveshare_epd import epd7in5_V2 as epd

            e = epd.EPD()

            logger.info("Using the standard display driver")
        except ImportError as err:
            logger.error(
                "Could not import epd library, are you running on a Raspberry Pi with the proper libraries installed?",
                exc_info=err,
            )
            sys.exit(1)

    if not e:
        raise ImportError("Could not create an instance of EPDDisplay protocol")
    return e
