from ..base.events import EventBase as __EventBase
from ..base.events import SubcribeEvent,WithPriority,TriggerEvent,EventFunction,EventInstance,EventSet


__all__ = [
    "SubcribeEvent",
    "WithPriority",
    "TriggerEvent",
    "EventFunction",
    "EventInstance",
    "EventSet"
]

class BaseEvent(__EventBase):pass