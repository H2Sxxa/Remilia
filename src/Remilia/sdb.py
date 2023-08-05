from abc import ABC
from typing_extensions import Self

from .fancy import hasInstance


@hasInstance
class DataStructBase(ABC):
    instance:Self

    @property
    def empty():
        pass


class DataBase:
    pass
