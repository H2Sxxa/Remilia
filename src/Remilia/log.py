from functools import partial
from pathlib import Path
from colorama import Fore, Back, Style, Cursor
from colorama import init as initcolor
from typing import Callable, Dict, List, Optional, Union,TYPE_CHECKING
from typing_extensions import Self
from time import strftime, localtime

from .res import rFile, rPath
from .base.models import Ruler
from .base.typings import PairType
from .impl import CommonPair as Pair

from platform import system
import inspect

if TYPE_CHECKING:
    class _CallLogMethod:
        def __call__(self, *args:str) -> None:
            ...

try:
    if system() == "Windows":
        initcolor(wrap=True)
    else:
        initcolor(wrap=False)
except:
    pass


class Log:
    def __init__(
        self, name: str, location: str, logs: tuple = (), ruler: Ruler = Ruler()
    ) -> None:
        super().__init__()
        self.ruler = ruler
        self.location = location
        self.logs = [str(log) for log in logs]
        self.name = name.upper()

    @property
    def color(self) -> str:
        # colorama stuff
        fore = Fore
        style = Style
        cursor = Cursor
        back = Back
        # base
        location = self.location
        ruler = self.ruler
        name = self.name
        text = " ".join(self.logs)
        time = strftime(self.ruler.timeformat, localtime())
        __all__ = [ruler, location, name, text, time, fore, style, cursor, back]
        return eval(self.ruler.excolor)

    @property
    def plain(self) -> str:
        location = self.location
        ruler = self.ruler
        name = self.name
        text = " ".join(self.logs)
        time = strftime(self.ruler.timeformat, localtime())
        __all__ = [ruler, location, name, text, time]
        return eval(self.ruler.explain)


class LogCat:
    all_logs: List[Log]
    all_subs: List[PairType[Callable[[Log], bool], rFile]]

    def __init__(self) -> None:
        self.all_logs = []
        self.all_subs = []

    def get_logs(self, filter: Callable[[Log], bool] = lambda _: True) -> List[Log]:
        return [log for log in self.all_logs if filter(log)]

    def record(self, *logs: Log) -> Self:
        self.all_logs.extend(logs)
        self._subwrite(*logs)
        return self

    def export(
        self,
        path: Union[rFile, rPath, Path, str],
        filter: Callable[[Log], bool] = lambda _: True,
        mode: str = "w",
    ) -> Self:
        rflog = rFile(path) if not isinstance(path, rFile) else path
        rflog.write(
            data="\n".join([log.plain for log in self.get_logs(filter)]), mode=mode
        )
        return self

    def subscribe(
        self, *pairs: PairType[Callable[[Log], bool], Union[rFile, rPath, Path, str]]
    ) -> Self:
        subs = [
            Pair(
                pair.name,
                rFile(pair.value) if not isinstance(pair.value, rFile) else pair.value,
            )
            for pair in pairs
        ]
        self.all_subs.extend(subs)
        return self

    def _subwrite(self, *logs: Log) -> None:
        for sub in self.all_subs:
            mode = "a" if sub.value.exists() else "w"
            for log in logs:
                if sub.name(log):
                    sub.value.write(data=log.plain + "\n", mode=mode)


class Logger:
    def __init__(
        self,
        logcat: LogCat = LogCat(),
        ruler_map: Optional[Dict[str, Ruler]] = {},
        model: str = "'%s[ '+name+' '+time+' '+location+'] %s'+text",
    ) -> None:
        self.ruler_map = {
            "DEBUG": Ruler(level=3).exgenerate(model, Fore.CYAN, Style.RESET_ALL),
            "INFO": Ruler(level=5).exgenerate(
                model, Fore.LIGHTGREEN_EX, Style.RESET_ALL
            ),
            "WARN": Ruler(level=6).exgenerate(
                model, Fore.LIGHTYELLOW_EX, Style.RESET_ALL
            ),
            "ERROR": Ruler(level=7).exgenerate(
                model, Fore.LIGHTRED_EX, Style.RESET_ALL
            ),
        }
        self.ruler_map.update(ruler_map)
        self.logcat = logcat
        self.handle_out = print
        self.vlevel = 5
        global instance
        instance = self

    def set_vlevel(self, vlevel: int) -> Self:
        self.vlevel = vlevel
        return self

    def ex_ruler(self, model: str, **colors: Dict[str, tuple]) -> Self:
        for n, c in colors.items():
            self.to_ruler(n, self.get_ruler(n).exgenerate(model, *c))
        return self

    def to_ruler(self, name: str, ruler: Ruler) -> Self:
        self.ruler_map.update({name.upper(): ruler})
        return self

    def get_ruler(self, name: str) -> Ruler:
        try:
            return self.ruler_map[name.upper()]
        except:
            return Ruler()

    def print(self, name: str, *log: Log) -> None:
        clog = Log(
            name,
            inspect.getmodule(inspect.stack()[1][0]).__name__,
            log,
            self.get_ruler(name),
        )
        self.logcat.record(clog)
        if self.vlevel >= clog.ruler.level:
            self.handle_out(clog.color)

    def __getattr__(self, name) -> "_CallLogMethod":
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )
        return partial(self.print, name)


instance: Logger


def get_logger(*args, **kwargs) -> Logger:
    """
    args & kwargs only work under (instance == None)
    """
    global instance
    try:
        if instance != None:
            return instance
        else:
            instance = Logger(*args, **kwargs)
            return instance
    except:
        instance = Logger(*args, **kwargs)
        return instance
