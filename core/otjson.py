import config
try:
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
except:
    print "Failing to load the JSON module %s, faling back to default json" % config.jsonLibrary
    from json import dumps, loads