from game.creature import Creature, CreatureBase, uniqueId
from game.monster import Monster, MonsterBrain
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
import game.scriptsystem

npcs = {}
brainFeatures = ({},{})

class NPC(Creature):
    def generateClientID(self):
        return 0x80000000 + uniqueId()
        
    def __init__(self, base, position, cid=None):
        Creature.__init__(self, base.data.copy(), position, cid)
        self.base = base
        self.creatureType = 2
        self.spawnPosition = position[:]
        self.noBrain = True
        self.walkPer = base.walkPer
        self.openChannels = []
        
    def description(self):
        return "You see %s" % self.base.data["description"]

    def onHit(self, by, type):
        if self.base.attackable:
            Monster.onHit(self, by, type)
    
    def actionIds(self):
        return self.base.actions
        
    def playerSay(self, player, said, type, channel):
        game.scriptsystem.get('playerSayTo').run(self, player, None, said=said, channelType=type, channelId=channel)

    def sayTo(self, to, text):
        id = to.openPrivateChannel(self)
        to.sendChannelMessage(self, text, game.enum.MSG_NPC_FROM, id)
        
class NPCBase(CreatureBase):
    def __init__(self, data):
        self.data = data
        self.voiceslist = []
        self.scripts = {"onFollow":[], "onTargetLost":[]}
        
        self.speed = 100
        self.intervals = {}
        
        self.walkable = True
        self.attackable = False
        self.walkPer = config.monsterWalkPer
        
        self.brainFeatures = ["default"]
        self.actions = ('99',)
        
    def spawn(self, position, place=True, spawnDelay=0.15, spawnTime=60, radius=5, radiusTo=None):
        if spawnDelay:
            return game.engine.safeCallLater(spawnDelay, self.spawn, position, place, 0, spawnTime, radius, radiusTo)
        else:
            npc = NPC(self, position, None)
            npc.radius = radius
            if radius <= 1:
                self.walkable = False
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

    def setDefense(self, armor=0, fire=0, earth=0, energy=0, ice=0, holy=0, death=0, physical=0, drown=0):
        self.armor = armor
        self.fire = fire
        self.earth = earth
        self.energy = energy
        self.ice = ice
        self.holy = holy
        self.death = death
        self.drown = drown
        self.physical = physical

    def setAttackable(self, attackable):
        self.attackable = attackable
        
    def bloodType(self, color="blood"):
        self.blood = getattr(game.enum, 'FLUID_'+color.upper())
        
    def setSpeed(self, speed):
        self.speed = speed
        
    def setWalkable(self, state):
        self.walkable = state

    def setRandomWalkInterval(self, per):
        self.walkPer = per

    def setBrainFeatures(self, *argc):
        self.brainFeatures = ('99',) + argc

    def setAddons(self, addon):
        self.data["lookaddons"] = addon

    def setActions(self, *argc):
        self.actions = argc
def chance(procent):
    def gen(npc):
        if 10 > random.randint(0, 100):
            return True
        else:
            return False
    return gen

class NPCBrain(MonsterBrain):
    @game.engine.loopInThread(2)
    def handleThink(self, npc, check=True):
        npc.noBrain = False
        # Are we alive?
        if not npc.alive:
            npc.noBrain = True
            return False # Stop looper 

        for feature in npc.base.brainFeatures:
            if feature in brainFeatures[0]:
                ret = brainFeatures[0][feature](self, npc)
                
                if ret in (True, False):
                    return ret

        for feature in npc.base.brainFeatures:
            if feature in brainFeatures[1]:
                ret = brainFeatures[1][feature](self, npc)

                if ret in (True, False):
                    return ret
                    
        # Are anyone watching?
        if check and not game.engine.getSpectators(npc.position, (11, 9), cache=False):
            monster.noBrain = True
            return False
            
        if npc.base.walkable and not npc.action and time.time() - npc.lastStep > npc.walkPer: # If no other action is available
            self.walkRandomStep(monster) # Walk a random step

def genNPC(name, look, description=""):
    # First build the common creature data
    data = {}
    data["looktype"] = look[0]
    data["lookhead"] = look[1]
    data["lookbody"] = look[2]
    data["looklegs"] = look[3]
    data["lookfeet"] = look[4]
    data["lookaddons"] = 0
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
        
def regBrainFeature(name, function, priority=1):
    if not name in brainFeatures[priority]:
        brainFeatures[priority][name] = function
    else:
        print "Warning, brain feature %s exists!" % name