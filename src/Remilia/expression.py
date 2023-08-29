from functools import partial
from typing import Callable, Iterable, List, Optional, Union, NoReturn
from typing_extensions import Self
from Remilia.base.typings import NT, RT, T, VT
from dataclasses import dataclass

from .base.models import Args


def __handleCondition(
    condition: Union[Callable[..., bool], bool],
    condargs: Args = Args(),
) -> bool:
    if isinstance(condition, Callable):
        condition = condition(*condargs.args, **condargs.kwargs)
    return condition


def ifElse(
    condition: Union[Callable[..., bool], bool] = lambda: True,
    ifdo: Callable[..., NT] = lambda: None,
    elsedo: Callable[..., VT] = lambda: None,
    condargs: Args = Args(),
    ifdoargs: Args = Args(),
    elsedoargs: Args = Args(),
) -> Union[NT, VT]:
    return (
        ifdo(*ifdoargs.args, **ifdoargs.kwargs)
        if __handleCondition(condition=condition, condargs=condargs)
        else elsedo(*elsedoargs.args, **elsedoargs.kwargs)
    )


def ifElseV(
    condition: Union[Callable[..., bool], bool] = lambda: True,
    ifdo: T = None,
    elsedo: T = None,
    condargs: Args = Args(),
):
    return ifdo if __handleCondition(condition=condition, condargs=condargs) else elsedo


def when(
    condition: Union[Callable[..., bool], bool] = lambda: True,
    whendo: Callable[..., T] = lambda: None,
    condargs: Args = Args(),
    whendoargs: Args = Args(),
    elsevalue: T = None,
) -> T:
    return (
        whendo(*whendoargs.args, **whendoargs.kwargs)
        if __handleCondition(condition=condition, condargs=condargs)
        else elsevalue
    )


def whenV(
    condition: Union[Callable[[], bool], bool] = lambda: True,
    whendo: T = None,
    condargs: Args = Args(),
) -> T:
    return whendo if __handleCondition(condition=condition, condargs=condargs) else None


def exception(exc: Exception = Exception()) -> NoReturn:
    raise exc


def tryDo(
    trydo: Callable[..., T],
    exceptdo: Callable[[Exception], T] = lambda exc: exception(exc),
    trydoargs: Args = Args(),
) -> T:
    try:
        return trydo(*trydoargs.args, **trydoargs.kwargs)
    except Exception as e:
        return exceptdo(e)


def invoke(obj: T, objmethod: Callable[..., None], *args, **kwargs) -> T:
    objmethod(*args, **kwargs)
    return obj


def forEach(iterobj: Iterable[T], eachdo: Callable[[T], RT] = lambda _: _) -> RT:
    return [eachdo(i) for i in iterobj]


def forEachEnum(func: Callable[[int, T], RT], iterable: Iterable[T]) -> List[RT]:
    return [func(index, x) for index, x in enumerate(iterable)]


# LogicEntry utils


@dataclass
class LambdaPreSet:
    setIt: Callable[[T], Callable[..., T]] = lambda value: partial(
        lambda value, *_: value, value
    )
    returnIt: Callable[[T], T] = lambda _: _
    equalIt: Callable[[T], Callable[[T], bool]] = lambda value: partial(
        lambda value, _: value == _, value
    )
    invokeIt: Callable[[Callable], T] = lambda _: _()
    printIt: Callable[[], None] = lambda _: print(_)
    printValue: Callable[[T], Callable[[], None]] = lambda value: lambda: print(value)
    isNone: Callable[[T], bool] = lambda _: _ is None
    notNone: Callable[[T], bool] = lambda _: _ is not None
    wrapCall: Callable[[Callable], Callable] = lambda call: partial(
        lambda call, *args, **kwargs: call(*args, **kwargs), call
    )
    exception: Callable[..., NoReturn] = lambda _: _
    returnValue: Callable[[T], Callable[[], T]] = lambda value: lambda: value


@dataclass
class LPS:
    SI = LambdaPreSet.setIt
    RI = LambdaPreSet.returnIt
    PI = LambdaPreSet.printIt
    PV = LambdaPreSet.printValue
    RV = LambdaPreSet.returnValue
    EI = LambdaPreSet.equalIt
    II = LambdaPreSet.invokeIt
    IN = LambdaPreSet.isNone
    NN = LambdaPreSet.notNone
    WC = LambdaPreSet.wrapCall
    EXC = LambdaPreSet.exception


class LogicExpression:
    __currentResult: RT = None

    def doto(self, doto: Callable[[T], RT]) -> Self:
        return self.setResult(doto(self.__currentResult))

    def when(
        self,
        condition: Union[Callable[[RT], bool], bool] = lambda: True,
        whendo: Callable[[RT], T] = lambda _: _,
    ) -> Self:
        return self.setResult(
            when(
                condition,
                whendo,
                condargs=self.__currentArgs,
                whendoargs=self.__currentArgs,
                elsevalue=self.__currentResult,
            )
        )

    def ifElse(
        self,
        condition: Union[Callable[[RT], bool], bool] = lambda _: True,
        ifdo: Callable[[RT], NT] = lambda _: _,
        elsedo: Callable[[RT], VT] = lambda _: _,
    ) -> Self:
        return self.setResult(
            ifElse(
                condition=condition,
                ifdo=ifdo,
                elsedo=elsedo,
                condargs=self.__currentArgs,
                ifdoargs=self.__currentArgs,
                elsedoargs=self.__currentArgs,
            )
        )

    def forEach(self, eachdo: Callable[[T], RT]) -> Self:
        return self.setResult(forEach(self.__currentResult, eachdo))

    def tryDo(
        self,
        trydo: Callable[[RT], T],
        exceptdo: Callable[[RT, Exception], T] = lambda _, exc: exception(exc),
        trydoargs: Args = Args(),
    ) -> Self:
        return self.setResult(
            tryDo(trydo=trydo, exceptdo=exceptdo, trydoargs=trydoargs)
        )

    def isEqual(self, value: T) -> "_BooleanExp":
        return _BooleanExp(value == self.__currentResult, self)

    def exception(self, exc: Exception = Exception()) -> NoReturn:
        return exception(exc=exc)

    @staticmethod
    def new(value: Optional[T] = None) -> "LogicExpression":
        return LogicExpression().setResult(value)

    @property
    def clear(self) -> Self:
        return self.setResult(None)

    @property
    def __currentArgs(self) -> Args:
        return Args(self.__currentResult)

    # Result getter

    def hasResult(self) -> bool:
        return self.__currentResult is not None

    def setResult(self, value: T) -> Self:
        self.__currentResult = value
        return self

    def getResult(self) -> RT:
        return self.__currentResult


class _BooleanExp:
    __true, __false = [], []

    def __init__(self, value: bool = True, lp: LogicExpression = LogicExpression):
        self.__lp = lp
        self.__value = value

    def then(self) -> LogicExpression:
        if self.__value:
            forEach(self.__true, LambdaPreSet.invokeIt)
        else:
            forEach(self.__false, LambdaPreSet.invokeIt)
        return self.__lp

    def ifTrue(self, truedo: Callable[[], None]):
        self.__true.append(truedo)
        return self

    def ifFalse(self, falsedo: Callable[[], None]):
        self.__false.append(falsedo)
        return self

    def sort(self, target=True, sortfunc=lambda _: _.sort()) -> Self:
        ifElse(
            target,
            LambdaPreSet.wrapCall(sortfunc),
            LambdaPreSet.wrapCall(sortfunc),
            ifdoargs=Args(self.__true),
            elsedo=Args(self.__false),
        )
        return self
