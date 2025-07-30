from matplotlib.patches import Polygon as PltPloy, Patch
import matplotlib.pyplot as plt

from ._shape import Shape
from FDLib.types import *

__all__ = ["Polygon"]


class Polygon(Shape):
    def __init__(
            self, *, location: T_Points,
            metalLayer: str, **kwargs  # pins: List[str], pins_location, vias, net
    ):
        super().__init__(metalLayer, **kwargs)
        assert len(location), "location is required"
        self.location = location

    def __repr__(self) -> "str":
        return (
            f"<Polygon:\n"
            f"  pins={self.pins}, pins_location={self.pins_location}\n"
            f"  metalLayer={self.metalLayer}, vias={self.vias}, net={self.net}\n"
            f"  location={self.location}\n"
            f">"
        )

    def draw_body(self, axes: plt.Axes, outer: Patch = None, is_hole: bool = False) -> Patch:
        patch = PltPloy(
            self.location,
            linewidth=0,
            fill=True,
            alpha=self._get_alpha(is_hole),
            color=self._get_color(is_hole)
        )
        axes.add_patch(patch)
        if outer is not None:
            patch.set_clip_path(outer)
        return patch
