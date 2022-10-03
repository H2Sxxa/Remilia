try:
    from . import (
    LiteLog,
    LiteTasks,
    utils,
    )
except:
    pass

from cmath import inf
from . import (
    LiteMixin,
    LitePGL,
    LiteEvent,
    LiteConfig,
    LiteResource,
    LiteI18n,
    LiteThread,
    base,
    )

__all__=[
    "LiteLog",
    "LiteMixin",
    "LiteThread",
    "LitePGL",
    "LiteResource",
    "LiteTasks",
    "LiteEvent",
    "LiteConfig",
    "LiteI18n",
    "base",
    "utils",
    ]

#__VERSION__#

def __REQUIREMENTS__():
    '''
## if you want to use some class in our lib,you must install the lib below
### LiteTasks/LiteLog:
- #### colorama >= 0.4.5

### utils/cli
- #### click >= 8.0
- #### prompt_toolkit >= 3.0.31

### utils/net/pixiv
- #### pixivpy_async >= 1.2.14
    '''
    info="".join(__import__("inspect").getsourcelines(__REQUIREMENTS__)[0][2:-4])
    print(info)
    return info