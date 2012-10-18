# This is a shadow of the main branch, 9.51
import base
from struct import pack

provide = []

def vertify(): return True


class Packet(base.BasePacket):
    maxOutfits = 33
    maxMounts = 31

    # Magic Effect
    def magicEffect(self, pos, type):
        self.data += pack("<BHHBB", 0x83, pos.x, pos.y, pos.z, type)
   
    # Shoot
    def shoot(self, fromPos, toPos, type):
        self.uint8(0x85)
        self.position(fromPos)
        self.position(toPos)
        self.uint16(type)
        
class Protocol(base.BaseProtocol):
    Packet = Packet