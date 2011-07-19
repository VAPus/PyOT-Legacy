import config

if config.jsonLibrary == "ujson":
    from ujson import decode as loads
    from ujson import encode as dumps
elif config.jsonLibrary == "cjson":
    from cjson import decode as loads
    from cjson import encode as dumps
elif config.jsonLibrary == "simplejson":
    from simplejson import dumps, loads
else:
    from json import dumps, loads
