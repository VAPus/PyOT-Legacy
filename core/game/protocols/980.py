# This is a shadow of 9.7
#import base
from struct import pack

base = sys.modules["game.protocols.970"]

provide = [981]

def verify(): return True


class Packet(base.Packet):
    maxOutfits = 34
    maxMounts = 32

    def speed(self, speed):
        self.uint16((speed - 49) // 2)

    def money(self, money):
        self.uint64(min(0xFFFFFFFFFFFFFFFE, money))

    def initialPacket(self, clientId, position):
        self.uint8(0x0A)
        self.uint8(0x17)
        self.uint32(clientId) # Cid
        self.uint16(1) # Drawing delay.

        # New speed formula thingy.
        self.double(857.36)
        self.double(261.29)
        self.double(-4795.01)

        self.uint8(1) # Rule violations?
      
class Protocol(base.Protocol):
    Packet = Packet
