"""Class representing a vector of hexgrid coordinates."""
from typing import Optional, Union


class Vector:

    def __init__(self, q: Union[float, int], r: Union[float, int], s: Optional[Union[float, int]] = None, /) -> None:
        """Class constructor."""
        if s is None:
            self.s = -q - r
        else:
            if q + r + s != 0:
                raise ValueError("Any Hex's cube coordinates must sum to 0.")
            self.s = s
        self.q = q
        self.r = r

    def __str__(self):
        return f"q: {self.q}, r: {self.r}, s: {self.s}"

    def __repr__(self):
        return f"{self.q}, {self.r}, {self.s}"

    def __hash__(self):
        return hash((self.q, self.r, self.s))

    def __eq__(self, other):
        """Implement equality."""
        if isinstance(other, Vector):
            return self.q == other.q and self.r == other.r and self.s == other.s
        else:
            raise ValueError("Comparison between Hexes and non-Hexes "
                             f"is not supported, other was : {other}")

    def __add__(self, other):
        """Implement addition."""
        if isinstance(other, Vector):
            return Vector(self.q + other.q, self.r + other.r, self.s + other.s)
        else:
            raise ValueError("Addition between Hexes and non-Hexes "
                             f"is not supported, other was : {other}")

    def __sub__(self, other):
        """Implement subtraction"""
        if isinstance(other, Vector):
            return Vector(self.q - other.q, self.r - other.r, self.s - other.s)
        else:
            raise ValueError("Subtraction between Hexes and "
                             f"non-Hexes is not supported, other was : {other}")

    def __mul__(self, factor: Union[float, int]):
        """Implement multiplication."""
        if isinstance(factor, float) or isinstance(factor, int):
            return Vector(self.q * factor, self.r * factor, self.s * factor)
        else:
            raise ValueError("Multiplication is only supported between Vector "
                             f"and int or float, other was : {factor}")

    def __truediv__(self, factor: int):
        """Implement division."""
        return Vector(self.q / factor, self.r / factor, self.s / factor)

    def __and__(self, other):
        """Implement logical 'and'."""
        if isinstance(other, Vector):
            return (self.q or self.r or self.s) and (other.q or other.r or other.s)
        else:
            raise ValueError("'and' operation between Vector and "
                             f"non-Vector is not supported, other was : {other}")

    def __or__(self, other):
        """Implement logical 'or'."""
        if isinstance(other, Vector):
            return (self.q or self.r or self.s) or (other.q or other.r or other.s)
        else:
            raise ValueError("'or' operation between Hexes and "
                             f"non-Hexes is not supported, other was : {other}")

    def __xor__(self, other):
        """Implement logical 'xor'."""
        if isinstance(other, Vector):
            return bool(self.q or self.r or self.s) ^ bool(other.q or other.r or other.s)
        else:
            raise ValueError("'xor' operation between Hexes and "
                             f"non-Hexes is not supported, other was : {other}")

    def __neg__(self):
        """Implement negation by returning additive inverse."""
        return Vector(-self.q, -self.r, -self.s)

    def __pos__(self):
        """Implement unary plus operator by returning a new value."""
        return Vector(self.q, self.r, self.s)

    def __abs__(self):
        """Implement 'abs()'."""
        return abs(self.q), abs(self.r), abs(self.s)

    def __matmul__(self, other: "Vector") -> float:
        """Implement dot product `@`."""
        return (self.q*other.q + self.r*other.r + self.s*other.s)/2
