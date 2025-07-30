import matplotlib.pyplot as plt

from .base import FDBase
from FDLib.lib._shape import Shape  # noqa

__all__ = ["FDLibrary"]


class FDLibrary(FDBase):
    def __init__(self):
        self.specifications: list[Shape] = []

    def __repr__(self):
        inner = [repr(one) for one in self.specifications]
        children = "\n\n".join(inner)
        return f"<FDLibrary:\n{children}\n>"

    def show(self):
        fig, axes = plt.subplots()
        axes.set_title(self.__class__.__name__)
        for one in self.specifications:
            one.draw_body(axes)
            one.draw_pins(axes)
            one.draw_net(axes)
        axes.relim()
        axes.autoscale_view()
        axes.set_aspect("equal")
        plt.show()
