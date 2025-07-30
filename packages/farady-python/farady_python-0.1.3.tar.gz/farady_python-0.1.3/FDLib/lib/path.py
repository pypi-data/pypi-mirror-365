from matplotlib import pyplot as plt
from matplotlib.path import Path as PltPath
from matplotlib.patches import PathPatch, Patch

from ._shape import Shape
from FDLib.types import *

__all__ = ["Path"]

PathTypeMap = {
    "butt": "miter", "round": "round", "square": "bevel"
}
CornerTypeMap = {
    "butt": "butt", "round": "round", "square": "projecting"
}


class Path(Shape):
    def __init__(
            self, *, location: T_Points, width: float,
            path_type: T_PathType = "round",
            corner_type: T_CornerType = "butt",
            metalLayer: str, **kwargs  # pins: List[str], pins_location, vias, net
    ):
        assert path_type.lower() in PathTypeMap
        assert corner_type.lower() in CornerTypeMap
        super().__init__(metalLayer, **kwargs)
        self.location = location
        self.width = width
        self.path_type = PathTypeMap[path_type.lower()]
        self.corner_type = CornerTypeMap[corner_type.lower()]

    def __repr__(self) -> "str":
        return (
            f"<Path:\n"
            f"  pins={self.pins}, pins_location={self.pins_location}\n"
            f"  metalLayer={self.metalLayer}, vias={self.vias}, net={self.net}\n"
            f"  width={self.width}, path_type={self.path_type}, corner_type={self.corner_type}\n"
            f"  location={self.location}\n"
            f">"
        )

    def draw_body(self, axes: plt.Axes, outer: Patch = None, is_hole: bool = False) -> Patch:
        codes = [PltPath.MOVETO] + [PltPath.LINETO] * (len(self.location) - 1)
        path = PltPath(self.location, codes)
        patch = PathPatch(
            path,
            fill=False,
            linewidth=self.width,
            joinstyle=self.path_type,
            capstyle=self.corner_type,
            alpha=self._get_alpha(is_hole),
            color=self._get_color(is_hole)
        )
        axes.add_patch(patch)
        if outer is not None:
            patch.set_clip_path(outer)
        return patch
