try:
    import noneprompt
    from noneprompt import prompts, utils
    from prompt_toolkit.styles import Style

    from . import prompts_extension
    
    
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
    
    __all__ = [
        noneprompt,
        prompts,
        prompts_extension,
        utils,
        "default_style",
    ]
    
    
    
except:
    __all__ = []
