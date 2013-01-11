# This is a shadow of the main branch, 9.1.
import sys

provide = []

def verify():
    return True
    
class Packet( sys.modules["game.protocols.854"].Packet ):

    def cancelTarget( self ):
        self.uint8( 0xA3 )
        self.uint32( 0 )
        
        
class Protocol( sys.modules["game.protocols.854"].Protocol ):
    Packet = Packet
