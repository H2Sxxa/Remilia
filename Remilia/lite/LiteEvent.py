from types import FunctionType
from ..base.Events import CancelError, EventBase, Pre, Post

class EventContainer:
    def __init__(self,EventBus,Event) -> None:
        self.EventBus=EventBus
        self.Event=Event
        self.result=None
        self.args=[]
        self.kwargs={}
    def setCancel(self,x:bool):
        if self.Event.Cancelable():
            self.EventBus.cache["cancel"][self.Event]=x
        else:
            raise CancelError("Event %s is uncancelable" % self.Event)
    
    def setResult(self,x):
        self.result=x
    
    def setArgs(self,args,kwargs):
        self.args=args
        self.kwargs=kwargs
    
class EventBus:
    def __init__(self) -> None:
        self.Events={}
        self.Triggers={}
        self.cache={
            "cancel":{},
        }
        
    def _regEvent(self,Event,x:FunctionType):
        self.Events.update({x:Event})
        self._addcache(Event)
        
    def callEvent(self,Event:EventBase,x,*args,**kwargs):
        conter:EventContainer=Event._build(EventBus=self,Event=Event)
        conter.setArgs(args,kwargs)
        temp=[t for t,event in self.Triggers.items() if event["event"] is Event and event["point"] is Pre]
        temp.sort(key=lambda x:self.Triggers[x]["level"],reverse=True)
        for t in temp:
            t(conter)
            if self.isCancel(Event):
                self.resetCache(Event)
                return
        result=x(*args,**kwargs)
        conter.setResult(result)
        temp=[t for t,event in self.Triggers.items() if event["event"] is Event and event["point"] is Post]
        temp.sort(key=lambda x:self.Triggers[x]["level"],reverse=True)
        for t in temp:
            t(conter)
        return result
    
    def EventHandle(self,Event:EventBase,level:int=10,Point=Pre):
        def outter(x:FunctionType):
            self.Triggers.update({x:{
                "event":Event,
                "level":level,
                "point":Point,
                }})
        return outter
    
    def resetCache(self,Event:EventBase) -> bool:
        self.cache["cancel"][Event]=False
        
    def isCancel(self,Event:EventBase) -> bool:
        return self.cache["cancel"][Event]
    
    def _addcache(self,Event:EventBase):
        self.cache["cancel"].update({Event:False})

class CommonEvent(EventBase):
    def call(self,EventBus:EventBus,Event,x,*args,**kwargs):
        super().call(super().__class__,EventBus,x,*args,**kwargs)
        EventBus.callEvent(Event,x,*args,**kwargs)

    def _build(EventBus,Event):
        return EventContainer(
            EventBus=EventBus,
            Event=Event,
                              )

def registEvent(Event:CommonEvent,EventBus:EventBus):
    def outter(x:FunctionType):
        EventBus._regEvent(Event,x)
        def inner(*args,**kwargs):
            result=Event().call(EventBus,Event,x,*args,**kwargs)
            return result
        return inner
    return outter