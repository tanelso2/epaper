from concurrent.futures import Executor
import logging
import sys
from typing import Optional, Literal

from PIL import Image

from epaper.display.mock import MockEPD
from epaper.display.protocol import EPDDisplay
import epaper.drawing.colors as colors
from epaper.utils.async_wrapper import PoolConfig, SyncToAsyncWrapper

logger = logging.getLogger(__name__)

type EPDInitMode = Literal["default", "partial", "fast", "4Gray"]


class AsyncEPDWrapper:
    _inner: EPDDisplay
    _async: SyncToAsyncWrapper[EPDDisplay]
    _init_status: Optional[EPDInitMode]

    def __init__(
        self, e: EPDDisplay, pool: PoolConfig | Executor | None = None
    ) -> None:
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

    async def display_and_sleep(self, img: Image.Image, partial=True) -> None:
        match self._init_status:
            case None:
                await self.init("partial" if partial else "default")
            case _:
                logger.debug(
                    "Display already initialized with mode %s", self._init_status
                )
        if partial:
            await self.display_full_partial(img)
        else:
            await self.display_image(img)
        await self.sleep()

    async def init(self, mode: EPDInitMode = "default"):
        if self._init_status is not None:
            raise IOError(
                f"Cannot initialize connection, already connected with mode {self._init_status}"
            )
        match mode:
            case "default":
                await self._async.init()
            case "partial":
                await self._async.init_part()
            case "fast":
                await self._async.init_fast()
        self._init_status = mode
        logger.debug(
            "Initialized connection to display with mode %s", self._init_status
        )

    async def init_part(self):
        await self._async.init_part()
        self._init_status = "partial"

    async def init_fast(self):
        await self._async.init_fast()
        self._init_status = "fast"

    async def clear(self):
        await self._async.Clear()

    async def sleep(self):
        await self._async.sleep()
        self._init_status = None


def get_display_wrapper(
    use_mock: bool = False, threaded: bool = False
) -> AsyncEPDWrapper:
    inst = get_display_instance(use_mock=use_mock)
    if threaded:
        pool_config = PoolConfig("thread", max_workers=1)
    else:
        pool_config = PoolConfig("process", max_workers=1)
    return AsyncEPDWrapper(inst, pool=pool_config)


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
