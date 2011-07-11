import game.scriptsystem as scriptsystem
from packet import TibiaPacket
from game.map import placeCreature, getTile
import game.engine, game.item
from game.creature import Creature, Monster

def callback(object, text):
    object.message("No you!!")
    
def repeater(object, text):
    object.message(text)
    
def teleporter(object, text):
    x,y,z = text.split(',')
    pos = [int(x),int(y),int(z)]
    object.teleport(pos)
    object.message("Welcome to %s" % text)
    
def tiler(object, text):
    #try:
        if len(text.split(" ")) < 2:
            pos = object.position
            id = int(text.split(" ")[0])
        else:
            x,y,z = text.split(" ")[0].split(',')
            pos = [int(x),int(y),int(z)]
            id = int(text.split(" ")[1])
            
        if not id in game.item.items:
            object.message("Item not found!")
            return False
        item = game.item.Item( id )

        getTile(pos).setThing(0, item)

        game.engine.updateTile(pos, getTile(pos))
        object.magicEffect(pos, 0x03)
    #except:
    #    object.message("Not possible!")
        return False
        
def dummyCreature(object, text):
    pos = [object.position[0]+1, object.position[1], 7]
    monsterData = {"name": "Dummy", "health":1000, "looktype": 59, "lookhead":0, "looklegs":0, "lookbody":0, "lookfeet":0} # A mal
    creature = Monster(monsterData, pos)
    stackpos = getTile(pos).placeCreature(creature)
    list = game.engine.getSpectators(pos)
    for client in list:
        stream = TibiaPacket()
        stream.addTileCreature(pos, stackpos, creature, client.player)
        stream.send(client)
scriptsystem.get("talkaction").reg("help", callback)
scriptsystem.get("talkactionFirstWord").reg('rep', repeater)
scriptsystem.get("talkactionFirstWord").reg('teleport', teleporter)
scriptsystem.get("talkactionFirstWord").reg('set', tiler)
scriptsystem.get("talkaction").reg('spawn', dummyCreature)

def speedsetter(object, text):
    try:
        object.setSpeed(int(text))
    except:
        object.message("Invalid speed!")
scriptsystem.get("talkactionFirstWord").reg('speed', speedsetter)