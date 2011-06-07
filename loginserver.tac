#!/usr/bin/env python
import config

#### Setup Reactor ####
if config.reactorStyle is "poll":
    from twisted.internet import pollreactor
    pollreactor.install()

elif config.reactorStyle is "epoll":
    from twisted.internet import epollreactor
    epollreactor.install()

elif config.reactorStyle is "kqueue":
    from twisted.internet import kqreactor
    kqreactor.install()

elif config.reactorStyle is "iocp":
    from twisted.internet import iocpreactor
    iocpreactor.install()

else: # This is the default reactor, "select"
    from twisted.internet import selectreactor
    selectreactor.install()

from twisted.internet import reactor

#### Suggest reactor thread pool size ####
reactor.suggestThreadPoolSize(config.suggestedLoginServerThreadPoolSize)

#### Initialize OTCrypto module ####
import core.otcrypto
core.otcrypto.setkeys(config.RSAKeys["n"], config.RSAKeys["e"], config.RSAKeys["d"], config.RSAKeys["p"], config.RSAKeys["q"])

#### Import the LoginServer ####
from twisted.application import internet, service
from core.service.loginserver import LoginProtocol, LoginFactory, LoginService



topService = service.MultiService()

LoginServiceInstance = LoginService()
LoginServiceInstance.setServiceParent(topService)

factory = LoginFactory(LoginServiceInstance)
tcpService = internet.TCPServer(config.loginPort, factory, interface=config.loginInterface)
tcpService.setServiceParent(topService)

application = service.Application("pyot-login-server")

topService.setServiceParent(application)

