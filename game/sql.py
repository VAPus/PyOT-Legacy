#XXX Port this.
#from twisted.enterprise import adbapi
#from twisted.internet.defer import inlineCallbacks
import config
import builtins
from tornado import gen
if config.sqlModule == "tormysql":
    import tormysql
    pool = tormysql.ConnectionPool(max_connections = 80,
    host = config.sqlHost,
    user = config.sqlUsername,
    passwd = config.sqlPassword,
    db = config.sqlDatabase,
    no_delay = True,
    charset = "utf8",
    cursorclass = tormysql.cursor.DictCursor # XXX: best would be to use SSDictCursor. This require us to kill fetchall tho.
    )
else:
    raise ImportError("Unsupported sqlModule!");
    
from tornado.ioloop import IOLoop

builtins.PYOT_RUN_SQLOPERATIONS = True

@gen.coroutine
def runOperation(*argc, **kwargs):
    """ Like runQuery, except no fetching, or returning. """
    conn = yield pool.Connection()
    cursor = conn.cursor()
    stat = yield cursor.execute(*argc, **kwargs)

    #data = cursor.fetchall()
    
    # XXX: Not sure we should do these things....
    yield cursor.close()
    conn.close()

    #return data
    
@gen.coroutine
def runQuery(*argc, **kwargs):
    conn = yield pool.Connection()
    cursor = conn.cursor()

    stat = yield cursor.execute(*argc, **kwargs)
    
    data = cursor.fetchall()
    
    # XXX: Not sure we should do these things....
    yield cursor.close()
    conn.close()

    return data
    
# A custom call we got. Not in the twisted standard.
@gen.coroutine
def runOperationLastId(*argc, **kwargs):
    conn = yield pool.Connection()
    cursor = conn.cursor()
    yield cursor.execute(*argc, **kwargs)
    lastId = cursor.lastrowid
    
    # XXX: Not sure we should do these things....
    yield cursor.close()
    conn.close()

    return lastid
    
