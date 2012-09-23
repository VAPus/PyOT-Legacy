from twisted.enterprise import adbapi
from twisted.internet.defer import inlineCallbacks
import config

def connect(module = config.sqlModule):
    if module == "MySQLdb":
        if config.sqlSocket:
            return adbapi.ConnectionPool(module, host=config.sqlHost, unix_socket=config.sqlSocket, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug)
        else:
            return adbapi.ConnectionPool(module, host=config.sqlHost, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug)
    elif module == "mysql-ctypes":
        return adbapi.ConnectionPool("MySQLdb", host=config.sqlHost, port=3306, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug)

    elif module == "oursql":
        try:
            import oursql
        except ImportError:
            print "Falling oursql back to MySQLdb"
            return connect("MySQLdb")

        if config.sqlSocket:
            return adbapi.ConnectionPool(module, host=config.sqlHost, unix_socket=config.sqlSocket, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug)
        else:
            return adbapi.ConnectionPool(module, host=config.sqlHost, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug)

    elif module == "pymysql": # This module is indentical, but uses a diffrent name
        try:
            import pymysql
        except ImportError:
            print "Falling pymysql back to MySQLdb"
            return connect("MySQLdb")          

        if config.sqlSocket:
            return adbapi.ConnectionPool(module, host=config.sqlHost, unix_socket=config.sqlSocket, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug)
        else:
            return adbapi.ConnectionPool(module, host=config.sqlHost, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cp_reconnect=True, cp_noisy=config.sqlDebug)
    elif module == "sqlite3":
        import sqlite3

        # Implode our little hack to allow both sqlite3 and mysql to work together!
        # This is a bit slower I guess, but it works :)
        def runQuery(self, *args, **kw):
            args = list(args)
            args[0] = args[0].replace('%s', '?').replace('%f', '?').replace('%d', '?') # String, float and digit support
            args = tuple(args)
            return self.runInteraction(self._runQuery, *args)
        adbapi.ConnectionPool.runQuery = runQuery

        return adbapi.ConnectionPool(module, config.sqlDatabase, isolation_level=None, check_same_thread=False)

    else:
        raise NameError("SQL module %s is invalid" % module)
# Setup the database pool when this module is imported for the first time
conn = connect()

@inlineCallbacks
def runOperation(*argc, **kwargs):
    yield conn.runOperation(*argc, **kwargs)
    
@inlineCallbacks
def runQuery(*argc, **kwargs):
    yield conn.runQuery(*argc, **kwargs)