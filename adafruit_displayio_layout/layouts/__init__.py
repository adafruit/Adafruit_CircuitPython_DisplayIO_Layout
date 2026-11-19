# SPDX-FileCopyrightText: 2025 Shubham Patel
#
# SPDX-License-Identifier: MIT

from micropython import const

try:
    from typing import Tuple
except ImportError:
    pass

# Anchor point constants for anchor method.
ANCHOR_TOP_LEFT = const((0.0, 0.0))
ANCHOR_TOP_CENTER = const((0.5, 0.0))
ANCHOR_TOP_RIGHT = const((1.0, 0.0))
ANCHOR_CENTER_LEFT = const((0.0, 0.5))
ANCHOR_CENTER = const((0.5, 0.5))
ANCHOR_CENTER_RIGHT = const((1.0, 0.5))
ANCHOR_BOTTOM_LEFT = const((0.0, 1.0))
ANCHOR_BOTTOM_CENTER = const((0.5, 1.0))
ANCHOR_BOTTOM_RIGHT = const((1.0, 1.0))


def anchor(obj, anchor: Tuple[float, float], width: int, height: int) -> None:
    """Helper to position a display object on screen using a defined anchor point.

    Sets `anchor_point` and `anchored_position` for display elements such as `Label`,
    `Widget`, `AnchoredTileGrid`, or `AnchoredGroup`.

    :param obj: The object to be positioned. Must support `anchor_point` and `anchored_position`.
    :param anchor: One of the predefined anchor constants (e.g. ANCHOR_TOP_LEFT, ANCHOR_CENTER)
    :param width: Width of the display in pixels
    :param height: Height of the display in pixels
    """
    if not hasattr(obj, "anchor_point") or not hasattr(obj, "anchored_position"):
        raise AttributeError(
            "Object must have both `anchor_point` and `anchored_position` attributes."
        )

    if anchor not in {
        ANCHOR_TOP_LEFT,
        ANCHOR_TOP_CENTER,
        ANCHOR_TOP_RIGHT,
        ANCHOR_CENTER_LEFT,
        ANCHOR_CENTER,
        ANCHOR_CENTER_RIGHT,
        ANCHOR_BOTTOM_LEFT,
        ANCHOR_BOTTOM_CENTER,
        ANCHOR_BOTTOM_RIGHT,
    }:
        raise ValueError(
            "Anchor must be one of: ANCHOR_TOP_LEFT, ANCHOR_TOP_CENTER, ANCHOR_TOP_RIGHT,\n"
            "ANCHOR_CENTER_LEFT, ANCHOR_CENTER, ANCHOR_CENTER_RIGHT,\n"
            "ANCHOR_BOTTOM_LEFT, ANCHOR_BOTTOM_CENTER, ANCHOR_BOTTOM_RIGHT."
        )

    obj.anchor_point = anchor
    obj.anchored_position = (
        int(anchor[0] * width),
        int(anchor[1] * height),
    )
