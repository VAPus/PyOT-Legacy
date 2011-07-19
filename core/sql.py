from twisted.enterprise import adbapi
import config

def connect():
    if config.sqlModule == "MySQLdb":
        from MySQLdb.cursors import DictCursor
        return adbapi.ConnectionPool(config.sqlModule, host="localhost",db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cursorclass=DictCursor)

    elif config.sqlModule == "sqlite3":
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
        return adbapi.ConnectionPool(config.sqlModule, config.sqlDatabase, isolation_level=None, cp_openfun=fixer, check_same_thread=False)
        
    else:
        raise NameError("SQL module %s is invalid" % config.sqlModule)
# Setup the database pool when this module is imported for the first time
conn = connect()
