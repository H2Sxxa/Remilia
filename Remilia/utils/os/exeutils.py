import subprocess

'''
@Author H2Sxxa
'''


class ProcessHandle:
    def __init__(self,path:str,log_file:str,*args) -> None:
        with open(log_file,"w",encoding="utf-8") as f:
                self.prcs=subprocess.Popen(
                        args=(path,*args),
                        shell=True,
                        stdout=f,
                        stderr=f,
                )
class Client:
    def __init__(self,gsspath:str,log_file:str="shadowsocks2.log",*args) -> None:
        self.ph=ProcessHandle(gsspath,log_file,*args)
        
    @property
    def process(self):
        return self.ph.prcs

    def wait(self):
        self.process.wait()