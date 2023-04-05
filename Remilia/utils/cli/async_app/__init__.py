from typing import Optional, Union
from prompt_toolkit.styles import Style

from ..prompts import DT, RT, BasePrompt, CanceledError, NoAnswer
from ....lite.v2.ClassMixin import Mixin

def MakeAsync():
    @Mixin(BasePrompt)
    class Mixinto:
        async def prompt(
            self,
            default: DT = None,
            no_ansi: bool = False,
            style: Optional[Style] = None,
        ) -> Union[DT, RT]:
            app = self._build_application(no_ansi=no_ansi, style=style or Style([]))
            result: RT = await app.run_async()
            if result is NoAnswer:
                if default is None:
                    raise CanceledError("No answer selected!")
                return default
            else:
                return result
    return Mixinto