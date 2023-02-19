import os,pathlib,json

class Path:
    def __init__(self,path:str,force_abs=True) -> None:
        self.path=path
        self.force_abs=force_abs
    
    @property
    def __get_path(self):
        return self.abspath if self.force_abs else self.path
    
    @property
    def abspath(self):
        return os.path.abspath(self.__get_path)
    
    @property
    def name(self):
        return os.path.basename(self.__get_path)
    
    @property
    def parentdir(self):
        return os.path.dirname(self.__get_path)
    
    @property
    def isexist(self) -> bool:
        return os.path.exists(self.__get_path)

    @property
    def parentPath(self):
        return Path(self.parentdir)
    
    def glob(self,pattern):
        """Iterate over this subtree and yield all existing files (of any
        kind, including directories) matching the given relative pattern.
        """
        return list(pathlib.Path(self.__get_path).glob(pattern))
    
    def rglob(self,pattern):
        """Recursively yield all existing files (of any kind, including
        directories) matching the given relative pattern, anywhere in
        this subtree.
        """
        return list(pathlib.Path(self.__get_path).rglob(pattern))
    
    def __enter__(self):
        return self
    
    def __exit__(self,*args,**kwargs):
        pass
    
    def __str__(self) -> str:
        return self.__get_path
    
    def unlink(self):
        os.unlink(self.__get_path)
class File(Path):
    def __init__(self, path: str,encoding="utf-8") -> None:
        super().__init__(path)
        self.encoding=encoding
        
    @property
    def Attrs(self):
        return FileAttr(self)

    @property
    def text(self):
        with open(self.abspath,"r",encoding=self.encoding) as f:
            return f.read()
        
    @property
    def content(self):
        with open(self.abspath,"rb") as f:
            return f.read()
    @property
    def json(self):
        try:
            return json.loads(self.text)
        except Exception as e:
            return e
    
    def write(self,mode,text):
        with open(self.abspath,mode,encoding=self.encoding) as f:
            f.write(text)
class Directory(Path):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        
    @property
    def Attrs(self):
        return DirectoryAttr(self)
    
class FileAttr:
    def __init__(self,path:File) -> None:
        self.path=path
        self.createtime=os.path.getctime(self.path.abspath)
        self.modifytime=os.path.getmtime(self.path.abspath)
        self.accesstime=os.path.getatime(self.path.abspath)
        self.exttuple=os.path.splitext(self.path.abspath)
        self.ext=os.path.splitext(self.path.abspath)[-1]
    
    @property
    def filesize(self):
        return os.path.getsize(self.path.abspath)
    
    @property
    def fileAllext(self):
        result=[]
        tempPath=self.path.abspath
        lastTemp=""
        while len(os.path.splitext(tempPath)) > 1:
            handle=os.path.splitext(tempPath)
            if lastTemp == handle[0]:
                break
            else:
                lastTemp=handle[0]
            result.append(handle[-1])
            tempPath=handle[0]
        result.reverse()
        return result

class DirectoryAttr:
    def __init__(self,pathType:Directory) -> None:
        self.pathType=pathType
        self.createtime=os.path.getctime(self.pathType.abspath)
        self.modifytime=os.path.getmtime(self.pathType.abspath)
        self.accesstime=os.path.getatime(self.pathType.abspath)
        self.exttuple=os.path.splitext(self.pathType.abspath)
        self.ext=os.path.splitext(self.pathType.abspath)[-1]
    
    @property
    def totalsize(self):pass

class PathError(Exception):pass
