from .db import JsonDB
class DBVar:
    def setdb(self,db:JsonDB):
        self.db=db
        
    def sync(self):
        if "db" in dir(self):
            if isinstance(self.db,JsonDB):
                self.uploadtoDB(self.db)