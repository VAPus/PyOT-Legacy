from twisted.enterprise import adbapi
import config

def connect():
    if config.sqlModule is "MySQLdb":
        from MySQLdb.cursors import DictCursor
        return adbapi.ConnectionPool(config.sqlModule, host="localhost",db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cursorclass=DictCursor)
    elif config.sqlModule is "sqlite3":
        import sqlite3
        return adbapi.ConnectionPool(config.sqlModule, database=config.sqlDatabase, check_same_thread=False, detect_types=sqlite3.PARSE_COLNAMES)
# Setup the database pool when this module is imported for the first time
conn = connect()
