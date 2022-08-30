import os,chardet
class Path:
    def __init__(self,path) -> None:
        self.path=path
        if not os.path.exists(self.path):
            raise OSError("No such file '%s'" % self.path)
        if os.path.isdir(self.path):
            self.ISDIRECTORY=True
            self.ISFILE=False
        elif os.path.isfile(self.path):
            self.ISDIRECTORY=False
            self.ISFILE=True
        else:
            self.ISFILE=False
            self.ISDIRECTORY=False
        self.parentdir=os.path.dirname(self.path)
        self.abspath=os.path.abspath(self.path)
        self.readcodingtype="utf-8"
    def getParentDir(self):
        return Path(os.path.dirname(self.path))
    
    @property
    def FileAttr(self):
        return FileAttr(self)
    
    @staticmethod
    def isexist(path:str):
        return os.path.exists(path)
    
    @property
    def text(self):
        with open(self.abspath,"r",encoding=self.readcodingtype) as f:
            return f.read()
    
class FileAttr:
    def __init__(self,pathType:Path) -> None:
        self.pathType=pathType
        self.createtime=os.path.getctime(self.pathType.abspath)
        self.modifytime=os.path.getmtime(self.pathType.abspath)
        self.accesstime=os.path.getatime(self.pathType.abspath)
        self.filesize=os.path.getsize(self.pathType.abspath)
        self.exttuple=os.path.splitext(self.pathType.abspath)
        self.ext=os.path.splitext(self.pathType.abspath)[-1]
    
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
    
    