# This is a shadow of 9.7
#import base
from struct import pack

base = sys.modules["game.protocols.970"]

provide = [981]

def verify(): return True


class Packet(base.Packet):
    def speed(self, speed):
        self.uint16((speed - 49) // 2)
      
class Protocol(base.Protocol):
    Packet = Packet
