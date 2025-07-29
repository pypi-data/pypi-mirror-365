import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from ._shape import Shape
from FDLib.types import *

__all__ = ["PolygonWithHole"]


class PolygonWithHole(Shape):  # TODO，确认是不是需要接收kwargs这些参数
    def __init__(
            self, *, polygon: Shape, polygonHoles: List[Shape],  # TODO，确认polygon是不是可以为任意形状，polygonHoles可不可以递归
            metalLayer: str, **kwargs  # pins: List[str], pins_location, vias, net
    ):
        super().__init__(metalLayer, **kwargs)
        self.polygon = polygon
        self.holes = polygonHoles

    def __repr__(self) -> "str":
        return (
            f"<PolygonWithHole:\n"
            f"  pins={self.pins}, pins_location={self.pins_location}\n"
            f"  metalLayer={self.metalLayer}, vias={self.vias}, net={self.net}\n"
            f"  polygon={self.polygon}\n"
            f"  holes: {self.holes}\n"
            f">"
        )

    def draw_body(self, axes: plt.Axes, outer: Patch = None, is_hole: bool = False) -> Patch:
        patch = self.polygon.draw_body(axes, outer, is_hole)
        for hole in self.holes:
            hole.draw_body(axes, patch, not is_hole)
        if outer is not None:
            patch.set_clip_path(outer)
        return patch
