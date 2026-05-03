from typing import Protocol

from PIL import Image

from epaper.display.protocol import EPDDisplay
from epaper.display.wrapper import AsyncEPDWrapper
import epaper.drawing.colors as colors


class ResetStrategy(Protocol):
    async def async_reset_display(self, e: AsyncEPDWrapper) -> None: ...


class ResetByClear(ResetStrategy):
    """
    Causes screen to flash black
    """
    async def async_reset_display(self, e: AsyncEPDWrapper) -> None:
        await e.clear()


class ResetByWhiteScreen(ResetStrategy):
    """
    Causes screen to flash black
    """
    async def async_reset_display(self, e: AsyncEPDWrapper) -> None:
        img = Image.new("1", (e.width, e.height), color=colors.WHITE)
        await e.display_image(img)


class ResetByPartialWhiteScreen(ResetStrategy):
    """
    Causes screen to flash white and doesn't fix burn-in
    """
    async def async_reset_display(self, e: AsyncEPDWrapper) -> None:
        img = Image.new("1", (e.width, e.height), color=colors.WHITE)
        await e.display_full_partial(img)


class ResetByReInit(ResetStrategy):
    """
    This one works pretty well, actually
    """
    async def async_reset_display(self, e: AsyncEPDWrapper) -> None:
        await e.init()
