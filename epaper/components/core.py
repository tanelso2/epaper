from dataclasses import dataclass
from functools import cached_property
import logging
from typing import Sequence, override, Literal

from PIL import ImageDraw

logger = logging.getLogger(__name__)


@dataclass
class BoundingBox:
    left: int
    top: int
    right: int
    bottom: int

    @staticmethod
    def rect(w: int, h: int) -> "BoundingBox":
        return BoundingBox(
            left=0,
            top=0,
            right=w,
            bottom=h,
        )

    @staticmethod
    def square(s: int) -> "BoundingBox":
        return BoundingBox.rect(s, s)

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    def shift(self, dx: int, dy: int) -> "BoundingBox":
        return BoundingBox(
            left=self.left + dx,
            top=self.top + dy,
            right=self.right + dx,
            bottom=self.bottom + dy,
        )

    def normalize(self) -> "BoundingBox":
        """
        Returns a BoundingBox of the same size but with (0,0) as the upper left corner.
        """
        return BoundingBox(
            left=0,
            top=0,
            right=self.width,
            bottom=self.height,
        )

    def is_normalized(self) -> bool:
        return self.left == 0 and self.top == 0

    def __add__(self, other: "BoundingBox") -> "BoundingBox":
        return BoundingBox(
            left=min(self.left, other.left),
            top=min(self.top, other.top),
            right=max(self.right, other.right),
            bottom=max(self.bottom, other.bottom),
        )

    @property
    def corners(self) -> list[tuple[int, int]]:
        return [(self.left, self.top), (self.right, self.bottom)]


class Component:
    def __init__(self, pos: "Position"):
        self.pos = pos
        self._x_pos_calculated = None
        self._y_pos_calculated = None

    @cached_property
    def content_bbox(self) -> BoundingBox:
        """Returns the bounding box of the content of this component, as a tuple of (left, top, right, bottom)"""
        raise NotImplementedError("Subclasses must implement content_bbox()")

    def draw(self, draw: ImageDraw.ImageDraw) -> None:
        """Draws this component onto the given ImageDraw object"""
        raise NotImplementedError("Subclasses must implement draw()")

    @cached_property
    def x_pos(self) -> int:
        match self.pos.x:
            case int():
                return self.pos.x
            case AlignedWith(other=other):
                return other.x_pos
            case LeftOf(other=other, padding=padding):
                return other.x_pos - self.width - padding
            case RightOf(other=other, padding=padding):
                return other.x_pos + other.width + padding
            case CenteredOn(other=Component() as other):
                return other.x_pos + (other.width - self.width) // 2
            case CenteredOn(other=int() as x):
                return x + (-self.width // 2)
            case RightAlignedWith(other=int() as right):
                return right - self.width
            case RightAlignedWith(other=Component() as other):
                return other.x_pos + other.width - self.width
            case RightAlignedWith(other=int() as right):
                return right - self.width
            case MatchAlignedWith(other=other):
                match other.pos.x:
                    case RightAlignedWith():
                        return other.x_pos + other.width - self.width
                    case _:
                        return other.x_pos
            case _:
                raise ValueError(f"Unsupported PositionType for x: {self.pos.x}")

    @cached_property
    def y_pos(self) -> int:
        match self.pos.y:
            case int():
                return self.pos.y
            case AlignedWith(other=other):
                return other.y_pos
            case Above(other=other, padding=padding):
                return other.y_pos - self.height - padding
            case Below(other=other, padding=padding):
                return other.y_pos + other.height + padding
            case CenteredOn(other=Component() as other):
                return other.y_pos + (other.height - self.height) // 2
            case CenteredOn(other=int() as y):
                return y + (-self.height // 2)
            case BottomAlignedWith(other=Component() as other):
                return other.y_pos + other.height - self.height
            case BottomAlignedWith(other=int() as bottom):
                return bottom - self.height
            case MatchAlignedWith(other=other):
                match other.pos.y:
                    case BottomAlignedWith():
                        return other.y_pos + other.height - self.height
                    case _:
                        return other.y_pos
            case _:
                raise ValueError(f"Unsupported PositionType for y: {self.pos.y}")

    @property
    def width(self) -> int:
        return self.content_bbox.width

    @property
    def height(self) -> int:
        return self.content_bbox.height

    @property
    def position(self) -> tuple[int, int]:
        return (self.x_pos, self.y_pos)

    @property
    def bbox(self) -> BoundingBox:
        bb = self.content_bbox
        x, y = self.position
        return bb.shift(x, y)


@dataclass
class AlignedWith:
    other: Component


@dataclass
class Below:
    other: Component
    padding: int = 0


@dataclass
class Above:
    other: Component
    padding: int = 0


@dataclass
class LeftOf:
    other: Component
    padding: int = 0


@dataclass
class RightOf:
    other: Component
    padding: int = 0


@dataclass
class CenteredOn:
    other: Component | int


@dataclass
class RightAlignedWith:
    other: Component | int


@dataclass
class BottomAlignedWith:
    other: Component | int


@dataclass
class MatchAlignedWith:
    other: Component


type XPosition = (
    int
    | AlignedWith
    | LeftOf
    | RightOf
    | CenteredOn
    | RightAlignedWith
    | MatchAlignedWith
)
type YPosition = (
    int
    | AlignedWith
    | Above
    | Below
    | CenteredOn
    | BottomAlignedWith
    | MatchAlignedWith
)


@dataclass
class Position:
    x: XPosition
    y: YPosition

    @staticmethod
    def centered_on(other: tuple[int, int] | Component) -> "Position":
        match other:
            case Component():
                return Position(x=CenteredOn(other), y=CenteredOn(other))
            case (x, y):
                return Position(x=CenteredOn(x), y=CenteredOn(y))


class CompositeComponent(Component):
    def __init__(self, children: Sequence[Component], pos: Position):
        super().__init__(pos)
        self.children = children

    @cached_property
    @override
    def content_bbox(self) -> BoundingBox:
        ret = None
        for child in self.children:
            child_bbox = child.bbox
            if ret is None:
                ret = child_bbox
            else:
                ret += child_bbox
        if ret is None:
            return BoundingBox(0, 0, 0, 0)
        return ret.normalize()

    @override
    def draw(self, draw: ImageDraw.ImageDraw):
        for child in self.children:
            child.draw(draw)
