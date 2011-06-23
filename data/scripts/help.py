import core.game.scriptsystem as scriptsystem
from core.packet import TibiaPacket

def callback(object, text):
    object.message("No you!!")
    
def repeater(object, text):
    object.message(text)
    
scriptsystem.get("talkaction").reg("help", callback)
scriptsystem.get("talkactionFirstWord").reg('rep', repeater)