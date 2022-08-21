from inspect import getframeinfo,stack


def Deprecated(func):
    '''
    A deprecated decorator , love from java
    '''
    def inner(*args,**kwargs):
        caller = getframeinfo(stack()[1][0])
        print("WARNING:Somewhere are useing a deprecated api file:%s line:%s"%(caller.filename,caller.lineno))
        result=func(*args,**kwargs)
        return result
    return inner
