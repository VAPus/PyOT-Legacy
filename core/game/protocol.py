from twisted.python import log
import sys, os, glob

protocolsAvailable = []
for path in glob.iglob('core/game/protocols/*.py'):
    version = path.split(os.sep)[-1].split('.', 1)[0]
    if not '_' in version and not '.' in version and not 'base' in version:
        try:
            protocolsAvailable.append(int(version))
        except:
            protocolsAvailable.append(version)
protocolsUsed = {}

def getProtocol(version):
    if not version in protocolsUsed:
        loadProtocol(version)
    
    protocol = protocolsUsed[version]
    if not protocol:
        log.msg("Protocol %d unsupported" % version)
    return protocol

def loadProtocol(version):
    if "_trial_temp" in os.getcwd():
        os.chdir("..")
        
    if not version in protocolsAvailable:
        log.msg("Protocol (Base) %d doesn't exist!" % version)
        return
        
    protocol = __import__('game.protocols.%s' % version, globals(), locals())
    protocol = sys.modules['game.protocols.%s' % version]
            
    protocol.verify()
    protocolsUsed[version] = protocol.Protocol()
    for x in protocol.provide:
        protocolsUsed[x] = protocolsUsed[version]
