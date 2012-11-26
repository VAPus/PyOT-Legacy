import config
# Not supported anymore, no object hook.
"""try:
        from ujson import decode as loads
        from ujson import encode as dumps
except:
    try:
        from cjson import decode as loads
        from cjson import encode as dumps
    except:"""

try:
    from simplejson import dumps, loads
except:
    from json import dumps, loads
