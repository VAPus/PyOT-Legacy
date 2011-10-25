from twisted.enterprise import adbapi
import config

def connect(module = config.sqlModule):
    if module == "MySQLdb":
        from MySQLdb.cursors import DictCursor
        from MySQLdb.constants import FIELD_TYPE
        import MySQLdb.converters
        
        def autoFloat(s):
            return float(s) if '.' in s else int(s)

        MySQLdb.converters.conversions[FIELD_TYPE.LONG] = int
        MySQLdb.converters.conversions[FIELD_TYPE.DECIMAL] = autoFloat
        MySQLdb.converters.conversions[FIELD_TYPE.NEWDECIMAL] = autoFloat
        
        return adbapi.ConnectionPool(module, host=config.sqlHost, unix_socket=config.sqlSocket, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cursorclass=DictCursor, conv=MySQLdb.converters.conversions)

    elif module == "oursql":
        try:
            import oursql
        except:
            print "Falling oursql back to MySQLdb"
            return connect("MySQLdb")
        
        return adbapi.ConnectionPool(module, host=config.sqlHost, unix_socket=config.sqlSocket, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, default_cursor=oursql.DictCursor)

    elif module == "pymysql": # This module is indentical, but uses a diffrent name
        try:
            from pymysql.cursors import DictCursor
            from pymysql.constants import FIELD_TYPE
            import pymysql.converters
        except:
            print "Falling pymysql back to MySQLdb"
            return connect("MySQLdb")          
              
        def autoFloat(s):
            return float(s) if '.' in s else int(s)

        pymysql.converters.conversions[FIELD_TYPE.LONG] = int
        pymysql.converters.conversions[FIELD_TYPE.DECIMAL] = autoFloat
        pymysql.converters.conversions[FIELD_TYPE.NEWDECIMAL] = autoFloat
        
        return adbapi.ConnectionPool(module, host=config.sqlHost, unix_socket=config.sqlSocket, db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cursorclass=DictCursor, conv=pymysql.converters.conversions)

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
        
        def fixer(conn):
            conn.row_factory = sqlite3.Row
        return adbapi.ConnectionPool(module, config.sqlDatabase, isolation_level=None, cp_openfun=fixer, check_same_thread=False)
        
    else:
        raise NameError("SQL module %s is invalid" % module)
# Setup the database pool when this module is imported for the first time
conn = connect()
