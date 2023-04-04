from typing import Optional, Union
from prompt_toolkit import Application
from ..prompts import DT, RT, BasePrompt, CanceledError, DisableColorTransformation, NoAnswer
from ....lite.v2.ClassMixin import Mixin,NameTransform
from prompt_toolkit.styles import Style

from asyncio import get_event_loop
def MakeAsync():
    @Mixin(BasePrompt)
    class Mixinto:
        @NameTransform("_build_application")
        async def mixin_build_application(self, no_ansi: bool, style: Style) -> Application:
            return await Application(
                layout=self._build_layout(),
                style=self._build_style(style),
                style_transformation=DisableColorTransformation(no_ansi),
                key_bindings=self._build_keybindings(),
                mouse_support=True,
            ).run_async()
            
        async def prompt(
            self,
            default: DT = None,
            no_ansi: bool = False,
            style: Optional[Style] = None,
        ) -> Union[DT, RT]:
            app = await self._build_application(no_ansi=no_ansi, style=style or Style([]))
            result: RT = await app.run()
            if result is NoAnswer:
                if default is None:
                    raise CanceledError("No answer selected!")
                return default
            else:
                return result
    return Mixinto