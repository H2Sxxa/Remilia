from enum import Enum
from functools import partial
from typing import Callable, Dict, Iterable, List, Optional, Union, NoReturn
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
    exception: Callable[[Exception], NoReturn] = lambda _: exception(_)
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
        exceptdo: Callable[[RT, Exception], T] = LPS.EXC,
        trydoargs: Args = Args(),
    ) -> Self:
        return self.setResult(
            tryDo(trydo=trydo, exceptdo=exceptdo, trydoargs=trydoargs)
        )

    def isEqual(self, value: T) -> "BooleanExpression":
        return BooleanExpression(value == self.__currentResult, self)

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


class BooleanExpression:
    __true, __false = [], []

    def __init__(self, value: bool = True, lp: LogicExpression = LogicExpression):
        self.__lp = lp
        self.__value = value

    def then(self) -> LogicExpression:
        if self.__value:
            forEach(self.__true, LambdaPreSet.invokeIt)
        else:
            forEach(self.__false, LambdaPreSet.invokeIt)
        self.__true.clear()
        self.__false.clear()
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


class MatchExpression:
    __cases: List[Callable] = []
    value = None
    __default = lambda _: _

    def match(self, value: T) -> Self:
        self.value = value
        return self

    def case(self, value: T, casedo: Callable[[], T]) -> Self:
        self.__cases.append(
            (
                value,
                casedo,
            )
        )
        return self

    def default(self, default: Callable[[T], T]) -> Self:
        self.__default = default
        return self

    def then(self) -> None:
        doto = [_ for v, _ in self.__cases if v == self.value]
        self.__cases.clear()
        if doto != []:
            return forEach(doto, LPS.II)
        else:
            return [self.__default(self.value)]


class FunctionBuilder:
    class __Directives(Enum):
        BIND_FUNC = 0
        POST_ARG = 1
        POST_KWARG = 2
        POST_END = 3
        INVOKE_FUNC = 4

        GET_VAR = 5
        SAVE_VAR = 6
        BIND_VAR = 7

        END = -1

    _Directives = __Directives
    __func_directives: List[__Directives]
    __func_namespace: Dict[str, T]

    def __init__(self) -> None:
        self.__func_directives = [
            Args(),
        ]
        self.__func_namespace = {}

    def clearNameSpace(self) -> Self:
        self.__func_namespace.clear()
        return self

    def defArgs(self, *arg_names: str, **kwargs) -> Self:
        self.__func_directives[0] = Args(*arg_names, **kwargs)
        return self

    def saveVar(self, name: str) -> Self:
        self.__func_directives.extend([self.__Directives.SAVE_VAR, name])
        return self

    def getVar(self, name: str) -> Self:
        self.__func_directives.extend([self.__Directives.GET_VAR, name])
        return self

    def end(self) -> Callable:
        self.__func_directives.append(self.__Directives.END)
        return self.build()

    def bindVar(self, name: str, value: Optional[T] = None) -> Self:
        self.__func_directives.extend([self.__Directives.BIND_VAR, name, value])
        return self
    
    
    def bindFunc(self, func: Callable) -> Self:
        self.__func_directives.extend([self.__Directives.BIND_FUNC, func])
        return self

    def invokeFunc(self) -> Self:
        self.__func_directives.append(self.__Directives.INVOKE_FUNC)
        return self

    def postArgs(self) -> Self:
        self.__func_directives.append(self.__Directives.POST_ARG)
        return self

    def postKwarg(self, name: str) -> Self:
        self.__func_directives.extend([self.__Directives.POST_KWARG, name])
        return self

    def raw(self, v: T) -> Self:
        self.__func_directives.append(v)
        return self

    def endPost(self) -> Self:
        self.__func_directives.append(self.__Directives.POST_END)
        return self

    def build(self) -> Callable:
        def _wrap(*args, **kwargs) -> RT:
            __current: RT = None
            __current_func: Callable = None
            # Receive Args & store in namespace
            defargs: Args = self.__func_directives[0]
            for n, v in zip(defargs.args, args):
                self.__func_namespace.update({n: v})
            self.__func_namespace.update(defargs.kwargs)
            self.__func_namespace.update(kwargs)
            # Handle directives
            directives = iter(self.__func_directives[1:])
            _dit = next(directives)
            while _dit != self.__Directives.END:
                if _dit == self.__Directives.GET_VAR:
                    __current = self.__handleVarDirectives(_dit, directives)
                if _dit == self.__Directives.SAVE_VAR:
                    self.__func_namespace.update(
                        {
                            self.__handleVarDirectives(
                                next(directives), directives
                            ): __current
                        }
                    )
                if _dit == self.__Directives.BIND_VAR:
                    __current = self.__handleVarDirectives(_dit, directives)
                if _dit == self.__Directives.BIND_FUNC:
                    __current_func = next(directives)
                if _dit == self.__Directives.POST_ARG:
                    __current = next(directives)
                    rawarg = []
                    rawkwarg = {}
                    while __current != self.__Directives.POST_END:
                        if __current == self.__Directives.POST_KWARG:
                            rawkwarg.update(
                                {
                                    next(directives): self.__handleVarDirectives(
                                        next(directives), directives
                                    )
                                }
                            )
                        else:
                            rawarg.append(
                                self.__handleVarDirectives(__current, directives)
                            )
                        __current = next(directives)
                    __current = Args(*rawarg, **rawkwarg)
                if _dit == self.__Directives.INVOKE_FUNC:
                    if isinstance(__current, Args):
                        __current = __current_func(*__current.args, **__current.kwargs)
                    else:
                        __current = __current_func()
                _dit = next(directives)
            return __current

        return _wrap

    def __handleVarDirectives(self, dit, directives):
        if dit == self.__Directives.GET_VAR:
            key = next(directives)
            if key not in self.__func_namespace:
                raise NameError("name '%s' is not defined" % (key))
            return self.__func_namespace[key]
        elif dit == self.__Directives.BIND_VAR:
            name, val = next(directives), next(directives)
            self.__func_namespace.update({name: val})
            return val
        else:
            return dit

    @staticmethod
    def fromDirectives(*directives: Union[__Directives, T]) -> Callable:
        _ = FunctionBuilder()
        forEach(directives, _.raw)
        return _.build()

    @staticmethod
    def fromDirectiveBody(*directives: Union[__Directives, T]) -> Callable:
        _ = FunctionBuilder()
        _.raw(Args())
        forEach(directives, _.raw)
        return _.end()
