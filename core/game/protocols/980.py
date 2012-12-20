# This is a shadow of 9.7
#import base
from struct import pack

base = sys.modules["game.protocols.970"]

provide = []

def verify(): return True


class Packet(base.Packet):
    pass
        
class Protocol(base.Protocol):
    Packet = Packet
