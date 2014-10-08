import config
import builtins
from tornado import gen
from collections import deque

connections = deque(maxlen=10)

if config.sqlModule == "mysql":
    @gen.coroutine
    def connect():
        import asynctorndb
        # Make connection pool.
        for x in range(10):
            conn = asynctorndb.Connect(user=config.sqlUsername, passwd=config.sqlPassword, database=config.sqlDatabase, no_delay = True, charset='utf8')
            connections.append(conn)
            yield conn.connect()
else:
    raise ImportError("Unsupported sqlModule!");

builtins.PYOT_RUN_SQLOPERATIONS = True

@gen.coroutine
def runOperation(*argc):
    # Get a connection.
    conn = None
    while not conn:
        conn = connections.popleft()
        if not conn:
            yield gen.Task(IOLoop.instance().add_timeout, time.time() + 0.05)
            
    yield conn.execute(*argc)
    
    # Put connection back
    connections.append(conn)

@gen.coroutine
def runQuery(*argc):
    # Get a connection.
    conn = None
    while not conn:
        conn = connections.popleft()
        if not conn:
            yield gen.Task(IOLoop.instance().add_timeout, time.time() + 0.05)

    res = (yield conn.query(*argc))
    
    # Put connection back
    connections.append(conn)
    
    return res

@gen.coroutine
def runOperationLastId(*argc):
    # Get a connection.
    conn = None
    while not conn:
        conn = connections.popleft()
        if not conn:
            yield gen.Task(IOLoop.instance().add_timeout, time.time() + 0.05)

    res = yield conn.execute_lastrowid(*argc)
    
    # Put connection back
    connections.append(conn)
    
    return res