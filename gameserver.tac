#!/usr/bin/env python

import config
import sys

#### Setup Reactor ####
if config.reactorStyle is "poll":
    from twisted.internet import pollreactor
    pollreactor.install()

elif config.reactorStyle is "epoll" or (sys.platform == "linux2" and config.reactorStyle is "default"):
    from twisted.internet import epollreactor
    epollreactor.install()

elif config.reactorStyle is "kqueue" or (sys.platform.find("freebsd") and config.reactorStyle is "default"):
    from twisted.internet import kqreactor
    kqreactor.install()

elif config.reactorStyle is "iocp" or (sys.platform == "win32" and config.reactorStyle is "default"):
    from twisted.internet import iocpreactor
    iocpreactor.install()

else: # This is the default reactor, "select"
    from twisted.internet import selectreactor
    selectreactor.install()

from twisted.internet import reactor

#### Suggest reactor thread pool size ####
reactor.suggestThreadPoolSize(config.suggestedGameServerThreadPoolSize)

#### Initialize OTCrypto module ####
import core.otcrypto
core.otcrypto.setkeys(config.RSAKeys["n"], config.RSAKeys["e"], config.RSAKeys["d"], config.RSAKeys["p"], config.RSAKeys["q"])

#### Import the LoginServer ####
from twisted.application import internet, service
from core.service.gameserver import GameProtocol, GameFactory, GameService
import time

startTime = time.time()
topService = service.MultiService()

GameServiceInstance = GameService()
GameServiceInstance.setServiceParent(topService)

factory = GameFactory(GameServiceInstance)
tcpService = internet.TCPServer(config.gamePort, factory, interface=config.gameInterface)
tcpService.setServiceParent(topService)

application = service.Application("pyot-game-server")

topService.setServiceParent(application)

# Load the core stuff!
# Note, we use 0 here so we don't begin to load stuff before the reactor is free to do so, SQL require it, and anyway the logs will get fucked up a bit if we don't
import core.game.game
reactor.callLater(0, core.game.game.loader, startTime)