def collect_attr(target):
    return [{_:getattr(target,_)} for _ in dir(target) if not _.startswith("__") and not _.endswith("_") and not _.startswith("_") and  not _.endswith("_")]