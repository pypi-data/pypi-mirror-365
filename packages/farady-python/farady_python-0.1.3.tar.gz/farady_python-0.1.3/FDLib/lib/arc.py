import math
from matplotlib.patches import Wedge, Patch
import matplotlib.pyplot as plt

from ._shape import Shape
from FDLib.types import *

__all__ = ["Arc"]

ArcTypeMap = {
    "butt": "butt", "round": "round", "square": "square"
}


class Arc(Shape):
    def __init__(
            self, *, location: T_Point, innerRadius: float, outerRadius: float,
            beginAngle: float, endAngle: float, clockwise: int = 1, arc_type: T_ArcType = "butt",
            metalLayer: str, **kwargs  # pins: List[str], pins_location, vias, net
    ):
        assert 0 < innerRadius < outerRadius
        assert arc_type.lower() in ArcTypeMap
        super().__init__(metalLayer, **kwargs)
        self.location = location
        self.innerRadius = innerRadius
        self.outerRadius = outerRadius
        self.beginAngle = (beginAngle * 180 / math.pi) % 360
        self.endAngle = (endAngle * 180 / math.pi) % 360
        self.clockwise = clockwise
        self.arc_type = ArcTypeMap[arc_type.lower()]

    def __repr__(self) -> "str":
        return (
            f"<Arc:\n"
            f"  location={self.location}, pins={self.pins}, pins_location={self.pins_location}\n"
            f"  metalLayer={self.metalLayer}, vias={self.vias}, net={self.net}\n"
            f"  innerRadius={self.innerRadius}, outerRadius={self.outerRadius}\n"
            f"  beginAngle={self.beginAngle}, endAngle={self.endAngle}\n"
            f"  clockwise={self.clockwise}, arc_type={self.arc_type}\n"
            f">"
        )

    def draw_body(self, axes: plt.Axes, outer: Patch = None, is_hole: bool = False) -> Patch:
        if self.clockwise:
            self.beginAngle, self.endAngle = self.endAngle, self.beginAngle
        width = self.outerRadius - self.innerRadius
        patch = Wedge(
            self.location,
            self.outerRadius,
            self.beginAngle,
            self.endAngle,
            width=width,
            linewidth=0,
            alpha=self._get_alpha(is_hole),
            color=self._get_color(is_hole)
        )
        axes.add_patch(patch)
        if outer is not None:
            patch.set_clip_path(outer)
        return patch
