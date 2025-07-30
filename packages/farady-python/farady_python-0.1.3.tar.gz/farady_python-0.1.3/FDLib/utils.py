import hashlib

__all__ = ["Config", "get_color", "color_maker"]


class Config:
    PinSize: float = 5.0
    PinEdge: str = "black"
    PinFace: str = "red"
    Alpha: float = 0.5


def get_color(s: str) -> str:
    digest = hashlib.md5(s.encode()).hexdigest()
    return f"#{digest[:6]}"


def color_maker():
    colors = {}

    def inner(s: str) -> str:
        if s not in colors:
            colors[s] = get_color(s)
        return colors[s]

    return inner
