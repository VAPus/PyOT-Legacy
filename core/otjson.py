import config

try:
    from ujson import decode as loads
    from ujson import encode as dumps
    from ujson import load
except:
    try:
        from cjson import decode as loads
        from cjson import encode as dumps
        def load(data):
            return loads(data.read())
    except:
        try:
            from simplejson import dumps, loads, load
        except:
            from json import dumps, loads, load
