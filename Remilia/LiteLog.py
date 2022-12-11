#from typing import Optional
import types,re
from typing import List
from colorama import Fore,Style,Back,init
from time import strftime,localtime
from platform import system
from os.path import exists
if system() == "Windows":
    init(wrap=True)
else:
    init(wrap=False)
    
class LogStyle:
    def __init__(self,
                 LogHeader="<headercolor>[ <name> | <logger> | <time> ]<bodycolor>",
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

    def initRenderHeader(self,logger,name):
        return self.LogHeader.replace("<name>",name).replace("<logger>",logger).replace("<time>",self.nowtime)
    
    def buildPlainHeader(self,logger,name):
        return re.sub(r"=:(.*?):=","",re.sub(r"[<](.*?)[>]","",self.initRenderHeader(logger,name)))
    
    def buildPlainBody(self,*args):
        return " ".join(map(str,args))
    
    def buildPlainLog(self,logger:str,name:str,*args):
        return "%s %s" % (
            self.buildPlainHeader(logger,name),
            self.buildPlainBody(*args),
            )
        
    def buildColorHeader(self,logger:str,name:str,style):
        header=self.initRenderHeader(logger,name)
        for temp in set(re.findall(r"<(.+?)>",header)):
            if temp in dir(style):
                header=header.replace("<"+temp+">",getattr(style,temp))
        return re.sub(r"[<](.*?)[>]","",header).replace("=:","").replace(":=","")
    
    def buildColorLog(self,logger:str,name:str,style,*args):
        return f"%s %s" % (
            self.buildColorHeader(logger,name,style),
            self.buildPlainBody(*args),
            )

class TextStyle:
    def __init__(self,**kwargs) -> None:
        for key,value in kwargs.items():
            setattr(self,str(key),value)
    
    
    @staticmethod
    def buildLogColor(headercolor:Fore=Fore.GREEN,
                      bodycolor:Fore=Fore.RESET
                      ):
        '''
        A default static method
        '''
        return TextStyle(
                bodycolor=bodycolor,
                headercolor=headercolor
            )

class SimpleLog:
    def __init__(self,plainlog:str,colorlog:str,logname:str) -> None:
        self.plainlog=plainlog
        self.colorlog=colorlog
        self.logname=logname
    
    def __str__(self) -> str:
        return self.plainlog

    def __clstr__(self) -> str:
        return self.colorlog
    
class LogRecorder:
    def __init__(self) -> None:
        '''
        when you add a new print type,there will be a new list in LogRecoder
        ```python
        logger=Logger()
        logger.addPrintType("newprint")
        logger.newprint(1,2,3)
        print(type(logger.recorder.newprint))
        
        <class 'list'>
        ```
        '''
        self.lastplainlog=""
        self.lastcolorlog=""
        self.lastfunc=None
        self.totallog=[]
        self.__subscribepaths=[]
    
    def subscribePath(self,path:str,resetfile=True) -> None:
        self.__subscribepaths.append(path)
        if resetfile:
            with open(path,"w",encoding="utf-8") as f:
                f.write("")
                
    def exportLog(self,path:str,ignore:List[str]=[]):
        fintotallog=[ _ for _ in self.totallog if _.logname not in ignore]
        with open(path,"w",encoding="utf-8") as f:
            f.write("\n".join(map(str,fintotallog)))
    
    def exportCateLog(self,category:str,path:str):
        with open(path,"w",encoding="utf-8") as f:
            f.write("\n".join(map(str,self.getLogfromCate(category))))
    
    def getLogfromCate(self,category:str):
        if category in dir(self):
            return getattr(self,category)
        else:
            return []
    
    def classify(self):
        if self.lastfunc.__name__ not in dir(self):
            setattr(self,self.lastfunc.__name__,list())
        loglist=getattr(self,self.lastfunc.__name__)
        if isinstance(loglist,list):
            loglist.append(SimpleLog(self.lastplainlog,self.lastcolorlog,self.lastfunc.__name__))
        self.totallog.append(SimpleLog(self.lastplainlog,self.lastcolorlog,self.lastfunc.__name__))
        self.__writeSub()
    
    def __writeSub(self):
        return [ self.__write(_) for _ in self.__subscribepaths ]
    
    
    def __write(self,path:str):
        mode=lambda: "a" if exists(path) else "w"
        with open(path,mode(),encoding="utf-8") as f:
            f.write(self.lastplainlog+"\n")
            
class Logger:
    def __init__(self,
                 name:str="Logger",
                 style:LogStyle=LogStyle(),
                 recorder:LogRecorder=LogRecorder()
                 ) -> None:
        '''
        ## Useage
        ### add new print type
        you should know that info/warn/error have been contained in this class,you should not add it mannually
        use it like following:
        ```python
        logger=Logger(__name__)
        logger.info(1,2,3)
        logger.addPrintType("newprint")
        logger.newprint(1,2,3)
        
        [ INFO | __main__ | 14:31:14 ] 123
        [ NEWPRINT | __main__ | 14:31:14 ] 123
        ```
        you can also use addPrintType and TextStyle to custom your log color
        
        ## Extension
        ### Logger.style <class "LogStyle">
        ### Logger.recorder <class "LogRecoder">
        
        '''
        self.name=name
        self.style=style
        self.recorder=recorder
        self.addPrintType("info")
        self.addPrintType("warn",TextStyle.buildLogColor(Fore.YELLOW,Fore.RESET))
        self.addPrintType("error",TextStyle.buildLogColor(Fore.RED,Fore.RESET))
        self.isSilent=False
        self.isDebug=False
        self.addPrintType("debug",TextStyle.buildLogColor(Fore.CYAN))
        
    def setSilent(self,x:bool=False):
        self.isSilent=x
        
    def setDebug(self,x:bool=False):
        self.isDebug=x
    
    def addPrintType(self,
                     name:str,
                     style:TextStyle=TextStyle.buildLogColor(),
                    ) -> None:
        def func(self,*args):
            self.println(func,*args)
        func.__name__=name
        func.__style__:TextStyle=style
        setattr(self,name,types.MethodType(func,self))

    def println(self,func:types.MethodType,*args):
        plainlog=self.style.buildPlainLog(
            self.name,
            func.__name__.upper(),
            *args
            )
        colorlog=self.style.buildColorLog(
            self.name,
            func.__name__.upper(),
            func.__style__,
            *args
            )
        self.recorder.lastcolorlog=colorlog
        self.recorder.lastplainlog=plainlog
        self.recorder.lastfunc=func
        self.recorder.classify()
        if self.isSilent:
            return
        else:
            if func.__name__ == "debug" and not self.isDebug:
                return
            print(colorlog)
            
    def info():
        '''
        A method built by addPrintType()
        '''
    def warn():pass
    def error():pass
    def debug():pass
    
class __DefaultStyle:
    @property
    def default_LogStyle1(self):
        return LogStyle(
            LogHeader=f" <time> <headercolor>[ <logger> ] =:{Style.BRIGHT}:=[ <name> ]<bodycolor>=:{Style.RESET_ALL}:="
        )
DefaultStyle=__DefaultStyle()