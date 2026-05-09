from abc import ABC, abstractmethod
from typing import override

from PIL import Image

from epaper.display.wrapper import AsyncEPDWrapper
import epaper.drawing.colors as colors


class ResetStrategy(ABC):
    @abstractmethod
    async def reset_display(self, e: AsyncEPDWrapper) -> None: ...

    @property
    def name(self):
        return self.__class__.__name__


class DontReset(ResetStrategy):
    """
    Magic conch, what should we do?

    Nothing.
    """

    pass


# class ResetByClear(ResetStrategy):
#     """
#     Causes screen to flash black
#     """
#
#     @override
#     async def reset_display(self, e: AsyncEPDWrapper) -> None:
#         await e.clear()
#
#
# class ResetByWhiteScreen(ResetStrategy):
#     """
#     Causes screen to flash black
#     """
#
#     @override
#     async def reset_display(self, e: AsyncEPDWrapper) -> None:
#         img = Image.new("1", (e.width, e.height), color=colors.WHITE)
#         await e.display_image(img)
#
#
# class ResetByPartialWhiteScreen(ResetStrategy):
#     """
#     Causes screen to flash white and doesn't fix burn-in
#     """
#
#     @override
#     async def reset_display(self, e: AsyncEPDWrapper) -> None:
#         img = Image.new("1", (e.width, e.height), color=colors.WHITE)
#         await e.display_full_partial(img)
#
#
# class ResetByReInit(ResetStrategy):
#     """
#     Leaks file descriptors
#     """
#
#     @override
#     async def reset_display(self, e: AsyncEPDWrapper) -> None:
#         await e.init()
#
#
# class ResetByReInitPart(ResetStrategy):
#     """
#     Leaks file descriptors
#     """
#
#     @override
#     async def reset_display(self, e: AsyncEPDWrapper) -> None:
#         await e.init()
#
#
# class ResetByReInitFast(ResetStrategy):
#     """
#     Causes screen to flash inverted
#
#     Still leaks file descriptors
#     """
#
#     @override
#     async def reset_display(self, e: AsyncEPDWrapper) -> None:
#         await e.init_fast()


class ResetBySleepThenReInit(ResetStrategy):
    """
    Seems to work well and doesn't leak file descriptors
    """

    @override
    async def reset_display(self, e: AsyncEPDWrapper) -> None:
        await e.sleep()
        await e.init()


class ResetBySleepThenReInitPart(ResetStrategy):
    """
    Seems to work well and doesn't leak file descriptors
    """

    @override
    async def reset_display(self, e: AsyncEPDWrapper) -> None:
        await e.sleep()
        await e.init_part()
