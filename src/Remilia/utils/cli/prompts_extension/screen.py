from abc import abstractmethod, ABC
from typing import Self


class ScreenBase(ABC):
    parent: Self

    def __init__(self) -> None:
        super().__init__()
        self.parent = None

    def setParent(self, parent: Self) -> Self:
        self.parent = parent
        return self

    def backto(self) -> None:
        if self.parent is not None:
            self.parent.build()

    @abstractmethod
    def build(self):
        """
        draw your screen here
        """
