from dataclasses import dataclass
from functools import partial
import logging

from PIL import Image

from epaper.display.protocol import EPDDisplay

logger = logging.getLogger(__name__)


@dataclass
class MockEPD(EPDDisplay):
    @property
    def width(self) -> int:
        return 640

    @property
    def height(self) -> int:
        return 480

    def do_nothing(self, name, *args, **kwargs):
        logger.debug(
            "Doing nothing instead of %s(*args: %s, **kwargs: %s)", name, args, kwargs
        )
        return None

    def __getattr__(self, name):
        """Anything we don't recognize, return a function that does nothing"""
        return partial(self.do_nothing, name)

    def init(self):
        self.do_nothing("init")

    def init_part(self):
        self.do_nothing("init_part")

    def init_fast(self):
        self.do_nothing("init_fast")

    def init_4Gray(self):
        self.do_nothing("init_4Gray")

    def getbuffer(self, image: Image.Image) -> bytearray | list[int]:
        logger.debug("Doing nothing instead of getbuffer. Returning empty list")
        return []

    def getbuffer_4Gray(self, image: Image.Image) -> bytearray | list[int]:
        logger.debug("Doing nothing instead of getbuffer_4Gray. Returning empty list")
        return []

    def display(self, image: Image.Image) -> None:
        self.do_nothing("display", image)

    def display_4Gray(self, image: Image.Image) -> None:
        self.do_nothing("display_4Gray", image)

    def display_Partial(
        self, image: Image.Image, Xstart: int, Ystart: int, Xend: int, Yend: int
    ) -> None:
        self.do_nothing("display_Partial", image, Xstart, Ystart, Xend, Yend)

    def Clear(self):
        self.do_nothing("Clear")

    def sleep(self):
        self.do_nothing("sleep")
