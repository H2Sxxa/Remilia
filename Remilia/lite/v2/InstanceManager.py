
class InstanceReference(dict):
    def get(self,name:str):
        return self[name]
    def add(self,name:str,obj):
        self.update({name:obj})
        return self

Globals_Instance=InstanceReference()

def from_global(name:str):
    return Globals_Instance.get(name)


def to_global(name:str,obj):
    Globals_Instance.add(name,obj)
    return Globals_Instance


