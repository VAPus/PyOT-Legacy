from game.creature import Creature, CreatureBase, uniqueId
import game.engine, game.map, game.scriptsystem
from packet import TibiaPacket
import copy, random, time
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.python import log
import game.enum
import game.errors
import game.item
import config

npcs = {}

class NPC(Creature):
    def generateClientID(self):
        return 0x80000000 + uniqueId()
        
    def __init__(self, base, position, cid=None):
        Creature.__init__(self, base.data.copy(), position, cid)
        self.base = base
        self.creatureType = 2
        self.spawnPosition = position[:]
        
    def description(self):
        return "You see %s" % self.base.data["description"]
        
class NPCBase(CreatureBase):
    def __init__(self, data):
        self.data = data
        self.voiceslist = []
        self.scripts = {"onFollow":[], "onTargetLost":[]}
        
        self.speed = 100
        self.experience = 0
        self.intervals = {}
        
    def spawn(self, position, place=True, spawnDelay=0.5, spawnTime=60, radius=5, radiusTo=None):
        if spawnDelay:
            return game.engine.safeCallLater(spawnDelay, self.spawn, position, place, 0, spawnTime, radius, radiusTo)
        else:
            npc = NPC(self, position, None)
            npc.radius = radius
            if not radiusTo:
                npc.radiusTo = (position[0], position[1])
            else:
                npc.radiusTo = radiusTo
            if place:
                try:
                    stackpos = game.map.getTile(position).placeCreature(npc)
                    if stackpos > 9:
                        log.msg("Can't place creatures on a stackpos > 9")
                        return
                        
                    list = game.engine.getSpectators(position)
                    for client in list:
                        stream = TibiaPacket()
                        stream.magicEffect(position, 0x03)
                        stream.addTileCreature(position, stackpos, npc, client.player)
                
                        stream.send(client)
                except:
                    log.msg("Spawning of npc('%s') on %s failed" % (self.data["name"], str(position)))
            return npc    

    def setHealth(self, health, healthmax=None):
        if not healthmax:
            healthmax = health
        self.data["health"] = health
        self.data["healthmax"] = healthmax

def chance(procent):
    def gen(npc):
        if 10 > random.randint(0, 100):
            return True
        else:
            return False
    return gen


def genNPC(name, look, description=""):
    # First build the common creature data
    data = {}
    data["looktype"] = look[0]
    data["lookhead"] = look[1]
    data["lookbody"] = look[2]
    data["looklegs"] = look[3]
    data["lookfeet"] = look[4]
    data["corpse"] = look[5]
    data["health"] = 150
    data["healthmax"] = 150
    data["name"] = name
    data["description"] = description or "%s." % name
    
    # Then npc only data
    npcs[name] = NPCBase(data)

    return npcs[name]

def getNPC(name):
    if name in npcs:
        return npcs[name]
    else:
        return None