from . import (
    utils,
    base,
    mixin,
    mixin_decorations,
)

__all__=[
    "utils",
    "base",
    "mixin",
    "mixin_decorations",
]

#__VERSION__#

def __REQUIREMENTS__():
    '''
## if you want to use some class in our lib,you must install the lib below
### utils/cli
- #### noneprompt

### utils/net/pixiv
- #### pixivpy_async >= 1.2.14
    '''
    info="".join(__import__("inspect").getsourcelines(__REQUIREMENTS__)[0][2:-4])
    print(info)
    return info

