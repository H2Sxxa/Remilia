from typing import Dict
from Remilia.fancy import toInstance
from Remilia.utils.cli.prompts_extension.screen import ScreenBase


@toInstance
class GlobalRouter:
    __router_map: Dict[str, ScreenBase] = {}

    __current: ScreenBase = None

    def push(self, name: str):
        self.__current = self.__router_map[name].setParent(self.__current)
        self.__current.build()

    def back(self):
        self.__current.backto()
