# This is a shadow of the main branch, 9.50
import base

provide = []

def vertify(): return True


class Packet(base.BasePacket):
    maxOutfits = 31
    maxMounts = 27
	
class Protocol(base.BaseProtocol):
    Packet = Packet