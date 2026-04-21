from functools import cached_property
from typing import override

from epaper.components.core import (
    BottomAligned,
    Component,
    CompositeComponent,
    Position,
    BoundingBox,
    AlignedWith,
    Below,
    Above,
    LeftOf,
    RightOf,
    CenteredOn,
    RightAligned,
)


class FixedSizeComponent(Component):
    def __init__(self, width: int, height: int, pos: Position):
        super().__init__(pos)
        self._width = width
        self._height = height

    @cached_property
    @override
    def content_bbox(self) -> BoundingBox:
        return BoundingBox(left=0, top=0, right=self._width, bottom=self._height)


def test_fixed_size_component():
    c = FixedSizeComponent(100, 50, Position(x=10, y=20))
    assert c.content_bbox == BoundingBox(left=0, top=0, right=100, bottom=50)


def test_static_position():
    c = FixedSizeComponent(100, 50, Position(x=10, y=20))
    assert c.position == (10, 20)
    assert c.bbox == BoundingBox(left=10, top=20, right=110, bottom=70)


def test_below():
    c1 = FixedSizeComponent(100, 50, Position(x=10, y=20))
    c2 = FixedSizeComponent(80, 40, Position(x=AlignedWith(c1), y=Below(c1)))
    assert c2.position == (10, 70)
    c3 = FixedSizeComponent(
        80, 40, Position(x=AlignedWith(c2), y=Below(c1, padding=10))
    )
    assert c3.position == (10, 80)


def test_above():
    c1 = FixedSizeComponent(100, 50, Position(x=200, y=300))
    c2 = FixedSizeComponent(80, 40, Position(x=AlignedWith(c1), y=Above(c1)))
    assert c2.position == (200, 260)
    c3 = FixedSizeComponent(
        80, 40, Position(x=AlignedWith(c2), y=Above(c1, padding=10))
    )
    assert c3.position == (200, 250)


def test_left_of():
    c1 = FixedSizeComponent(100, 50, Position(x=200, y=300))
    c2 = FixedSizeComponent(80, 40, Position(x=LeftOf(c1), y=AlignedWith(c1)))
    assert c2.position == (120, 300)
    c3 = FixedSizeComponent(
        80, 40, Position(x=LeftOf(c1, padding=10), y=AlignedWith(c1))
    )
    assert c3.position == (110, 300)


def test_right_of():
    c1 = FixedSizeComponent(100, 50, Position(x=200, y=300))
    c2 = FixedSizeComponent(80, 40, Position(x=RightOf(c1), y=AlignedWith(c1)))
    assert c2.position == (300, 300)
    c3 = FixedSizeComponent(
        80, 40, Position(x=RightOf(c1, padding=10), y=AlignedWith(c1))
    )
    assert c3.position == (310, 300)


def test_centered_on():
    c1 = FixedSizeComponent(100, 50, Position(x=200, y=300))
    c2 = FixedSizeComponent(80, 40, Position(x=CenteredOn(c1), y=CenteredOn(c1)))
    assert c2.position == (210, 305)


def test_right_aligned():
    c1 = FixedSizeComponent(100, 50, Position(x=200, y=300))
    c2 = FixedSizeComponent(80, 40, Position(x=RightAligned(300), y=AlignedWith(c1)))
    assert c2.position == (220, 300)


def test_bottom_aligned():
    c1 = FixedSizeComponent(100, 50, Position(x=200, y=300))
    c2 = FixedSizeComponent(80, 40, Position(x=AlignedWith(c1), y=BottomAligned(400)))
    assert c2.position == (200, 360)


class EasyCompositeComponent(CompositeComponent):
    def __init__(self, children):
        super().__init__(pos=children[0].pos, children=children)


def test_composite_component__content_bbox():
    base_pos = Position(x=200, y=300)
    c1 = FixedSizeComponent(100, 50, base_pos)
    c2 = FixedSizeComponent(80, 40, Position(x=RightOf(c1), y=AlignedWith(c1)))
    cc = EasyCompositeComponent(children=[c1, c2])
    expected = BoundingBox.rect(w=180, h=50)
    assert expected == cc.content_bbox
    c3 = FixedSizeComponent(20, 20, pos=Position.centered_on(c1))
    cc = EasyCompositeComponent(children=[c1, c3])
    expected = BoundingBox.rect(100, 50)
    assert expected == cc.content_bbox
