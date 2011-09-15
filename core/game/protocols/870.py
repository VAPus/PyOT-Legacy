# This is a shadow of the main branch, 9.1
import base, sys

p860 = sys.modules["game.protocols.860"]
provide = []

def vertify(): return True

class Packet(base.BasePacket):
    maxOutfits = 25

    # Couple of things from 8.6
    item = p860.Packet.item
    tileDescription = p860.Packet.tileDescription
    creature = p860.Packet.creature
    skills = p860.Packet.skills

    def status(self, player):
        print "860"
        self.uint8(0xA0)
        self.uint16(player.data["health"])
        self.uint16(player.data["healthmax"])
        self.uint32(player.data["capasity"] - player.inventoryWeight) # TODO: Free Capasity
        #self.uint32(player.data["capasity"] * 100) # TODO: Cap
        self.uint64(player.data["experience"]) # TODO: Virtual cap? Experience
            
        if player.data["level"] > 0xFFFF:
            self.uint16(0xFFFF)
        else:
            self.uint16(player.data["level"]) # TODO: Virtual cap? Level
            
        self.uint8(math.ceil(float(config.levelFormula(player.data["level"]+1)) / player.data["experience"])) # % to next level, TODO
        self.uint16(player.data["mana"]) # mana
        self.uint16(player.data["manamax"]) # mana max
        self.uint8(player.data["maglevel"]) # TODO: Virtual cap? Manalevel
        #self.uint8(1) # TODO: Virtual cap? ManaBase
        self.uint8(0) # % to next level, TODO
        self.uint8(player.data["soul"]) # TODO: Virtual cap? Soul
        self.uint16(min(42 * 60, player.data["stamina"] / 60)) # Stamina minutes
        #self.uint16(player.speed) # Speed
        
        #self.uint16(0x00) # Condition
        
class Protocol(base.BaseProtocol): pass
