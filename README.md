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

```

## LitePGL

```python
#main.py
#test
# - plugin.py

#main

from Remilia import LitePGL,LiteResource
PGLoader=LitePGL.PluginLoader()
LoadPoint1=LitePGL.PluginLoadPoint(PGLoader,"loadpoint1")
PGLoader.initLoadPlugin(LiteResource.Path("test/plugin.py"))
LoadPoint1.run()

#test\plugin.py

PluginLoader=self
@PluginLoader.registPlugin("loadpoint1")
class plugin(PluginType):
    def __init__(self) -> None:
        print(PluginLoader)
    
    def __reference__(self):
        return {
            ...
        }

>>><class 'Remilia.LitePGL.PluginLoader'>

```