from unittest import result
from . import LiteUtils,LiteMixin
class Event:
    def __init__(self) -> None:
        self.EventList=[]
        self.PreEvent={}
        self.AftEvent={}
        
    def registEvent(self,event_name):
        if event_name not in self.EventList:
            self.EventList.append(event_name)
            self.PreEvent.update({event_name:[]})
            self.AftEvent.update({event_name:[]})
        def outter(func):
            def warpper(*args,**kwargs):
                self.EventPreCheck(event_name,func)
                result=func(*args,**kwargs)
                self.EventAfterCheck(event_name,func)
                return result
            return warpper
        return outter
    
    def registEventTrigger(self,event_name,point:dict,AutoaddEvent=False):
        def outter(func):
            try:
                point[event_name].append(func)
            except KeyError as e:
                if AutoaddEvent:
                    if point == self.PreEvent:
                        self.PreEvent.update({event_name:[func]})
                    elif point == self.AftEvent:
                        self.AftEvent.update({event_name:[func]})
                    self.EventList.append(event_name)
                else:
                    print(KeyError.__name__+":",e,"is not in event list")
        return outter
    
    def EventPreCheck(self,name,event_func):
        for event in self.PreEvent[name]:
            event(event_func)
            
    def EventAfterCheck(self,name,event_func):
        for event in self.AftEvent[name]:
            event(event_func)