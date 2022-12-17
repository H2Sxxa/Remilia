from . import (
    lite,
    utils,
    base,
    jsondb,
)

__all__=[
    "lite",
    "utils",
    "base",
    "jsondb",
]

#__VERSION__#

def __REQUIREMENTS__():
    '''
## if you want to use some class in our lib,you must install the lib below
### utils/cli
- #### click >= 8.0
- #### prompt_toolkit >= 3.0.31

### utils/net/pixiv
- #### pixivpy_async >= 1.2.14
    '''
    info="".join(__import__("inspect").getsourcelines(__REQUIREMENTS__)[0][2:-4])
    print(info)
    return info

