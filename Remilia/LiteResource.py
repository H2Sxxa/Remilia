import os,pathlib
class Path:
    def __init__(self,path:str,checkexist=False) -> None:
        self.path=path
        if not os.path.exists(self.path):
            if checkexist:
                raise OSError("No such file '%s'" % self.path)
            else:
                self.ISFILE=False
                self.ISDIRECTORY=False
        else:
            self._updateStatus()
            
        self.parentdir=os.path.dirname(self.path)
        self.abspath=os.path.abspath(self.path)
        self.encoding="utf-8"
        
    def _updateStatus(self):
        if os.path.isdir(self.path):
            self.ISDIRECTORY=True
            self.ISFILE=False
        elif os.path.isfile(self.path):
            self.ISDIRECTORY=False
            self.ISFILE=True
        else:
            self.ISFILE=False
            self.ISDIRECTORY=False
            
    def write(self,mode,x,encoding=None):
        self._updateStatus()
        if self.ISFILE:
            if not encoding:
                encoding=self.encoding
            with open(self.abspath,mode,encoding=encoding) as File:
                File.write(x)
            
    def getParentDir(self):
        return Path(os.path.dirname(self.abspath))
    
    def glob(self,pattern):
        """Iterate over this subtree and yield all existing files (of any
        kind, including directories) matching the given relative pattern.
        """
        return list(pathlib.Path(self.abspath).glob(pattern))
    
    def rglob(self,pattern):
        """Recursively yield all existing files (of any kind, including
        directories) matching the given relative pattern, anywhere in
        this subtree.
        """
        return list(pathlib.Path(self.abspath).rglob(pattern))
    
    def setEncoding(self,encoding="utf-8"):
        self.encoding=encoding
        return self
    
    def buildDirectory(self):
        if not self.isexist:
            os.makedirs(self.abspath)
            self._updateStatus()
        return self
    
    def buildFile(self,contant=""):
        if not self.isexist:
            self.write("w",contant,self.encoding)
            self._updateStatus()
        return self
    
    @property
    def Attrs(self):
        self._updateStatus()
        if self.ISFILE:
            return FileAttr(self)
        elif self.ISDIRECTORY:
            return DirectoryAttr(self)
        
    @property
    def isexist(self):
        return os.path.exists(self.abspath)
    
    @property
    def text(self):
        self._updateStatus()
        if self.ISFILE:
            with open(self.abspath,"r",encoding=self.encoding) as f:
                return f.read()
        else:
            return None
        
    @property
    def content(self):
        self._updateStatus()
        if self.ISFILE:
            with open(self.abspath,"rb",encoding=self.encoding) as f:
                return f.read()
        else:
            return None
        
    def __enter__(self):
        return self
    
    def __exit__(self,*args,**kwargs):
        pass
    
class FileAttr:
    def __init__(self,pathType:Path) -> None:
        self.pathType=pathType
        self.createtime=os.path.getctime(self.pathType.abspath)
        self.modifytime=os.path.getmtime(self.pathType.abspath)
        self.accesstime=os.path.getatime(self.pathType.abspath)
        self.exttuple=os.path.splitext(self.pathType.abspath)
        self.ext=os.path.splitext(self.pathType.abspath)[-1]
    
    @property
    def filesize(self):
        return os.path.getsize(self.pathType.abspath)
    
    @property
    def fileAllext(self):
        result=[]
        tempPath=self.pathType.abspath
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
    def __init__(self,pathType:Path) -> None:
        self.pathType=pathType
        self.createtime=os.path.getctime(self.pathType.abspath)
        self.modifytime=os.path.getmtime(self.pathType.abspath)
        self.accesstime=os.path.getatime(self.pathType.abspath)
        self.exttuple=os.path.splitext(self.pathType.abspath)
        self.ext=os.path.splitext(self.pathType.abspath)[-1]
    
    @property
    def totalsize(self):pass

class PathError(Exception):pass