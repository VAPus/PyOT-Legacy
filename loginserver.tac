import sys
sys.path.insert(0, '.')
sys.path.insert(1, 'core')

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

#### Import the LoginServer ####
from twisted.application import internet, service
from service.loginserver import LoginFactory

application = service.Application("pyot-login-server")

factory = LoginFactory()
tcpService = internet.TCPServer(config.loginPort, factory, interface=config.loginInterface)
tcpService.setServiceParent(application)


