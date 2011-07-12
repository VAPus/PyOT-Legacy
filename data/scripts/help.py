import game.scriptsystem as scriptsystem
from packet import TibiaPacket
from game.map import placeCreature, getTile
import game.engine, game.item
from game.creature import Creature, Monster

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
        
def dummyCreature(player, text):
    pos = [player.position[0]+1, player.position[1], 7]
    monsterData = {"name": "Dummy", "health":1000, "looktype": 59, "lookhead":0, "looklegs":0, "lookbody":0, "lookfeet":0} # A mal
    creature = Monster(monsterData, pos)
    stackpos = getTile(pos).placeCreature(creature)
    list = game.engine.getSpectators(pos)
    for client in list:
        stream = TibiaPacket()
        stream.magicEffect(pos, 0x03)
        stream.addTileCreature(pos, stackpos, creature, client.player)
        
        stream.send(client)
scriptsystem.get("talkaction").reg("help", callback)
scriptsystem.get("talkactionFirstWord").reg('rep', repeater)
scriptsystem.get("talkactionFirstWord").reg('teleport', teleporter)
scriptsystem.get("talkactionFirstWord").reg('set', tiler)
scriptsystem.get("talkaction").reg('spawn', dummyCreature)

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
    
    
    
    if item.openId == None:
        # Open a bag inside a bag?
        for bag in player.openContainers:
            if bag.openId == index:
                # Virtual close
                player.openContainers[index].openId = None
                
                # Virtual switch
                item.openId = index
                player.openContainers[index] = item
                
                # Update the container
                player.updateContainer(item)
                return
        
        # Open a new one
        player.openContainer(item)

    else:
        player.closeContainer(item)
        
scriptsystem.get("useItem").reg(1987, testContainer)