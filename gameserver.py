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
from service.gameserver import GameFactory
import time
import game.loading
try:
    import asyncio
    IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
except:
    pass # Asyncio not found. Ow well, not a crysis.
    
startTime = time.time()
# Game Server
gameServer = GameFactory()
gameServer.bind(config.gamePort, config.gameInterface)
gameServer.start()

# (optionally) buildt in login server.
if config.letGameServerRunTheLoginServer:
    from service.loginserver import LoginFactory
    loginServer= LoginFactory()
    loginServer.bind(config.loginPort, config.loginInterface)
    loginServer.start()
    
# (optional) built in extension server.
# XXX Port later or kill?
#if config.enableExtensionProtocol:
#    from service.extserver import ExtFactory
#    extFactory = ExtFactory()
#    tcpService = internet.TCPServer(config.loginPort + 10000, extFactory, interface=config.loginInterface)
#    tcpService.setServiceParent(topService)

# (optional) built in extension server.
# XXX: Port later...
#if config.enableExtensionProtocol:
#    from service.webserver import WebFactory, Web
#    webFactory = WebFactory(Web())
#    tcpService = internet.TCPServer(config.webPort, webFactory, interface=config.webInterface)
#    tcpService.setServiceParent(topService)

# Load the core stuff!
IOLoop.instance().add_callback(game.loading.loader, startTime)

# Start reactor. This will call the above.
IOLoop.instance().start()
            
