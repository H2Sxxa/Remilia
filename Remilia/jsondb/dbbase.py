class DBVar:
    @staticmethod
    def newfrom(vartype:type,*args,**kwargs) -> any:
        class cusVar(vartype):
            pass
        return cusVar(*args,**kwargs)