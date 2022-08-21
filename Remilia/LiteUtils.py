from types import FunctionType
from . import DecoratorUtils

def asFunction(funclist):
    def runfunction(*args,**kwargs):
        for func in funclist:
            if func["args"]=="*args":
                func["args"]=args
            if func["kwargs"]=="**kwargs":
                func["kwargs"]=kwargs
            func["func"](*func["args"],**func["kwargs"])
    return runfunction