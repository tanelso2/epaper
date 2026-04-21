import math

from PIL import ImageDraw

import epaper.drawing.colors as colors
from epaper.utils.angles import add_degrees, invert_y


def draw_arrow(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    direction_degs: float,
    r: float = 1.0,
    arm_length: float = 0.33,
    arm_angle_degs: float = 30.0,
    line_width: int = 3,
):
    c_x, c_y = center

    # Adjust the angle for the coordinate system of drawing (positive y is down)
    direction_degs = invert_y(direction_degs)
    dir_rads = math.radians(direction_degs)
    head_x = c_x + (r * math.cos(dir_rads))
    head_y = c_y + (r * math.sin(dir_rads))
    head = (head_x, head_y)

    opposite_degs = add_degrees(direction_degs, 180)
    opposite_rads = math.radians(opposite_degs)
    tail_x = c_x + (r * math.cos(opposite_rads))
    tail_y = c_y + (r * math.sin(opposite_rads))
    tail = (tail_x, tail_y)

    draw.line([head, tail], width=line_width)

    arm1_degs = add_degrees(opposite_degs, arm_angle_degs)
    arm1_rads = math.radians(arm1_degs)
    arm2_degs = add_degrees(opposite_degs, -arm_angle_degs)
    arm2_rads = math.radians(arm2_degs)

    arm1_x = head_x + (arm_length * math.cos(arm1_rads))
    arm1_y = head_y + (arm_length * math.sin(arm1_rads))
    arm1 = (arm1_x, arm1_y)

    arm2_x = head_x + (arm_length * math.cos(arm2_rads))
    arm2_y = head_y + (arm_length * math.sin(arm2_rads))
    arm2 = (arm2_x, arm2_y)

    draw.polygon([head, arm1, arm2], fill=colors.BLACK, width=line_width)
