try:
    import noneprompt
    from noneprompt import prompts,utils
    from prompt_toolkit.styles import Style

    default_style = Style.from_dict(
        {
            "questionmark": "fg:#673AB7 bold",
            "question": "",
            "sign": "",
            "unsign": "",
            "selected": "",
            "pointer": "bold",
            "annotation": "",
            "answer": "bold",
        }
    )
    
    from . import prompts_extension
except:
    pass
'''
A lib adopted from nb-cli by H2Sxxa

Original Project: https://github.com/nonebot/nb-cli
Original License: https://github.com/nonebot/nb-cli/blob/master/LICENSE (MIT LICENSE)
'''
__all__=[
    "noneprompt",
    "prompts",
    "prompts_extension",
    "utils",
    "default_style",
]