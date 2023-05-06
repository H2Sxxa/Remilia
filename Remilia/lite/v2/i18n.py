from abc import abstractclassmethod
import json,yaml
from typing import Any, List
from ..LiteResource import File

class Parser:
    @abstractclassmethod
    def todict(self,text:str) -> dict:pass

def getPaserfromCallable(call:callable):
    psr=Parser()
    setattr(psr,psr.todict.__name__,call)
    return psr

JSONParser=getPaserfromCallable(lambda text : json.loads(text))
YAMLParser=getPaserfromCallable(lambda text : yaml.load(text,yaml.Loader))

class I18nFile(File):
    def __init__(self, path: str,parser:Parser, encoding="utf-8") -> None:
        super().__init__(path, encoding)
        self.parser=parser
        
    def tomap(self) -> List[dict]:
        for i in self.parser.todict(self.text):
            for k,v in i.items():
                pass
        
class I18nManager:
    def __init__(self,*i18n:I18nFile) -> None:
        for ife in i18n:
            ife.tomap()

    def localize(self,uname) -> Any:pass
    
    def slocalize(self,uname) -> str:pass