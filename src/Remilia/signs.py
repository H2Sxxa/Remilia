from inspect import Parameter, _empty, signature
from typing import Callable


class Signs:
    @staticmethod    
    def getParasAsType(call:Callable):
        return [signarg.annotation for _,signarg in signature(call).parameters.items()]