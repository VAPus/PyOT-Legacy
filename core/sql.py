from twisted.enterprise import adbapi
import config

# Bad: MYSQL bound
from MySQLdb.cursors import DictCursor
# TODO: Fix compatibility!
def connect():
    return adbapi.ConnectionPool(config.sqlModule, host="localhost",db=config.sqlDatabase, user=config.sqlUsername, passwd=config.sqlPassword, cp_min=config.sqlMinConnections, cp_max=config.sqlMaxConnections, cursorclass=DictCursor)

# Setup the database pool when this module is imported for the first time
conn = connect()
