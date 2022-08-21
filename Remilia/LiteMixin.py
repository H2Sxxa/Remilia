import types

def MixInClass(pyClass:object, mixInClass:object, makeAncestor:bool=False,ignoreMagicMethod=False) -> None:
   '''
   @param {object} pyClass the target class\n
   @param {object} mixInClass your class\n
   @param {bool} makeAncestor modify the Ancestor of pyClass
   '''
   if makeAncestor:
     if mixInClass not in pyClass.__bases__:
         try:
            pyClass.__bases__ = (mixInClass,) + pyClass.__bases__
         except:
            raise MixInError("If you want to modify the ans class of the pyClass(without any ans),please False the makeAncestor,but it cannot modify the magic method")
   else:
     baseClasses = list(mixInClass.__bases__)
     baseClasses.reverse()
     for baseClass in baseClasses:
        MixInClass(pyClass, baseClass)
     for name in dir(mixInClass):
         if not name.startswith('__'):
            member = getattr(mixInClass, name)
            if type(member) is types.MethodType:
               member = member.__func__
            setattr(pyClass, name, member)
         elif ignoreMagicMethod:
            member = getattr(mixInClass, name)
            if type(member) is types.MethodType:
               member = member.__func__
            try:
               setattr(pyClass, name, member)
            except:
               pass

def InjectMethod(pyClass:object):
   '''
   A decorator for easy inject function
   '''
   def warpper(func:types.FunctionType):
      setattr(pyClass,func.__name__,types.MethodType(func,pyClass))
      return func
   return warpper

def MixInFunction(pyFunction:types.FunctionType,mixinFunction:types.FunctionType):
   '''
   a ugly function , but ...\n
   use it with static function,otherwise it may cause a error
   '''
   pyFunction.__code__=mixinFunction.__code__
class OriMethod:
   def __init__(self,pyClass:object) -> None:
      '''
      a class used to save the raw class\n
      cls=OriMethod(class)\n
      cls.class_method()
      '''
      MixInClass(self,pyClass)

class MixInError(Exception):
   def __init__(self, *args: object) -> None:
      super().__init__(*args)