from ..base.events import EventBase as __EventBase
from ..base.events import SubcribeEvent,WithPriority,TriggerEvent,EventFunction,IHasInstance


__all__ = [
    "SubcribeEvent",
    "WithPriority",
    "TriggerEvent",
    "EventFunction",
    "IHasInstance"
]

class BaseEvent(__EventBase,IHasInstance):
    @staticmethod
    def instance():
        return LibEvents.BaseEvent
    
class LibEvents:
    BaseEvent=BaseEvent()