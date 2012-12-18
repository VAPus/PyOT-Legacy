from twisted.python import log
import sys, os, glob

protocolsAvailable = []
for path in glob.iglob('core/game/protocols/*.py'):
    version = path.split(os.sep)[-1].split('.', 1)[0]
    if not '_' in version and not '.' in version and not 'base' in version:
        protocolsAvailable.append(int(version))

protocolsUsed = {}

def getProtocol(version):
    if not protocolsUsed:
        loadProtocol(version)
    try:
        return protocolsUsed[version]
    except:
        log.msg("Protocol %d unsupported" % version)
    return None

def loadProtocol(version):
    if "_trial_temp" in os.getcwd():
        os.chdir("..")
        
    if not version in protocolsAvailable:
        log.msg("Protocol (Base) %d doesn't exist!" % version)
        return
        
    protocol = __import__('game.protocols.%d' % version, globals(), locals())
    protocol = sys.modules['game.protocols.%d' % version]
            
    protocol.verify()
    protocolsUsed[version] = protocol.Protocol()
    for x in protocol.provide:
        protocolsUsed[x] = protocolsUsed[version]
