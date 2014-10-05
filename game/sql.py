#XXX Port this.
#from twisted.enterprise import adbapi
#from twisted.internet.defer import inlineCallbacks
import config
import builtins
from tornado.ioloop import IOLoop
"""
builtins.PYOT_RUN_SQLOPERATIONS = True
# Our own methods.
def runOperationLastId(self, *args, **kw):
    if PYOT_RUN_SQLOPERATIONS:
        return self.runInteraction(self._runOperationLastId, *args, **kw)
    return random.randint(1, 1000)

def _runOperationLastId(self, trans, *args, **kw):
    trans.execute(*args, **kw)
    return trans.lastrowid

# Patch adbapi.ConnectionPool
adbapi.ConnectionPool._runOperationLastId = _runOperationLastId
adbapi.ConnectionPool.runOperationLastId = runOperationLastId
"""
# Connection function.
def connect(module = config.sqlModule):
    if module == "MySQLdb":
        import MySQLdb.cursors
        conv = None
        try:
            from MySQLdb.converters import conversions
            from MySQLdb.constants import FIELD_TYPE
            
            # Patch.
            conv = conversions.copy()
            conv[FIELD_TYPE.LONG] = int # Get rid of the longs.
        except:
            pass # Moist / MysqlDB2 already do this.
            
        if config.sqlSocket:
            if conv:
                return adbapi.ConnectionPool(module, host=config.sqlHost, unix_socket=config.sqlSocket, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug, cursorclass=MySQLdb.cursors.DictCursor, conv=conv)
            else:
                return adbapi.ConnectionPool(module, host=config.sqlHost, unix_socket=config.sqlSocket, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug, cursorclass=MySQLdb.cursors.DictCursor)
        else:
            if conv:
                return adbapi.ConnectionPool(module, host=config.sqlHost, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug, cursorclass=MySQLdb.cursors.DictCursor, conv=conv)
            else:
                return adbapi.ConnectionPool(module, host=config.sqlHost, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug, cursorclass=MySQLdb.cursors.DictCursor)
    elif module == "mysql-ctypes":
        import MySQLdb.cursors
        return adbapi.ConnectionPool("MySQLdb", host=config.sqlHost, port=3306, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug, cursorclass=MySQLdb.cursors.DictCursor, conv=conv)

    elif module == "oursql":
        try:
            import oursql
        except ImportError:
            print("Falling oursql back to MySQLdb")
            return connect("MySQLdb")

        from MySQLdb.constants import FIELD_TYPE
        from MySQLdb.converters import conversions
        
        # Patch.
        conv = conversions.copy()
        conv[FIELD_TYPE.LONG] = int
        
        if config.sqlSocket:
            return adbapi.ConnectionPool(module, host=config.sqlHost, unix_socket=config.sqlSocket, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug, default_cursor=oursql.DictCursor)
        else:
            return adbapi.ConnectionPool(module, host=config.sqlHost, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug, default_cursor=oursql.DictCursor)

    elif module == "pymysql": # This module is indentical, but uses a diffrent name
        try:
            import pymysql
            import pymysql.cursors
        except ImportError:
            print("Falling pymysql back to MySQLdb")
            return connect("MySQLdb")          

        # XXX: Port.
        #if config.sqlSocket:
        #    return adbapi.ConnectionPool(module, host=config.sqlHost, unix_socket=config.sqlSocket, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug, cursorclass=pymysql.cursors.DictCursor)
        #else:
        #    return adbapi.ConnectionPool(module, host=config.sqlHost, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug, cursorclass=pymysql.cursors.DictCursor)
    elif module == "sqlite3":
        raise Exception("TODO: dictcursor for sqlite3 required!")
        import sqlite3

        # Implode our little hack to allow both sqlite3 and mysql to work together!
        # This is a bit slower I guess, but it works :)
        def runQuery(self, *args, **kw):
            args = list(args)
            args[0] = args[0].replace('%s', '?').replace('%f', '?').replace('%d', '?') # String, float and digit support
            args = tuple(args)
            return self.runInteraction(self._runQuery, *args)
        #adbapi.ConnectionPool.runQuery = runQuery

        #return adbapi.ConnectionPool(module, config.sqlDatabase, isolation_level=None, check_same_thread=False)

    else:
        raise NameError("SQL module %s is invalid" % module)
    
# Setup the database pool when this module is imported for the first time
conn = connect()

def runOperation(*argc, **kwargs):
    return conn.runOperation(*argc, **kwargs)
    
def runQuery(*argc, **kwargs):
    return conn.runQuery(*argc, **kwargs)
    
# A custom call we got. Not in the twisted standard.
def runOperationLastId(*argc, **kwargs):
    return conn.runOperationLastId(*argc, **kwargs)
    

# Update max_allowed_packet for MySQL.
def _():
    @gen.coroutine
    def x():
        d = yield runQuery("SHOW variables LIKE '%max_allowed_packet%';")
        if int(d[0]['Value']) < 128 * 1024 * 1024:
            print("""Warning: Set:
[mysqld]
max_allowed_packet = 128M
[client]
max_allowed_packet = 128M

in my.cnf (/etc/my.cnf or /etc/mysql/my.cnf on Linux, mysql install folder\\my.cnf on windows) and restart mysql and pyot is highly recommended!""")
    x()
IOLoop.instance().call_later(2, _)