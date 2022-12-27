from ..lite.LiteResource import File
from ..lite.LiteData import JsonFile
from typing import List

class DBError(Exception):pass

class Table(dict):
    def sync(self):
        if "db" in dir(self):
            if isinstance(self.db,JsonDB):
                self.uploadtoDB(self.db)
    def __AutoSync(self):
        if self.autosync:
            self.sync()
    def setAutoSync(self,x:bool):
        self.autosync=x
    def uploadtoDB(self,db:"JsonDB"):
        db.updateTable(self)
    def setDB(self,db:"JsonDB"):
        self.db=db
    def setname(self,tablename:str) -> "Table":
        self.oriname=tablename
        self.tablename=tablename
        self.__AutoSync()
        return self
    def getoriname(self) -> str:
        return self.oriname
    def getname(self) -> str:
        return self.tablename
    def getkey(self,key:str) -> any:
        return self[key]
    def haskey(self,key:str) -> bool:
        return self.__contains__(key)
    def delkey(self,key:str) -> "Table":
        self.__delitem__(key)
        self.__AutoSync()
        return self
    def setkey(self,key:str,value:any) -> "Table":
        self.update({key:value})
        self.__AutoSync()
        return self
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
        
    def getname(self):
        return self.dbname
    
    def createTable(self,tablename:str) -> None:
        data=self.jsonfile.read("data")
        tables=self.jsonfile.read("tables")
        if tablename not in tables:
            tables.append(tablename)
            data[0]["tables"].update({tablename:{}})
            self.jsonfile.write("tables",tables,indent=self.indent)
            self.jsonfile.write("data",data,indent=self.indent)
        else:
            raise DBError(f"Table '{tablename}' exists")
    def getTable(self,tablename:str) -> Table:
        if self.hasTable(tablename):
            table=Table(self.jsonfile.read("data")[0]["tables"][tablename])
            table.setAutoSync(False)
            table.setname(tablename)
            table.setDB(self)
            return table
    
    def getAllTable(self) -> List[Table]:
        return [ self.getTable(_) for _ in self.listTable() ]
    
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
        else:
            raise DBError(f"No such table '{tablename}'")
        
    def listTable(self) -> list:
        return self.jsonfile.read("tables")