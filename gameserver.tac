import sys
sys.path.insert(0, '.')
sys.path.insert(1, 'core')

import config

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
    from twisted.internet import epollreactor
    epollreactor.install()

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

#### Initialize OTCrypto module ####
import otcrypto
otcrypto.setkeys(config.RSAKeys["n"], config.RSAKeys["e"], config.RSAKeys["d"], config.RSAKeys["p"], config.RSAKeys["q"])

#### Import the LoginServer ####
from twisted.application import internet, service
from service.gameserver import GameProtocol, GameFactory
import time
import game.engine

startTime = time.time()

application = service.Application("pyot-game-server")

factory = GameFactory()
tcpService = internet.TCPServer(config.gamePort, factory, interface=config.gameInterface)
tcpService.setServiceParent(application)

# Load the core stuff!
# Note, we use 0 here so we don't begin to load stuff before the reactor is free to do so, SQL require it, and anyway the logs will get fucked up a bit if we don't
reactor.callLater(0, game.engine.loader, startTime)

    
            
