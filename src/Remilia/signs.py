from inspect import signature
from typing import Callable, List, Type


class Signs:
    @staticmethod
    def getParasAsType(call: Callable):
        return [signarg.annotation for _, signarg in signature(call).parameters.items()]

    @staticmethod
    def check_eq(paraa: List[Type], parab: List[Type]) -> bool:
        if len(paraa) != len(parab):
            return False
        else:
            for a, b in zip(paraa, parab):
                if a != b:
                    return False
            return True
