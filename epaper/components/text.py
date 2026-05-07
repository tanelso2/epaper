from functools import cached_property
from typing import Literal, override

from epaper.components.core import (
    Component,
    CompositeComponent,
    Position,
    BoundingBox,
    LeftOf,
    RightOf,
    CenteredOn,
)


class TextComponent(Component):
    def __init__(self, text: str, font, pos: Position):
        super().__init__(pos)
        self.text = text
        self.font = font

    @cached_property
    @override
    def content_bbox(self) -> BoundingBox:
        (left, top, right, bottom) = self.font.getbbox(self.text)
        return BoundingBox(left=left, top=top, right=right, bottom=bottom)

    @override
    def draw(self, draw):
        draw.text(self.position, self.text, font=self.font)


type LabelPos = Literal["left"] | Literal["right"]


class LabeledValueComponent(CompositeComponent):
    def __init__(
        self,
        value: str,
        label: str,
        value_font,
        label_font,
        value_pos: Position,
        label_pos: LabelPos = "left",
        padding: int = 10,
    ):
        val_component = TextComponent(value, font=value_font, pos=value_pos)
        if label_pos == "left":
            label_x_pos = LeftOf(val_component, padding=padding)
        else:
            label_x_pos = RightOf(val_component, padding=padding)
        label_component = TextComponent(
            label,
            font=label_font,
            pos=Position(x=label_x_pos, y=CenteredOn(val_component)),
        )
        children = [val_component, label_component]
        super().__init__(children, pos=value_pos)
