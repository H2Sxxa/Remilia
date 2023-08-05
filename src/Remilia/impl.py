from typing_extensions import Self
from Remilia.base.typings import NT, PairType, VT


class CommonPair(PairType):
    def __init__(self, name: NT, value: VT) -> None:
        self._name = name
        self._value = value

    def getname(self) -> NT:
        return self._name

    def getvalue(self) -> VT:
        return self._value

    @property
    def name(self) -> NT:
        return self.getname()

    @property
    def value(self) -> VT:
        return self.getvalue()

    @staticmethod
    def fromnv(name: NT, value: VT) -> Self:
        return CommonPair(name, value)
    