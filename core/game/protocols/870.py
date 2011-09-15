# This is a shadow of the main branch, 9.1
import base, sys
import math
import game.enum
import game.item

p860 = sys.modules["game.protocols.860"]
provide = []

def vertify(): return True

class Packet(base.BasePacket):
    maxOutfits = 25

    # Couple of things from 8.6
    def item(self, item, count=None):
        import game.item
        if isinstance(item, game.item.Item):
            cid = item.cid
            if cid > 11703:
                if item.solid:
                    self.uint16(100)
                elif item.pickable and item.movable:
                    if item.containerSize:
                        self.uint16(1987)
                    elif item.weaponType:
                        self.uint16(3264)
                    elif item.usable:
                        self.uint16(110)
                    else:
                        self.uint16(1780)
                else:
                    self.uint16(104)
                    
            else:    
                self.uint16(item.cid)

                if item.stackable:
                    self.uint8(item.count or 1)
                elif item.type == 11 or item.type == 12:
                    self.uint8(item.fluidSource or 0)
                """if item.animation:
                    self.uint8(0xFE)""" # No animations in 8.6
            
        else:
            print item
            self.uint16(item)
            if count:
                self.uint8(count)
    
    def tileDescription(self, tile, player=None):
        # self.uint16(0x00) No animations!
        print "8.6 tile description called"
        isSolid = False
        for item in tile.topItems():
            if item.solid:
                isSolid = True
                
            self.item(item)
        
        if not isSolid:
            for creature in tile.creatures():
                if creature == None:
                    del creature
                    continue
                
                known = False
                removeKnown = 0
                if player:
                    known = creature in player.knownCreatures
                    
                    if not known:
                        if len(player.knownCreatures) > self.maxKnownCreatures:
                            removeKnown = player.checkRemoveKnown()
                            if not removeKnown:
                                player.exit("Too many creatures in known list. Please relogin")
                                return
                        player.knownCreatures.add(creature)
                        creature.knownBy.add(player)
                    
                    self.creature(creature, known, removeKnown)
                    
                if creature.creatureType != 0 and creature.noBrain:
                    print "Begin think 1"
                    creature.base.brain.handleThink(creature, False)

            for item in tile.bottomItems():
                self.item(item)
        
    def creature(self, creature, known, removeKnown=0):
        if known:
            self.uint16(0x62)
            self.uint32(creature.clientId())
        else:
            self.uint16(0x61)
            self.uint32(removeKnown) # Remove known
            self.uint32(creature.clientId())
            #self.uint8(creature.creatureType)
            self.string(creature.name())
        self.uint8(round(creature.data["healthmax"] / creature.data["health"]) * 100) # Health %
        self.uint8(creature.direction) # Direction
        self.outfit(creature.outfit, creature.addon, creature.mount if creature.mounted else 0x00)
        self.uint8(0) # Light
        self.uint8(0) # Light
        self.uint16(creature.speed) # Speed
        self.uint8(creature.skull) # Skull
        self.uint8(creature.shield) # Party/Shield
        if not known:
            self.uint8(creature.emblem) # Emblem
        self.uint8(creature.solid) # Can't walkthrough
        
    def skills(self, player):
        self.uint8(0xA1) # Skill type
        for x in xrange(game.enum.SKILL_FIRST, game.enum.SKILL_LAST+1):
            self.uint8(player.skills[x]) # Value / Level
            #self.uint8(1) # Base
            self.uint8(0) # %
        
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
        
class Protocol(base.BaseProtocol):
    Packet = Packet