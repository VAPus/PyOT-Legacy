# This is a shadow of the main branch, 9.1
import base

provide = []
compatible_protocols = [860, 861, 862]

def vertify(): return True

class Packet(base.BasePacket): pass
class Protocol(base.BaseProtocol): pass
