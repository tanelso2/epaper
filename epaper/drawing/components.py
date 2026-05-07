from abc import ABC, abstractmethod
import logging
from typing import Optional, Protocol

from PIL import Image, ImageDraw

from epaper.components.core import Component, Position
from epaper.components.debugging import BoundingBoxComponent
from epaper.components.fonts import font
from epaper.components.text import TextComponent
import epaper.drawing.colors as colors

logger = logging.getLogger(__name__)


def generate_image(
    width: int,
    height: int,
    components: dict[str, Component],
    image_mode: str = "1",
    background_color=colors.WHITE,
    draw_outlines: bool = False,
) -> Image.Image:
    ret = Image.new(image_mode, (width, height), color=background_color)
    draw = ImageDraw.Draw(ret)
    for name, c in components.items():
        try:
            logger.debug(f"Drawing component: {name}")
            c.draw(draw)
        except Exception:
            logger.exception(f"Error drawing component: {name}")
    if draw_outlines:
        for name, c in components.items():
            b = BoundingBoxComponent(c)
            logger.debug(f"Trying to draw the outline for component: {name}")
            b.draw(draw)
    return ret


class ImagePlanner(ABC):
    width: int
    height: int
    draw_outlines: bool
    _top_components: dict[str, Component]
    _bottom_components: dict[str, Component]
    _prev_components: dict[str, Component]
    _curr_base_components: dict[str, Component]
    _curr_components: dict[str, Component]
    _curr_image: Optional[Image.Image]

    def __init__(self, width: int, height: int, draw_outlines: bool = False):
        self.width = width
        self.height = height
        self.draw_outlines = draw_outlines
        self._prev_components = {}
        self._curr_components = {}
        self._bottom_components = {}
        self._top_components = {}
        self._curr_image = None

    @property
    def center(self) -> tuple[int, int]:
        return (self.width // 2, self.height // 2)

    @abstractmethod
    def create_components(self) -> dict[str, Component]: ...

    def generate(self) -> Image.Image:
        self._prev_components = self._curr_components
        try:
            self._curr_base_components = self.create_components()
            self._curr_components = (
                # Merge dicts left to right (| operator prioritizes the second dict of the two)
                self._bottom_components
                | self._curr_base_components
                | self._top_components
            )
        except Exception as e:
            error_component = TextComponent(
                text=f"Error while generating components: {e}",
                font=font(size=32),
                pos=Position.centered_on(self.center),
            )
            self._curr_components = {"error": error_component}
        self._curr_image = generate_image(
            width=self.width,
            height=self.height,
            components=self._curr_components,
            draw_outlines=self.draw_outlines,
        )
        return self._curr_image

    def add_component_on_top(self, name: str, c: Component):
        self._top_components[name] = c

    def add_component_on_bottom(self, name: str, c: Component):
        self._bottom_components[name] = c

    def remove_component_from_top(self, name: str):
        if name in self._top_components:
            del self._top_components[name]
        else:
            raise AttributeError(f"Could not find top component named {name}")

    def remove_component_from_bottom(self, name: str):
        if name in self._bottom_components:
            del self._bottom_components[name]
        else:
            raise AttributeError(f"Could not find bottom component named {name}")

    @classmethod
    def construct(
        cls, width: int, height: int, *, draw_outlines: bool = False, **_
    ) -> "ImagePlanner":
        """
        Helper method to create a function that matches the ImagePlannerConstructor protocol
        """
        return cls(width=width, height=height, draw_outlines=draw_outlines)


class ImagePlannerConstructor(Protocol):
    def __call__(
        self,
        width: int,
        height: int,
        *,
        draw_outlines: bool = False,
        **kwargs,
    ) -> ImagePlanner: ...
