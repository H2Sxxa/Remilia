![https://raw.githubusercontent.com/IAXRetailer/Remilia/main/background.png](https://raw.githubusercontent.com/IAXRetailer/Remilia/main/background.png "PID 100402267")

# Install

```shell
pip install Remilia
```

# Quick start

## LiteLog

```python
from Remilia.LiteLog import LiteLog

Logger=LiteLog(__name__)

Logger.info("hello")

>>>[ INFO | __main__ | 14:58:50 ] hello
```

## LiteEvent

```python
from Remilia.LiteEvent import EventType,EventBus
EventBus=EventBus()

@EventBus.registEvent(EventType("hello"))
def hello():
    print("hello")

@EventBus.registEventTrigger("hello",EventBus.PreEvent)
def beforehello(event:EventType):
    print(f"before the {event.getOBJ().__code__.co_name} event")
    #event.setCancel()
    #print("I cancel the event")
    
@EventBus.registEventTrigger("hello",EventBus.AftEvent)
def beforehello(event:EventType):
    print(f"after the {event.getOBJ().__code__.co_name} event")

hello()

>>>before the hello
>>>hello
>>>after the hello
```

## LiteThread

```python
from Remilia import LiteThread

def hello():
    return "hello"

TVManager=LiteThread.ThreadValueManager()
TestThread=LiteThread.LiteThread(target=hello)
TestThread.start()
print(TVManager.waitResult(TestThread))

>>>hello
```

## LiteMixin

```python
W.I.P
```