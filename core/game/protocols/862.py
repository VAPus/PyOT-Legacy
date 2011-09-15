# This is a shadow of the main branch, 9.1
import sys

provide = []
compatible_protocols = [860, 861, 910]

def vertify(): return True

class Packet(sys.modules["game.protocols.861"].Packet):
    maxKnownCreatures = 1300
    

class Protocol(sys.modules["game.protocols.861"].Protocol): pass