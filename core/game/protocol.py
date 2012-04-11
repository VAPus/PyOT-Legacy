from twisted.python import log
import sys

protocolsAvailable = (860, 861, 862, 870, 910, 920, 931, 940, 941, 942, 943, 944, 945, 946, 950, 951)
protocolsUsed = {}

def getProtocol(version):
    try:
        return protocolsUsed[version]
    except:
        log.msg("Protocol %d unsupported" % version)
    return None

def loadProtocol(version):
    if not version in protocolsAvailable:
        log.msg("Protocol (Base) %d doesn't exist!" % version)
        return
        
    protocol = __import__('game.protocols.%d' % version, globals(), locals())
    protocol = sys.modules['game.protocols.%d' % version]
            
    protocol.vertify()
    protocolsUsed[version] = protocol.Protocol()
    for x in protocol.provide:
        protocolsUsed[x] = protocolsUsed[version]