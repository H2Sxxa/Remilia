from typing import Generic, TypeVar
from inspect import _empty

RT = TypeVar("RT")  # Return Type
T = TypeVar("T")

NT = TypeVar("NT")  # the first arg of a pair
VT = TypeVar("VT")  # the second arg of a pair


class PairType(Generic[NT, VT]):
    ...

Empty = _empty
