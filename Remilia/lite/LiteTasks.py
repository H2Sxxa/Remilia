
import traceback
from colorama import init,Fore,Back,Style
import platform
if platform.system() == "Windows":
    init(autoreset=True,wrap=True)
TASKFORE={
    "TASK_NAME":Fore.CYAN,
    "TASK_START":Fore.LIGHTCYAN_EX,
    "TASK_SUCCESS":Fore.GREEN,
    "TASK_ERROR":Fore.LIGHTRED_EX,
    "TASK_RESET":Fore.RESET
}    

class Task:
    def __init__(self,name,target,*args,**kwargs) -> None:
        self.name=name
        self.target=target
        self.args=args
        self.kwargs=kwargs
        self.reuslt=None
        self.status=None
    def run(self):
        print(f"{TASKFORE['TASK_NAME']}:TASK %s {TASKFORE['TASK_START']}START{TASKFORE['TASK_RESET']}" % self.name)
        try:
            self.result=self.target(*self.args,**self.kwargs)
            self.status="SUCCESS"
            print(f"{TASKFORE['TASK_NAME']}:TASK %s {TASKFORE['TASK_SUCCESS']}SUCCESS{TASKFORE['TASK_RESET']}" % self.name)
        except:
            traceback.print_exc()
            self.result=traceback.format_exc()
            self.status="ERROR"
            print(f"{TASKFORE['TASK_NAME']}:TASK %s {TASKFORE['TASK_ERROR']}ERROR{TASKFORE['TASK_RESET']}" % self.name)
    def getResult(self):
        return self.result
    def getStatus(self):
        return self.status
class TaskGroup:
    def __init__(self,*tasks:Task) -> None:
        self.nowtask=None
        self.tasks=tasks
        self.tasksresult=[]
    def run(self):
        for task in self.tasks:
            print(f"{TASKFORE['TASK_SUCCESS']}TASK (%s/%s)"%(self.tasks.index(task)+1,len(self.tasks)))
            task.run()
            self.tasksresult.append(task.getResult())
            if task.getStatus() == "ERROR":
                break