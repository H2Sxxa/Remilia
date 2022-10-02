from inspect import getframeinfo,stack


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
