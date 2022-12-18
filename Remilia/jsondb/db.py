from ..lite.LiteResource import File
from ..lite.LiteData import JsonFile

class Table(dict):
    def setname(self,tablename:str) -> None:
        self.oriname=tablename
        self.tablename=tablename
    def getoriname(self) -> str:
        return self.oriname
    def getname(self) -> str:
        return self.tablename
    def getkey(self,key:str) -> any:
        return self[key]
    def haskey(self,key:str) -> bool:
        return self.__contains__(key)
    def setkey(self,key:str,value:any) -> None:
        self.update({key:value})
class JsonDB:
    def __init__(self,dbfile:File,dbname:str,indent:int=4) -> None:
        isinit=dbfile.isexist
        self.indent=indent
        self.dbname=dbname
        self.jsonfile=JsonFile(dbfile)
        if not isinit:
            self.initdb()
        
    def initdb(self):
        self.jsonfile.write("name",self.dbname)
        self.jsonfile.write("tables",[],indent=self.indent)
        self.jsonfile.write("data",[{"tables":{}}],indent=self.indent)
        
    def hasTable(self,tablename:str) -> bool:
        if tablename in self.jsonfile.read("tables"):
            return True
        else:
            return False
        
    def createTable(self,tablename:str) -> None:
        data=self.jsonfile.read("data")
        tables=self.jsonfile.read("tables")
        tables.append(tablename)
        data[0]["tables"].update({tablename:{}})
        self.jsonfile.write("tables",tables,indent=self.indent)
        self.jsonfile.write("data",data,indent=self.indent)
        
    def getTable(self,tablename:str) -> Table:
        if self.hasTable(tablename):
            table=Table(self.jsonfile.read("data")[0]["tables"][tablename])
            table.setname(tablename)
            return table
        
    def updateTable(self,table:Table) -> None:
        if table.getname() == table.getoriname():
            data=self.jsonfile.read("data")
            data[0]["tables"].update({table.getname():table})
            self.jsonfile.write("data",data,indent=self.indent)
        else:
            self.delTable(table.getoriname())
            data=self.jsonfile.read("data")
            data[0]["tables"].update({table.getname():table})
            self.jsonfile.write("data",data,indent=self.indent)
            
    def delTable(self,tablename:str) -> None:
        if self.hasTable(tablename):
            data=self.jsonfile.read("data")
            tables=self.jsonfile.read("tables")
            tables.remove(tablename)
            del data[0]["tables"][tablename]
            self.jsonfile.write("tables",tables,indent=self.indent)
            self.jsonfile.write("data",data,indent=self.indent)