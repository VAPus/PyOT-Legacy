import game.scriptsystem as scriptsystem
from packet import TibiaPacket
from game.map import placeCreature, getTile
import game.engine, game.item
from game.creature import Creature

def callback(player, text):
    player.message("No you!!")
    
def repeater(player, text):
    player.message(text)
    
def teleporter(player, text):
    x,y,z = text.split(',')
    pos = [int(x),int(y),int(z)]
    player.teleport(pos)
    player.message("Welcome to %s" % text)
    
def tiler(player, text):
    #try:
        if len(text.split(" ")) < 2:
            pos = player.position
            id = int(text.split(" ")[0])
        else:
            x,y,z = text.split(" ")[0].split(',')
            pos = [int(x),int(y),int(z)]
            id = int(text.split(" ")[1])
            
        if not id in game.item.items:
            player.message("Item not found!")
            return False
        item = game.item.Item( id )

        getTile(pos).setThing(0, item)

        game.engine.updateTile(pos, getTile(pos))
        player.magicEffect(pos, 0x03)
    #except:
    #    player.message("Not possible!")
        return False
        

scriptsystem.get("talkaction").reg("help", callback)
scriptsystem.get("talkactionFirstWord").reg('rep', repeater)
scriptsystem.get("talkactionFirstWord").reg('teleport', teleporter)
scriptsystem.get("talkactionFirstWord").reg('set', tiler)

def speedsetter(player, text):
    try:
        player.setSpeed(int(text))
    except:
        player.message("Invalid speed!")
scriptsystem.get("talkactionFirstWord").reg('speed', speedsetter)



# First use of actions :p
def testContainer(player, item, position, index):
    # Each time you open it, add a bag. I use this code to test max capasity stuff
    if position[1] is 3:
        bag1 = game.item.Item(1987)
        item.container.placeItem(bag1)
    
    
    if not item.opened:
        print "Not open"
        # Open a bag inside a bag?
        open = True
        try:
            bagFound = player.openContainers[index]
            print "Bag found"
        except:
            bagFound = None       
            
        if bagFound:
            # Virtual close
            player.openContainers[index].opened = False
                
            # Virtual switch
            item.opened = True
            item.parent = player.openContainers[index]
                
            # Update the container
            player.updateContainer(item, parent=1)
            open = False
        
        if open:
            # Open a new one
            parent = 0
            print position
            print player.openContainers

            if position[0] == 0xFFFF and position[1] >= 64:
                parent = 1
                item.parent = player.openContainers[position[2]-64]
            player.openContainer(item, parent=parent)

        # Opened from ground, close it on next step :)
        if position[0] != 0xFFFF:
            player.scripts["onNextStep"].append(lambda who: player.closeContainer(item))
    else:
        player.closeContainer(item)
        
scriptsystem.get("useItem").reg(1987, testContainer)


def makeitem(player, text):
     try:
        text = int(text)
        if text >= 1000:
            newitem = game.item.Item(text, 1)
            bag = player.inventory[2]
            player.itemToContainer(bag, newitem)
        else:
            raise NameError()
     except:
         player.message("Invalid Item!")
         
     return False

scriptsystem.get("talkactionFirstWord").reg('i', makeitem)