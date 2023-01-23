
from abc import ABC, abstractmethod
from types import FunctionType
from typing import List
from inspect import signature,_empty
class EventBase(ABC):
    def __init__(self) -> None:
        self.__block=False
    
    @property
    def cancelable(self):
        return True
    
    def cancel(self):
        if self.cancelable:
            self.__block=True
        else:
            raise CancelError("uncancelable event %s" % self.__class__.__name__)

    @abstractmethod
    def instance() -> "EventBase":
        return None

    def call_event(self,func:FunctionType):
        self.Data.Calls=sorted(self.Data.Calls,key=lambda x: getPriority(x))
        for sub in self.Data.Calls:
            executesub(sub)
            if self.__block:
                self.__block=False
                return False
        return True
    
    class Data:
        Calls:List[FunctionType]=[]

class CancelError(Exception):pass

def getPriority(func:FunctionType):
        return 0 if "__event_priority__" not in dir(func) else getattr(func,"__event_priority__")

def TriggerEvent(event:"EventBase"):
    def EventTrigger(func):
        def execute(*args,**kwargs):
            if event.call_event(func):
                return func(*args,**kwargs)
        return execute
    return EventTrigger

def SubcribeEvent(func:FunctionType):
    func.__event_priority__=0
    loadinto(func)
    
def WithPriority(priority:int=0):
    def SubcribeEvent(func:FunctionType):
        func.__event_priority__=priority
        loadinto(func)
    return SubcribeEvent

def loadinto(func:FunctionType):
    for _,signarg in signature(func).parameters.items():
        if issubclass(signarg.annotation,EventBase):
            signarg.annotation.instance().Data.Calls.append(func)
            return

def executesub(func:FunctionType):
    paras={}
    for _,signarg in signature(func).parameters.items():
        if issubclass(signarg.annotation,EventBase):
            paras.update({signarg.name:signarg.annotation.instance()})
        elif signarg.default != _empty:
            paras.update({signarg.name:signarg.default})
        else:
            paras.update({signarg.name:None})
    func(**paras)