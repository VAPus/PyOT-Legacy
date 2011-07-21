from game.creature import Creature, uniqueId
import game.engine, game.map
from packet import TibiaPacket
import copy

monsters = {}

monsters["default"] = {"lookhead":0, "lookfeet":0, "lookbody":0, "looklegs":0}
class Monster(Creature):
    def generateClientID(self):
        return 0x40000000 + uniqueId()
        
    def __init__(self, base, position, cid=None):
        Creature.__init__(self, base.data, position, cid)
        self.base = base
        self.creatureType = 1

    


class MonsterBase:
    def __init__(self, data, monsterData):
        self.data = data
        self.monsterData = monsterData
        self.voiceslist = []
        
    def spawn(self, position, place=True):
        monster = Monster(self, position, None)
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
def genMonster(name, look, description="", speed=200, experience=100, race="blood", brain="default", template="default"):
    # First build the common creature data
    if template in monsters:
        data = copy.deepcopy(monsters[template])

    data["speed"] = speed
    data["looktype"] = look[0]
    data["name"] = name
    # Then monster only data
    monsters[name] = MonsterBase(data, None)
    return monsters[name]

def getMonster(name):
    if name in monsters:
        return monsters[name]
    else:
        return None