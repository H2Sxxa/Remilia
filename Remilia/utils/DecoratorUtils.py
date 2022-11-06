from inspect import getframeinfo,stack
from types import MethodType


def Deprecated(func):
    '''
    A deprecated decorator , love from java
    '''
    def inner(*args,**kwargs):
        caller = getframeinfo(stack()[1][0])
        print("WARNING:Somewhere are useing a deprecated api File \"%s\", line %s, in %s"%(caller.filename,caller.lineno,caller.function))
        result=func(*args,**kwargs)
        return result
    return inner

def Redirect(tofunc):
    '''
    when got exception it can post exception to other function to handle it
    '''
    def outter(func):
        def inner(*args,**kwargs):
            try:
                result=func(*args,**kwargs)
            except Exception as excp:
                result=tofunc(excp)
            return result
        return inner
    return outter

def AnnoMethod(func):
    '''
    use it in a class
    #FIX use 'delattr' to replace 'del'
    '''
    try:
        del func
        return
    except:pass
    return func.__class__