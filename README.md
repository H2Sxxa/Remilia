<div align=center>
  <img src="https://raw.githubusercontent.com/IAXRetailer/Remilia/main/background.png"  alt="[BG](https://raw.githubusercontent.com/IAXRetailer/Remilia/main/background.png)"/>
  <h1 align="center">Remilia</h1> 
</div>
<div align=center>
  <img src="https://img.shields.io/badge/python-3.8+-blue" alt="python">
  <img src="https://img.shields.io/github/languages/code-size/IAXRetailer/Remilia" alt="size">
  <img src="https://img.shields.io/github/license/IAXRetailer/Remilia" alt="license">
</div>

# Install

```shell
pip install Remilia
```

# Quick start

## LiteLog

```python
from Remilia.lite import LiteLog

logger=LiteLog.Logger(__name__)
logger.info(1,2,3)
logger.addPrintType("newprint")
logger.newprint(1,2,3)

>>>[ INFO | __main__ | 14:58:50 ] hello
```

## LiteEvent

```python
from Remilia.lite.LiteEvent import CommonEvent,EventBus,registEvent,EventContainer,Pre,Post

Bus1=EventBus()

@registEvent(CommonEvent,Bus1)
def run1():
    print("Event run now")

@Bus1.EventHandle(CommonEvent,Point=Pre)
def t1(Conter:EventContainer):
    print("Before the %s" % Conter.Event)

@Bus1.EventHandle(CommonEvent,Point=Post)
def t2(Conter:EventContainer):
    print("after the %s" % Conter.Event)

run1()

>>>Before the <class 'Remilia.LiteEvent.CommonEvent'>
>>>Event run now
>>>after the <class 'Remilia.LiteEvent.CommonEvent'>
```

## LiteThread

```python
from Remilia.lite import LiteThread

def hello():
    return "hello"

TVManager=LiteThread.ThreadValueManager()
TestThread=LiteThread.RewardThread(target=hello)
TestThread.start()
print(TVManager.waitResult(TestThread))

>>>hello
```

## LiteMixin

```python
from Remilia.lite import LiteMixin
class A:
    def __init__(self) -> None:
        self.hello()
    def hello(self):
        print("hello")
A()
class A_patch:
    def hello(self):
        print("byebye")

LiteMixin.MixInClass(A,A_patch)
A()


>>>hello
>>>byebye
```

## LitePGL

```python

# main.py
# test
#  - plugin1.py
#  - plugin2.py



#main

from Remilia.lite import LitePGL,LiteResource
PGLoader=LitePGL.PluginLoader()
LoadPoint1=LitePGL.PluginLoadPoint(PGLoader,"loadpoint1")
PGLoader.setInterface(globals())
PGLoader.initLoadPlugin(LiteResource.Path("test/plugin2.py"))
PGLoader.initLoadPlugin(LiteResource.Path("test/plugin1.py"))
LoadPoint1.run()

#test/plugin1.py
PluginLoader=self
p2Self=PluginLoader.requestPlugin("p2")

@PluginLoader.registPlugin(PluginLoader.getInterface["LoadPoint1"])
class plugin:
    def __init__(self) -> None:
        global PluginLoader,p2Self
        print("I am p1")
        p2Self.hello("hello")
    def __reference__(self):
        return {
            "pluginid":"p1"
        }

#test/plugin2.py
PluginLoader=self
@PluginLoader.registPlugin(PluginLoader.getInterface["LoadPoint1"])
class plugin2:
    def __init__(self) -> None:
        print("I am p2")
    
    def hello(self,*args):
        print(*args)

    def __reference__(self):
        return {
            "pluginid":"p2"
        }

>>>I am p2
>>>I am p1
>>>hello



```
# QA

## Q: AttributeError: module 'Remilia' has no attribute '...'

use the function below or see it in Remilia.__init__ to install the required lib,

if it doesn't work,please consider a issue

```python
Remilia.__REQUIREMENTS__()
```
# Learn more in our WIKI

## https://github.com/IAXRetailer/Remilia/wiki
