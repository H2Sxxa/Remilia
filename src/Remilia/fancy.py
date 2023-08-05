import json
import re
from typing import Type

from .base.typings import instanceType,T

def hasInstance(cls:T) -> T:
    setattr(cls, "instance", cls())
    return cls

def typedet(string:str,strict=True) -> any:
    if not re.match(r"[\u4E00-\u9FA5A-Za-z]",string) and re.match(r"[0-9]",string) and not re.match(r"[`~!@#$%^&*()_\-+=<>?:\"{}|,\/;'\\[\]·~！@#￥%……&*（）——\-+={}|《》？：“”【】、；‘'，。、]",string):
        if "." in string:
            try:
                return float(string)
            except:
                pass
        else:
            return int(string)
    try:
        res=json.loads(string,strict=strict)
        return res
    except:
        pass
    return string