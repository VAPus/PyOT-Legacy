from game.creature import Creature, uniqueId
import game.engine, game.map
from packet import TibiaPacket
import copy, random
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
monsters = {}

monsters["default"] = {"lookhead":0, "lookfeet":0, "lookbody":0, "looklegs":0}
class Monster(Creature):
    def generateClientID(self):
        return 0x40000000 + uniqueId()
        
    def __init__(self, base, position, cid=None):
        Creature.__init__(self, base.data, position, cid)
        self.base = base
        self.creatureType = 1
        self.spawnPosition = position[:]

    


class MonsterBase:
    def __init__(self, data, brain, monsterData):
        self.data = data
        self.monsterData = monsterData
        self.voiceslist = []
        self.brain = brain
        
    def spawn(self, position, place=True):
        monster = Monster(self, position, None)
        self.brain.beginThink(monster) # begin the heavy thought process!

        if place:
            stackpos = game.map.getTile(position).placeCreature(monster)
            list = game.engine.getSpectators(position)
            for client in list:
                stream = TibiaPacket()
                stream.magicEffect(position, 0x03)
                stream.addTileCreature(position, stackpos, monster, client.player)
        
                stream.send(client)
        return monster
    def setHealth(self, health, healthmax=None):
        if not healthmax:
            healthmax = health
        self.data["health"] = health
        self.data["healthmax"] = healthmax

    def setDefense(self, armor, defense, fire=1, earth=1, energy=1, ice=1, holy=1, death=1):
        self.armor = armor
        self.defense = defense
        self.fire = fire
        self.earth = earth
        self.energy = energy
        self.ice = ice
        self.holy = holy
        self.death = death
    def voices(self, *argc):
        self.voiceslist = tuple(argc)

class MonsterBrain:
    def beginThink(self, monster):
        monster.actionThink = LoopingCall(self.handleThink, monster)
        monster.actionThink.start(1, False)
        if monster.base.voiceslist:
            monster.actionTalk = LoopingCall(self.handleTalk, monster)
            monster.actionTalk.start(5, False)
            
    def handleThink(self, monster):
        # Walking
        if 33 > random.randint(0, 100):
            self.walkRandomStep(monster)
            
    def handleTalk(self, monster):
        if 10 > random.randint(0, 100): # 10%. TODO: Support config
            text = random.choice(monster.base.voiceslist)
            if text.isupper():
                monster.yell(text)
            else:
                monster.say(text)
                
    def walkRandomStep(self, monster):
        spectators = game.engine.getSpectatorList(monster.position)
        if not spectators:
            return False
        
        steps = []
        xFrom = monster.position[0]-monster.spawnPosition[0]
        yFrom = monster.position[1]-monster.spawnPosition[1]
        
        steps = [0,1,2,3]
        random.shuffle(steps)
        for step in steps:
            if step is 0:
                if monster.spawnPosition[1]-(monster.position[1]-1) > 5:
                    continue
            elif step is 1:
                if monster.spawnPosition[0]-(monster.position[0]+1) > -5:
                    continue
            elif step is 2:
                if monster.spawnPosition[1]-(monster.position[1]+1) > -5:
                    continue
            elif step is 3:
                if monster.spawnPosition[0]-(monster.position[0]-1) > 5:
                    continue
                
            if monster.move(step, spectators):
                return True
        return False
        
brains = {}
brains["default"] = MonsterBrain()
def genMonster(name, look, description="", speed=200, experience=100, race="blood", brain="default", template="default"):
    # First build the common creature data
    if template in monsters:
        data = copy.deepcopy(monsters[template])

    data["speed"] = speed
    data["looktype"] = look[0]
    data["name"] = name
    # Then monster only data
    monsters[name] = MonsterBase(data, brains[brain], None)
    return monsters[name]

def getMonster(name):
    if name in monsters:
        return monsters[name]
    else:
        return None