from ..base.events import EventBase as __EventBase
from ..base.events import SubcribeEvent,WithPriority,TriggerEvent


__all__ = [
    "SubcribeEvent",
    "WithPriority",
    "TriggerEvent"
]

class BaseEvent(__EventBase):
    @staticmethod
    def instance():
        return LibEvents.BaseEvent
    
class LibEvents:
    BaseEvent=BaseEvent()