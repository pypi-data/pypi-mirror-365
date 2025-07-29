from typing import List, Tuple, Literal, Union

__all__ = [
    "List", "Tuple", "Literal", "Union",
    "T_Number", "T_Point", "T_Points",
    "T_PathType", "T_CornerType", "T_ArcType"
]
T_Number = Union[int, float]
T_Point = Tuple[T_Number, T_Number]
T_Points = List[T_Point]

T_PathType = Literal["miter", "round", "bevel", "butt", "square"]  # TODO: 确认到底是哪些
T_CornerType = Literal["butt", "round", "projecting", "square"]  # TODO: 确认到底是哪些
T_ArcType = Literal["butt", "round", "square"]  # TODO: 确认到底是哪些
