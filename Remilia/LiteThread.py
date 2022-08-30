import threading
import traceback
class ThreadValueBody(Exception):pass

class ThreadValueManager():
    def __init__(self,isHookVaule=True) -> None:
        '''
        must call it before use a LiteThread,if you want to receive a result\n
        if you call it after the thread,it won't get any value
        '''
        if isHookVaule:
            ThreadHook(self)
        self.ThreadValue={}        
    def waitResult(self,ThreadType:threading.Thread,waitwithfunc=None):
        '''
        will wait the result of the thread,or will wait the stop of the thread\n
        waitwithfunc: a callable obj to call when waiting the result
        '''
        ThreadName=ThreadType.getName()
        while True:
            if ThreadName in self.ThreadValue.keys():
                returnvalue=self.ThreadValue[ThreadName]
                self.ThreadValue.__delitem__(ThreadName)
                return returnvalue
            if waitwithfunc != None:
                waitwithfunc()
    
class ThreadHook():
    def __init__(self,ThreadManager:ThreadValueManager) -> None:
        '''
        you can use mixin or others to replace the class (or the method threadhooker)\n
        you don't need to call it if you use a ThreadValueManager(isHookValue=True)
        '''
        threading.excepthook=self.threadhooker
        self.ThreadManager=ThreadManager
        
    def threadhooker(self,HookerInfo):
        self.exc_type=HookerInfo.exc_type
        self.exc_value=HookerInfo.exc_value
        self.exc_traceback=HookerInfo.exc_traceback
        self.thread:threading.Thread=HookerInfo.thread
        self.threadName=self.thread.getName()
        if self.exc_type == ThreadValueBody:
            self.ThreadManager.ThreadValue.update({self.threadName:self.exc_value.args[0]})
        else:
            try:
                print("Exception in thread %s:" % self.threadName)
            except:
                pass
            traceback.print_exception(self.exc_type,self.exc_value,self.exc_traceback)

class LiteThread(threading.Thread):
    def run(self) -> None:
        """Method representing the thread's activity.

        You may override this method in a subclass. The standard run() method
        invokes the callable object passed to the object's constructor as the
        target argument, if any, with sequential and keyword arguments taken
        from the args and kwargs arguments, respectively.

        """
        try:
            if self._target:
                try:
                    returnValue=self._target(*self._args, **self._kwargs)
                    raise ThreadValueBody(returnValue)
                except BaseException as e:
                    raise e
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs
        

