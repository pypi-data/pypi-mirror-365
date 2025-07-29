from matplotlib.axes import Axes
from matplotlib.patches import Rectangle, Patch

from FDLib.types import *
from FDLib.utils import Config, get_color

__all__ = ["Shape"]


class Shape:
    def __init__(
            self,
            metalLayer: str,
            pins: List[str] = None,
            pins_location: List[T_Points] = None,
            vias: List[str] = None,
            net: str = ""
    ):
        pins = pins or []
        pins_location = pins_location or []
        vias = vias or []

        self.metalLayer = metalLayer
        self.pins = pins
        self.pins_location = pins_location
        self.vias = vias
        self.net = net

    @staticmethod
    def _get_alpha(is_hole: bool) -> float:
        return 1.0 if is_hole else Config.Alpha

    def _get_color(self, is_hole: bool) -> str:
        return "white" if is_hole else get_color(self.metalLayer)

    def draw_body(self, axes: Axes, outer: Patch = None, is_hole: bool = False) -> Patch:
        raise NotImplementedError

    def draw_pins(self, axes: Axes):
        for locations in self.pins_location:
            for location in locations:
                x, y = location[0] - Config.PinSize / 2, location[1] - Config.PinSize / 2
                patch = Rectangle(
                    (x, y), Config.PinSize, Config.PinSize, angle=45, rotation_point="center",
                    fill=True, facecolor=Config.PinFace, edgecolor=Config.PinEdge, alpha=Config.Alpha
                )
                axes.add_patch(patch)

    def draw_net(self, axes: Axes):
        pass
