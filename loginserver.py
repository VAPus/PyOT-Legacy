import sys
sys.path.insert(0, '.')
sys.path.insert(1, 'game')

try:
    import config
except ImportError:
    print("You got no config.py file. Please make a file from config.py.dist")
    sys.exit()

#### Try Cython? ####
if config.tryCython:
    try:
        import pyximport
        pyximport.install(pyimport = True)
    except:
        pass # No cython / old cython

#### Import the tornado ####
from tornado.tcpserver import *
from tornado.ioloop import IOLoop
import tornado.gen
import time

try:
    import asyncio
    IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
except:
    pass # Asyncio not found. Ow well, not a crysis.
    
from service.loginserver import LoginFactory
loginServer= LoginFactory()
loginServer.bind(config.loginPort, config.loginInterface)
loginServer.start()

# Fix logging machinery.
IOLoop.instance().add_future(fut, lambda fut: fut.result())

# Start reactor. This will call the above.
IOLoop.instance().start()
            
