#from typing import Optional
import types
from colorama import Fore
from time import strftime,localtime

from .LiteEvent import registEvent,CommonEvent,EventBus
class LogEvent(CommonEvent):pass
class DebugEvent(LogEvent):pass
LogEventBus=EventBus()
class LogStyle:
    def __init__(self,
                 LogHeader="[ <name> | <logger> | <time> ]",
                 LogBody="<msg>",
                 LogTimeFormat="%H:%M:%S",
                 ) -> None:
        '''
        ```
        [ <name> | <logger> | <time> ] <msg>
        └──────────────┬─────────────┘ └─┬─┘
                    LogHeader         LogBody
        ```
        '''
        self.LogHeader=LogHeader
        self.LogBody=LogBody
        self.LogTimeFormat=LogTimeFormat
        
    @property
    def nowtime(self):
        return strftime(
            self.LogTimeFormat,
            localtime()
            )

    def buildPlainHeader(self,logger,name):
        return self.LogHeader.replace("<name>",name).replace("<logger>",logger).replace("<time>",self.nowtime)
    
    def buildPlainBody(self,*args):
        return "".join(map(str,args))
    
    def buildPlainLog(self,logger:str,name:str,*arg):
        return "%s %s" % (
            self.buildPlainHeader(logger,name),
            self.buildPlainBody(*arg),
            )
    
    def buildColorLog(self,logger:str,name:str,headercolor:Fore,bodycolor:Fore,*arg):
        return f"{headercolor}%s {bodycolor}%s" % (
            self.buildPlainHeader(logger,name),
            self.buildPlainBody(*arg),
            )
        
class TextStyle:
    def __init__(self,
                 headerColor:Fore=Fore.GREEN,
                 bodyColor:Fore=Fore.RESET,
                 ) -> None:
        self.headerColor=headerColor
        self.bodyColor=bodyColor

class LogRecorder:
    def __init__(self) -> None:
        self.lastplainlog=""
        self.lastcolorlog=""
        self.lastfunc=None
        self.totalplainlog=[]
        self.totalcolorlog=[]
        
    def exportAllLog(self):
        pass
    
    def exportCateLog(self,category):
        pass
    
    def classify(self):
        if self.lastfunc.__name__ not in dir(self):
            setattr(self,self.lastfunc.__name__,list())
        loglist=getattr(self,self.lastfunc.__name__)
        if isinstance(loglist,list):
            loglist.append(self.lastplainlog)
        self.totalplainlog.append(self.lastplainlog)
        self.totalcolorlog.append(self.lastcolorlog)
        self.__write()
        
    def __write(self):pass
    
class Logger:
    def __init__(self,
                 name:str="Logger",
                 style:LogStyle=LogStyle(),
                 recorder:LogRecorder=LogRecorder()
                 ) -> None:
        self.name=name
        self.style=style
        self.recoder=recorder
        self.addPrintType("info")
        self.addPrintType("warn",TextStyle(Fore.YELLOW,Fore.RESET))
        self.addPrintType("error",TextStyle(Fore.RED,Fore.RESET))
        self.isSilent=False
        self.isDebug=False
        
    def setSilent(self,x:bool=False):
        self.isSilent=x
        
    def setDebug(self,x:bool=False):
        self.isDebug=x
        
    @registEvent(DebugEvent,LogEventBus)
    def debug(self,*args):pass
    
    def addPrintType(self,
                     name:str,
                     style:TextStyle=TextStyle(),
                    ) -> None:
        def func(self,*args):
            self.println(func,*args)
        func.__name__=name
        func.__style__:TextStyle=style
        setattr(self,name,types.MethodType(func,self))

    def println(self,func:types.MethodType,*args):
        plainlog=self.style.buildPlainLog(
            self.name,
            func.__name__,
            *args
            )
        colorlog=self.style.buildColorLog(
            self.name,
            func.__name__.upper(),
            func.__style__.headerColor,
            func.__style__.bodyColor,
            *args
            )
        self.recoder.lastcolorlog=colorlog
        self.recoder.lastplainlog=plainlog
        self.recoder.lastfunc=func
        self.recoder.classify()
        if self.isSilent:
            return
        print(colorlog)