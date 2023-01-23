from ..base.events import EventBase,SubcribeEvent,WithPriority,TriggerEvent


class BaseEvent(EventBase):
    @staticmethod
    def instance():
        return LibEvents.BaseEvent
    
class LibEvents:
    BaseEvent=BaseEvent()