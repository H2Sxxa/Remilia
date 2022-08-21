# Install

```shell
pip install Remilia
```

# Quick start

## LiteLog

```python
import Remilia

Logger=Remilia.LiteLog.LiteLog(__name__)

Logger.info("hello")

>>>[ INFO | __main__ | 14:58:50 ] hello
```

## LiteEvent

```python
import Remilia

EventBus=Remilia.LiteEvent.Event()

@EventBus.registEvent("hello")
def hello():
    print("hello")

@EventBus.registEventTrigger("hello",EventBus.PreEvent)
def beforehello(event):
    print(f"before the {event.__code__.co_name}")
    
@EventBus.registEventTrigger("hello",EventBus.AftEvent)
def beforehello(event):
    print(f"after the {event.__code__.co_name}")

hello()

>>>before the hello
>>>hello
>>>after the hello
```