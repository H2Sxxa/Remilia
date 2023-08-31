from abc import ABC, abstractmethod
import ctypes
from functools import partial
from typing import TYPE_CHECKING, Any, Dict, Optional, Type
from typing_extensions import Self

from Remilia.base.typings import NT, T, RT, VT
from Remilia.fancy import toInstance, redirectTo


if TYPE_CHECKING:

    class _InvokeAPIMethod:
        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            pass


class PyObject(ctypes.Structure):
    """
    ```c
    typedef struct _object {
        _PyObject_HEAD_EXTRA //not need to impl, when under non-debug
        Py_ssize_t ob_refcnt;
        PyTypeObject *ob_type;
    } PyObject;
    ```
    """

    class PyType(ctypes.Structure):
        pass

    ssize = ctypes.c_int64 if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_int32
    _fields_ = [
        ("ob_refcnt", ssize),
        ("ob_type", ctypes.POINTER(PyType)),
    ]


class AddressConventer:
    def __init__(self, obj: Optional[T] = None, address: Optional[int] = -1):
        self.address = id(obj) if obj is not None else address

    def castPy(self, pytype: Type[T], isbasic: bool = False) -> T:
        v = ctypes.cast(self.address, ctypes.py_object).value
        return pytype(v) if isbasic else v

    def castPyobj(self) -> "ctypes._CastT":
        return ctypes.cast(self.address, ctypes.py_object)

    def castPyPointer(self):
        return ctypes.cast(self.address, ctypes.POINTER(ctypes.py_object))

    def castC(self, ctype: "ctypes._CData") -> RT:
        return ctypes.cast(self.address, ctype)

    def castCPointer(self, ctype: "ctypes._CData"):
        return ctypes.cast(self.address, ctypes.POINTER(ctype))

    @staticmethod
    def from_address(address: int):
        return AddressConventer(address=address)

    @staticmethod
    def from_object(obj: T):
        return AddressConventer(obj=obj)


def toPyObj(val: T) -> ctypes.py_object:
    return ctypes.py_object(val)


class _InvokeApi(ABC):
    @abstractmethod
    def _invoke(self, name: str, *args, **kwargs):
        ...

    def __getattr__(self, name: str) -> "_InvokeAPIMethod":
        return partial(self._invoke, name)


class DLLApiBase(_InvokeApi):
    @property
    def APIType(self) -> Type[Self]:
        return self.__class__


@toInstance
class CPyAPI(DLLApiBase):
    """
    { @link https://docs.python.org/zh-cn/3.11/c-api/index.html }
    """

    def _invoke(self, name: str, *args, **kwargs):
        super()._invoke(name, *args, **kwargs)
        return ctypes.pythonapi.__getattr__(name)(*args, **kwargs)

    @redirectTo(ctypes.pythonapi.PyDict_SetItem)
    def PyDict_SetItem(
        self,
        __object: ctypes.py_object,
        __key: ctypes.py_object,
        __val: ctypes.py_object,
    ) -> int:
        ...

    @redirectTo(ctypes.pythonapi.PyDict_DelItem)
    def PyDict_DelItem(
        self, __object: ctypes.py_object, __key: ctypes.py_object
    ) -> int:
        ...

    @redirectTo(ctypes.pythonapi.PyDict_Contains)
    def PyDict_Contains(
        self, __object: ctypes.py_object, __key: ctypes.py_object
    ) -> int:
        ...

    @redirectTo(ctypes.pythonapi.PyDict_GetItem)
    def PyDict_GetItem(
        self, __object: ctypes.py_object, __key: ctypes.py_object
    ) -> int:
        ...


@toInstance
class PyAPI(CPyAPI.APIType):
    """
    The class's some method accepts Python type, you don't need to convert them. { @link CPyAPI }
    """

    def PyDict_SetItem(self, __object: Dict[NT, VT], __key: NT, __val: VT) -> None:
        super().PyDict_SetItem(toPyObj(__object), toPyObj(__key), toPyObj(__val))

    def PyDict_Contains(self, __object: Dict[NT, VT], __key: NT) -> bool:
        return bool(super().PyDict_Contains(toPyObj(__object), toPyObj(__key)))

    def PyDict_DelItem(self, __object: Dict[NT, VT], __key: NT) -> None:
        super().PyDict_DelItem(toPyObj(__object), toPyObj(__key))

    def PyDict_GetItem(self, __object: Dict[NT, VT], __key: NT) -> int:
        """
        return Borrowed reference
        """
        return super().PyDict_GetItem(toPyObj(__object), toPyObj(__key))
