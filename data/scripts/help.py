import core.game.scriptsystem as scriptsystem
from core.packet import TibiaPacket
from core.game.map import placeCreature
import copy

def callback(object, text):
    object.message("No you!!")
    
def repeater(object, text):
    object.message(text)
    
def clone(object, text):
    clone = copy.deepcopy(object)
    clone.cid += 1
    clone.position[0] -= 1
    clone.position[1] -= 1
   
    placeCreature(clone, clone.position)
scriptsystem.get("talkaction").reg("help", callback)
scriptsystem.get("talkaction").reg("clone", clone)
scriptsystem.get("talkactionFirstWord").reg('rep', repeater)