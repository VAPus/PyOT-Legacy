# This is a shadow of the main branch, 9.51
import base

provide = [950]

def vertify(): return True


class Packet(base.BasePacket):
    maxOutfits = 31
    maxMounts = 27
	
class Protocol(base.BaseProtocol):
    Packet = Packet