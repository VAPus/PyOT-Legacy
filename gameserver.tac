import sys
sys.path.insert(0, '.')
sys.path.insert(1, 'game')

try:
    import config
except ImportError:
    print "You got no config.py file. Please make a file from config.py.dist"
    sys.exit()

#### Use psyco? ####
if config.tryPsyco:
    try:
        import psyco
        psyco.full(0)
    except:
        pass # No psyco / 64-bit

#### Try Cython? ####
if config.tryCython:
    try:
        import pyximport
        pyximport.install(pyimport = True)
    except:
        pass # No cython / old cython

#### Setup Reactor ####
if config.reactorStyle == "poll":
    from twisted.internet import pollreactor
    pollreactor.install()

elif config.reactorStyle == "epoll" or (sys.platform == "linux2" and config.reactorStyle == "default"):
    try:
        from twisted.internet import epollreactor
        epollreactor.install()
    except:
        print "EPoll reactor not found"

elif config.reactorStyle == "kqueue" or ('freebsd' in sys.platform and config.reactorStyle == "default"):
    from twisted.internet import kqreactor
    kqreactor.install()

elif config.reactorStyle == "iocp" or (sys.platform == "win32" and config.reactorStyle == "default"):
    from twisted.internet import iocpreactor
    iocpreactor.install()

else: # This is the default reactor, "select"
    from twisted.internet import selectreactor
    selectreactor.install()

from twisted.internet import reactor


#### Suggest reactor thread pool size ####
reactor.suggestThreadPoolSize(config.suggestedGameServerThreadPoolSize)

#### Import the LoginServer ####
from twisted.application import internet, service
from service.gameserver import GameFactory
import time
import game.loading

startTime = time.time()

# Top level service demon
topService = service.MultiService()

# Application level.
application = service.Application("pyot-game-server")
topService.setServiceParent(application)

# Game Server
gameFactory = GameFactory()
gameServer = internet.TCPServer(config.gamePort, gameFactory, interface=config.gameInterface)
gameServer.setServiceParent(topService)

# (optionally) buildt in login server.
if config.letGameServerRunTheLoginServer:
    from service.loginserver import LoginFactory
    loginFactory = LoginFactory()
    tcpService = internet.TCPServer(config.loginPort, loginFactory, interface=config.loginInterface)
    tcpService.setServiceParent(topService)

# (optional) built in extension server.
if config.enableExtensionProtocol:
    from service.extserver import ExtFactory
    extFactory = ExtFactory()
    tcpService = internet.TCPServer(config.loginPort + 10000, extFactory, interface=config.loginInterface)
    tcpService.setServiceParent(topService)

# (optional) built in extension server.
if config.enableExtensionProtocol:
    from service.webserver import WebFactory, Web
    webFactory = WebFactory(Web())
    tcpService = internet.TCPServer(config.webPort, webFactory, interface=config.webInterface)
    tcpService.setServiceParent(topService)

# Load the core stuff!
# Note, we use 0 here so we don't begin to load stuff before the reactor is free to do so, SQL require it, and anyway the logs will get fucked up a bit if we don't
reactor.callLater(0, game.loading.loader, startTime)

    
            
