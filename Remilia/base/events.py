
from abc import ABC
from types import FunctionType
from typing import List
from inspect import signature,_empty

class CancelError(Exception):pass
class EventFunction:pass
class EventSet:
    etype:"EventBase"
    einstance:"EventInstance"
    efunction:"EventFunction"
    def __init__(self,etype,einstance,efunction) -> None:
        self.etype=etype
        self.einstance=einstance
        self.efunction=efunction

class EventBase(ABC):    
    @property
    def cancelable():
        return True
    
    def instance(event:"EventBase",*args,**kwargs) -> "EventInstance":
        return EventInstance(event).withProperty(*args,**kwargs)
    
    class __Data:Calls:List[callable]=[]
    
    @staticmethod
    def getData(event:"EventBase"):
        return event.__Data
    
    @staticmethod        
    def call_event(event:"EventBase",func:FunctionType):
        eventins=event.instance(event)
        for sub in sorted(event.__Data.Calls,key=lambda x: getPriority(x)):
            executesub(sub,func,eventins,event)
            if eventins.isBlock():
                return False
        return True
class EventInstance:
    def __init__(self,event:EventBase) -> None:
        self.args=[]
        self.block=False
        self.event=event
        
    def cancel(self):
        if self.event.cancelable:
            self.block=True
        else:
            raise CancelError("uncancelable event %s" % self.__class__.__name__)
        return self
    
    def isBlock(self):
        return self.block
    
    def withProperty(self,*args,**kwargs):
        self.args.extend(args)
        self.addProperty(**kwargs)
        return self

    def addProperty(self,**kwargs):
        for n,v in kwargs:
            setattr(self,n,v)
        return self

def getPriority(func:FunctionType):
        return 0 if "__event_priority__" not in dir(func) else getattr(func,"__event_priority__")

def TriggerEvent(event:EventBase):
    def EventTrigger(func):
        def execute(*args,**kwargs):
            if event.call_event(event,func):
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
            signarg.annotation.getData(signarg.annotation).Calls.append(func)
            return


def executesub(func:FunctionType,eventfunc:FunctionType,eventinstance:EventInstance,event:EventBase):
    paras={}
    for _,signarg in signature(func).parameters.items():
        if issubclass(signarg.annotation,EventBase):paras.update({signarg.name:signarg.annotation})
        elif issubclass(signarg.annotation,EventFunction):paras.update({signarg.name:eventfunc})
        elif issubclass(signarg.annotation,EventInstance):paras.update({signarg.name:eventinstance})
        elif issubclass(signarg.annotation,EventSet):paras.update({signarg.name:EventSet(etype=event,einstance=eventinstance,efunction=eventfunc)})
        elif signarg.default != _empty:paras.update({signarg.name:signarg.default})
        else:paras.update({signarg.name:None})
    func(**paras)