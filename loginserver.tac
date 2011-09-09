import sys
sys.path.insert(0, '.')
sys.path.insert(1, 'core')

import config

#### Setup Reactor ####
if config.reactorStyle is "poll":
    from twisted.internet import pollreactor
    pollreactor.install()

elif config.reactorStyle is "epoll" or (sys.platform == "linux2" and config.reactorStyle is "default"):
    from twisted.internet import epollreactor
    epollreactor.install()

elif config.reactorStyle is "kqueue" or ('freebsd' in sys.platform and config.reactorStyle is "default"):
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
reactor.suggestThreadPoolSize(config.suggestedLoginServerThreadPoolSize)

### Override sql:
config.sqlMinConnections = 1
config.sqlMaxConnections = 2

#### Initialize OTCrypto module ####
import otcrypto
otcrypto.setkeys(config.RSAKeys["n"], config.RSAKeys["e"], config.RSAKeys["d"], config.RSAKeys["p"], config.RSAKeys["q"])

#### Import the LoginServer ####
from twisted.application import internet, service
from service.loginserver import LoginProtocol, LoginFactory

application = service.Application("pyot-login-server")

factory = LoginFactory()
tcpService = internet.TCPServer(config.loginPort, factory, interface=config.loginInterface)
tcpService.setServiceParent(application)


