import core.game.scriptsystem as scriptsystem
from core.packet import TibiaPacket
from core.game.map import placeCreature, getTile
import core.game.game, core.game.item
from core.game.creature import Creature

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
            
        if not id in core.game.item.items:
            object.message("Item not found!")
            return False
        item = core.game.item.Item( id )

        getTile(pos).setThing(0, item)

        core.game.game.updateTile(pos, getTile(pos))
        object.magicEffect(pos, 0x03)
    #except:
    #    object.message("Not possible!")
        return False
        
def dummyCreature(object, text):
    pos = [object.position[0]+1, object.position[1], 7]
    monsterData = {"name": "Dummy", "health":1000, "looktype": 59, "lookhead":0, "looklegs":0, "lookbody":0, "lookfeet":0} # A mal
    creature = Creature(monsterData, pos)
    stackpos = getTile(pos).placeCreature(creature)
    stream = TibiaPacket()
    stream.addTileCreature(pos, stackpos, creature)
    stream.sendto(core.game.game.getSpectators(pos))
scriptsystem.get("talkaction").reg("help", callback)
scriptsystem.get("talkactionFirstWord").reg('rep', repeater)
scriptsystem.get("talkactionFirstWord").reg('teleport', teleporter)
scriptsystem.get("talkactionFirstWord").reg('set', tiler)
scriptsystem.get("talkaction").reg('spawn', dummyCreature)