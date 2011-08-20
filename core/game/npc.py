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

def chance(procent):
    def gen(monster):
        if 10 > random.randint(0, 100):
            return True
        else:
            return False
    return gen

brains = {}
brains["default"] = None #MonsterBrain()
def genNPC(name, look, description="", brain="default"):
    # First build the common creature data
    data = {"lookhead":0, "lookfeet":0, "lookbody":0, "looklegs":0}

    data["looktype"] = look[0]
    data["corpse"] = look[1]
    data["name"] = name
    # Then npc only data
    npcs[name] = NPCBase(data, brains[brain], None)

    return npcs[name]

def getNPC(name):
    if name in npcs:
        return npcs[name]
    else:
        return None