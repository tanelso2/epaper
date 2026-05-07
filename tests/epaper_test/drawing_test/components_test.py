from typing import override

import pytest

from epaper.components.core import Component
from epaper.components.debugging import FailingComponent
from epaper.drawing.components import ImagePlanner


class FailingImagePlanner(ImagePlanner):
    @override
    def create_components(self) -> dict[str, Component]:
        return {"im_a_failure": FailingComponent(raise_on_construct=True)}


@pytest.fixture
def fail_to_generate_planner() -> ImagePlanner:
    return FailingImagePlanner(width=0, height=0, draw_outlines=False)


def test_failing_to_generate_components_still_creates_image_with_error_message(
    fail_to_generate_planner: ImagePlanner,
):
    img = fail_to_generate_planner.generate()
    assert img is not None
    curr_components = fail_to_generate_planner._curr_components
    assert len(curr_components) == 1
    assert "error" in curr_components
    assert "im_a_failure" not in curr_components
