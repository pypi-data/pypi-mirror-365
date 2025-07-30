from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle as PltRect, Patch

from ._shape import Shape
from FDLib.types import *

__all__ = ["Rectangle"]


class Rectangle(Shape):
    def __init__(
            self, *, location: T_Point, width: T_Number, height: T_Number,
            metalLayer: str, **kwargs  # pins: List[str], pins_location, vias, net
    ):
        assert width > 0, "width must be > 0"
        assert height > 0, "height must be > 0"
        super().__init__(metalLayer, **kwargs)
        self.location = location
        self.width = width
        self.height = height

    def draw_body(self, axes: plt.Axes, outer: Patch = None, is_hole: bool = False) -> Patch:
        patch = PltRect(
            self.location,
            self.width,
            self.height,
            linewidth=0,
            alpha=self._get_alpha(is_hole),
            color=self._get_color(is_hole)
        )
        axes.add_patch(patch)
        if outer is not None:
            patch.set_clip_path(outer)
        return patch
