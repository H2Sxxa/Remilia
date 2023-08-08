from typing import Generic, TypeVar

RT=TypeVar("RT") #Return Type
T=TypeVar("T")
NT=TypeVar("NT")
VT=TypeVar("VT")

class PairType(Generic[NT,VT]):...