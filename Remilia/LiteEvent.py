class EventType:
    def __init__(self,name) -> None:
        self.cancel=False
        self.name=name
        self.obj=None
        self.result=None
    def setCancel(self,isCancel:bool=True):
        self.cancel=isCancel
    
    def getName(self):
        return self.name
    
    def setResult(self,result):
        self.result=result
        
    def getResult(self):
        return self.result
    
    def setOBJ(self,obj):
        self.obj=obj
        
    def getOBJ(self):
        return self.obj
    
class EventBus:
    def __init__(self) -> None:
        self.EventList=[]
        self.PreEvent={}
        self.AftEvent={}
        
    def registEvent(self,event:EventType):
        '''
        register the function/others as a event
        '''
        event_name=event.getName()
        if event_name not in self.EventList:
            self.EventList.append(event_name)
            self.PreEvent.update({event_name:[]})
            self.AftEvent.update({event_name:[]})
        def outter(func):
            event.setOBJ(func)
            def warpper(*args,**kwargs):
                self.EventPreCheck(event_name,event)
                if event.cancel:
                    result=None
                else:
                    result=func(*args,**kwargs)
                    self.EventAfterCheck(event_name,event)
                if event.cancel:
                    event.setCancel(False)
                event.setResult(result)
                return result
            return warpper
        return outter
    
    def registEventTrigger(self,event_name,point:dict,AutoaddEvent=False):
        '''
        bind it to your event which has registed\n
        point:\n
         - EventBus.PreEvent 
         - EventBus.AftEvent 
        '''
        def outter(func):
            try:
                point[event_name].append(func)
            except KeyError as e:
                if AutoaddEvent:
                    if point == self.PreEvent:
                        self.PreEvent.update({event_name:[func]})
                        self.AftEvent.update({event_name:[]})
                    elif point == self.AftEvent:
                        self.PreEvent.update({event_name:[]})
                        self.AftEvent.update({event_name:[func]})
                    self.EventList.append(event_name)
                else:
                    print(KeyError.__name__+":",e,"is not in event list")
        return outter
    
    def EventPreCheck(self,name,eventType:EventType):
        for event in self.PreEvent[name]:
            event(eventType)
                
    def EventAfterCheck(self,name,eventType):
        for event in self.AftEvent[name]:
            event(eventType)