import core.game.scriptsystem as scriptsystem
from core.packet import TibiaPacket
from core.game.map import placeCreature, getTile
import core.game.game, core.game.item

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
    try:
        x,y,z = text.split(" ")[0].split(',')
        pos = [int(x),int(y),int(z)]
        items = [int(text.split(" ")[1])]
        if not items[0] in core.game.item.items:
            object.message("Item not found!")
            return False
            
        getTile(pos).items = items
        object.message("Ok")
        core.game.game.updateTile(pos, getTile(pos))
        object.magicEffect(pos, 0x03)
    except:
        object.message("Not possible!")
    return False
scriptsystem.get("talkaction").reg("help", callback)
scriptsystem.get("talkactionFirstWord").reg('rep', repeater)
scriptsystem.get("talkactionFirstWord").reg('teleport', teleporter)
scriptsystem.get("talkactionFirstWord").reg('settile', tiler)