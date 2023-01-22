
from abc import ABC, abstractmethod

class EventBase(ABC):
    def Cancelable():
        return True
    
    def call(self,EventBus,Event,x,*args,**kwargs):
        pass
    
    @abstractmethod
    def _build():
        return any

class CancelError(Exception):pass
class Pre:pass
class Post:pass