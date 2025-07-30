import math

from FDLib import *


class V012(FDLibrary):
    def reload(self):
        self.specifications = [
            PolygonWithHole(
                polygon=Polygon(location=[(0, 0), (0, 100), (100, 100), (100, 0)], metalLayer="ploy-1"),
                polygonHoles=[
                    PolygonWithHole(
                        polygon=Rectangle(location=(5, 5), width=20, height=20, metalLayer="ploy-2"),
                        polygonHoles=[
                            Arc(
                                location=(10, 10),
                                innerRadius=5,
                                outerRadius=10,
                                beginAngle=0,
                                endAngle=math.pi / 3 * 2.5,
                                clockwise=0,
                                metalLayer="Arc"
                            )
                        ],
                        metalLayer="inner-PolygonWithHole"
                    ),
                    Polygon(location=[(5, 95), (20, 95), (10, 80)], metalLayer="ploy-3"),
                    Rectangle(location=(70, 70), width=25, height=25, metalLayer="rectangle"),
                    Path(
                        location=[(60, 30), (70, 15), (80, 30), (90, 15)],
                        width=10,
                        path_type="round",
                        corner_type="square",
                        metalLayer="path"
                    )
                ],
                metalLayer="outer-PolygonWithHole"
            )
        ]


if __name__ == "__main__":
    # from FDLib.utils import Config
    #
    # Config.Alpha = 0.1
    V012().run()
