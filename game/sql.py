import config
import builtins
from tornado import gen, ioloop
from collections import deque
import random

connections = deque(maxlen=10)
builtins.PYOT_RUN_SQLOPERATIONS = True
if config.sqlModule == "mysql":
    @gen.coroutine
    def connect():
        if PYOT_RUN_SQLOPERATIONS:
            import asynctorndb
            # Try one connection first.
            conn = asynctorndb.Connect(host = config.sqlHost, user=config.sqlUsername, passwd=config.sqlPassword, database=config.sqlDatabase, no_delay = True, charset='utf8')
            spawn = config.sqlConnections
            future = conn.connect()
            try:
                yield future
            except:
                pass

            if future.exception():
                print("SQL Connection to localhost failed, trying 127.0.0.1")
                if config.sqlHost == "localhost":
                    config.sqlHost = "127.0.0.1"
                    print("SQL Connection with localhost failed, trying 127.0.0.1")
            else:
                spawn -= 1
                connections.append(conn)


            # Make connection pool.
            for x in range(spawn):
                conn = asynctorndb.Connect(host = config.sqlHost, user=config.sqlUsername, passwd=config.sqlPassword, database=config.sqlDatabase, no_delay = True, charset='utf8')
                
                future = conn.connect()
                try:
                    yield future
                except:
                    pass

                if future.exception():
                    print("SQL Connection failed", sql.exception(), "check settings")
                    sys.exit()
                else:
                    connections.append(conn)

else:
    raise ImportError("Unsupported sqlModule!");



def runOperation(*argc):
    ioloop.IOLoop.instance().add_callback(_runOperation, *argc)

@gen.coroutine
def _runOperation(*argc):
    if PYOT_RUN_SQLOPERATIONS:
        # Get a connection.
        conn = None
        while not conn:
            try:
                conn = connections.popleft()
            except:
                conn = None

            if not conn:
                yield gen.Task(IOLoop.instance().add_timeout, time.time() + 0.05)
                
        future = conn.execute(*argc)
        try:
            yield future 
        except:
            pass

        exc = future.exc_info()
        if exc:
            print(exc[0].__name__, exc[1], 'from query:', argc[0])
            
        # Put connection back
        connections.append(conn)

@gen.coroutine
def runQuery(*argc):
    if PYOT_RUN_SQLOPERATIONS:
        # Get a connection.
        conn = None
        while not conn:
            try:
                conn = connections.popleft()
            except:
                conn = None

            if not conn:
                yield gen.Task(IOLoop.instance().add_timeout, time.time() + 0.05)

        future = conn.query(*argc)
        try:
            res = yield future
        except:
            res = None

        exc = future.exc_info()
        if exc:
            print(exc[0].__class__.__name__, exc[1], 'from query:', argc[0])
        exc = future.exception()
        
     
        
        # Put connection back
        connections.append(conn)
        
        return res
    return {}

@gen.coroutine
def runOperationLastId(*argc):
    if PYOT_RUN_SQLOPERATIONS:
        # Get a connection.
        conn = None
        while not conn:
            try:
                conn = connections.popleft()
            except:
                conn = None

            if not conn:
                yield gen.Task(IOLoop.instance().add_timeout, time.time() + 0.05)

        future = conn.execute_lastrowid(*argc)
        
        try:
            res = yield future
        except:
            res = None
        exc = future.exc_info()
        if exc:
            print(exc[0].__class__.__name__, exc[1], 'from query:', argc[0])
        # Put connection back
        connections.append(conn)
        
        return res
    return random.randint(1, 10000)
