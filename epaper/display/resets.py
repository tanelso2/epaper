from abc import ABC, abstractmethod
from typing import Protocol, override

from PIL import Image

from epaper.display.wrapper import AsyncEPDWrapper
from epaper.utils.decorators import fds_before_after
import epaper.drawing.colors as colors


class ResetStrategy(ABC):
    @abstractmethod
    async def reset_display(self, e: AsyncEPDWrapper) -> None: ...


class ResetByClear(ResetStrategy):
    """
    Causes screen to flash black
    """

    @override
    async def reset_display(self, e: AsyncEPDWrapper) -> None:
        await e.clear()


class ResetByWhiteScreen(ResetStrategy):
    """
    Causes screen to flash black
    """

    @override
    async def reset_display(self, e: AsyncEPDWrapper) -> None:
        img = Image.new("1", (e.width, e.height), color=colors.WHITE)
        await e.display_image(img)


class ResetByPartialWhiteScreen(ResetStrategy):
    """
    Causes screen to flash white and doesn't fix burn-in
    """

    @override
    async def reset_display(self, e: AsyncEPDWrapper) -> None:
        img = Image.new("1", (e.width, e.height), color=colors.WHITE)
        await e.display_full_partial(img)


class ResetByReInit(ResetStrategy):
    """
    This one works pretty well, actually
    """

    @override
    async def reset_display(self, e: AsyncEPDWrapper) -> None:
        await e.init()
