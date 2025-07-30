from typing import List, Tuple, Literal, Union

__all__ = [
    "List", "Tuple", "Literal", "Union",
    "T_Number", "T_Point", "T_Points",
    "T_PathType", "T_CornerType", "T_ArcType"
]
T_Number = Union[int, float]
T_Point = Tuple[T_Number, T_Number]
T_Points = List[T_Point]

T_PathType = Literal["butt", "round", "square"]
T_CornerType = Literal["butt", "round", "square"]
T_ArcType = Literal["butt", "round", "square"]
