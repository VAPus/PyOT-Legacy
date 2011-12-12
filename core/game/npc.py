from game.creature import Creature, CreatureBase, uniqueId
from game.monster import Monster, MonsterBrain
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
import game.scriptsystem
from packet import TibiaPacket

npcs = {}
brainFeatures = ({},{})
classActions = {}

class ClassAction(object):
    def __init__(self, on):
        self.on = on
        on.classActions.append(self)
        self.action()
        
    def action(self):
        pass

def Conversation(words, open, close=None):
    class Conv(ClassAction):
        def action(self):
            self.on.onSaid(words, open, close)
            
    return Conv
class NPC(Creature):
    def generateClientID(self):
        return 0x80000000 + uniqueId()

    def isNPC(self):
        return True
        
    def __init__(self, base, position, cid=None):
        Creature.__init__(self, base.data.copy(), position, cid)
        self.base = base
        self.creatureType = 2
        self.spawnPosition = position.copy()
        self.noBrain = True
        self.walkPer = base.walkPer
        self.openChannels = []
        self.focus = set()
        self.forSale = None
        self.activeModule = None
        self.activeSaid = None
        self.respawn = True
        
        # Replace handle say function with a speak tree parser.
        if self.base.speakTreeFunc:
            self.handleSpeak = self.handleSpeakTree
        
    def description(self):
        return "You see %s" % self.base.data["description"]
    
    def actionIds(self):
        return self.base.actions

    def setRespawn(self, state):
        self.respawn = state
        
    def playerSay(self, player, said, type, channel):
        game.scriptsystem.get('playerSayTo').run(self, player, None, said=said, channelType=type, channelId=channel)

    def sayTo(self, to, text, messageType=game.enum.MSG_NPC_FROM):
        self.sayPrivate(text, to, messageType)

    def sendTradeOffers(self, to):
        forSale = set()
        stream = TibiaPacket(0x7A)
        stream.string(self.data["name"])
        stream.uint8(min(len(self.base.offers), 255))
        for item in self.base.offers:
            stream.uint16(game.item.items[item[0]]["cid"])
            stream.uint8(item[3])
            stream.string(game.item.items[item[0]]["name"])
            stream.uint32(game.item.items[item[0]]["weight"] * 100)
            stream.int32(item[1])
            stream.int32(item[2])
            if item[2]:
                forSale.add(item[0])
                
        stream.send(to.client)
        self.sendGoods(to, forSale)
        self.forSale = forSale
    
    def sendGoods(self, to, forSale=None):
        # A bit heavy stuff:
        stream = TibiaPacket(0x7B)
        stream.uint32(to.getMoney())
        
        items = {}
        count = 0
        for item in to.inventory[2].container.getRecursive():
            if item.itemId in forSale:
                if item.itemId in items and item.stackable:
                    items[item.itemId] += item.count
                elif item.stackable:
                    items[item.itemId] = item.count
                    count += 1
                elif item.itemId in items:
                    items[item.itemId] += 1
                else:
                    items[item.itemId] = 1
                    count += 1
                    
                if count == 255:
                    break       
        stream.uint8(count)
        for itemId in items:
            stream.uint16(game.item.items[itemId]["cid"])
            stream.uint8(0) #or items[itemId]
            
        stream.send(to.client) 
        
    def buy(self, player, itemId, count, amount, ignoreCapasity=True, withBackpack=False):
        for offer in self.base.offers:
            if offer[0] == itemId and offer[3] == count:
                # Can we afford it?
                if player.removeMoney(offer[1] * amount):
                    count = count * amount
                    container = player.inventory[2]
                    if withBackpack:
                        container = game.item.Item(1987)
                        player.itemToContainer(player.inventory[2], container)
                        
                    while count:
                        rcount = min(100, count)
                        player.itemToContainer(container, game.item.Item(itemId, count))
                        count -= rcount
                        
                    if self.forSale and player.openTrade == self: # Resend my items
                        self.sendGoods(player, self.forSale)
                        
    def sell(self, player, itemId, count, amount, ignoreEquipped=True):
        for offer in self.base.offers:
            count = count * amount
            if offer[0] == itemId and offer[3] == count:
                # Do we really have this item?
                item = player.findItemById(itemId, count)
                if item.count == count:
                    player.addMoney(offer[2] * amount)
                    if self.forSale and player.openTrade == self: # Resend my items
                        self.sendGoods(player, self.forSale)

    def handleSpeak(self, player, said):
        if said in self.base._onSaid:
            self.activeModule = self.base._onSaid[said][0](self, player)
            self.activeSaid = said
            try:
                self.activeModule.send(None)
                
            except:
                self.activeModule = None
        else:
            pass # Get some ideas for this

    def handleSpeakTree(self, player, said):
        self.activeModule = self.base.speakTreeFunc(self, player)
        self.activeSaid = said
        self.activeModule.send(None)
        self.activeModule.send(said)
            
    def isAttackable(self, by):
        return self.base.attackable
        
class NPCBase(CreatureBase):
    def __init__(self, brain, data):
        self.data = data
        self.voiceslist = []
        self.scripts = {"onFollow":[], "onTargetLost":[]}
        
        self.speed = 100
        self.intervals = {}
        
        self.walkable = True
        self.attackable = False
        self.walkPer = config.monsterWalkPer
   
        self.brainFeatures = ["default"]
        self.classActions = []
        self.actions = ['creature', 'npc', self.data["name"]]
        self.speakGreet ="Welcome, %(playerName)s! I have been expecting you."
        self.speakFarewell = "Good bye, %(playerName)s!" 
        self.brain = brain
        self._onSaid = {}
        self.speakTreeFunc = None
        self.speakTreeGreet = None
        self.speakTreeFarewell = None

    def spawn(self, position, place=True, spawnDelay=0.25, spawnTime=60, radius=5, radiusTo=None):
        if spawnDelay:
            return game.engine.safeCallLater(spawnDelay, self.spawn, position, place, 0, spawnTime, radius, radiusTo)
        else:
            npc = NPC(self, position, None)
            npc.radius = radius
            if radius <= 1:
                self.walkable = False
            if not radiusTo:
                npc.radiusTo = (position[0], position[1])
            else:
                npc.radiusTo = radiusTo
            if place:
                try:
                    stackpos = game.map.getTile(position).placeCreature(npc)
                    if stackpos > 9:
                        log.msg("Can't place creatures on a stackpos > 9")
                        return
                        
                    for player in game.engine.getPlayers(position):
                        if player.client and not npc.cid in player.knownCreatures:
                            stream = player.packet()
                            stream.addTileCreature(position, stackpos, npc, player)
                        
                            stream.send(player.client)
                except:
                    log.msg("Spawning of npc('%s') on %s failed" % (self.data["name"], str(position)))
            return npc    

    def setHealth(self, health, healthmax=None):
        if not healthmax:
            healthmax = health
        self.data["health"] = health
        self.data["healthmax"] = healthmax

    def setDefense(self, armor=0, fire=0, earth=0, energy=0, ice=0, holy=0, death=0, physical=0, drown=0):
        self.armor = armor
        self.fire = fire
        self.earth = earth
        self.energy = energy
        self.ice = ice
        self.holy = holy
        self.death = death
        self.drown = drown
        self.physical = physical

    def setAttackable(self, attackable):
        self.attackable = attackable
        
    def bloodType(self, color="blood"):
        self.blood = getattr(game.enum, 'FLUID_'+color.upper())
        
    def setSpeed(self, speed):
        self.speed = speed
        
    def setWalkable(self, state):
        self.walkable = state

    def setRandomWalkInterval(self, per):
        self.walkPer = per

    def setBrainFeatures(self, *argc):
        self.brainFeatures = ('99',) + argc

    def setAddons(self, addon):
        self.data["lookaddons"] = addon

    def setActions(self, *argc):
        self.actions = list(argc)
        
    def regAction(self, action):
        self.actions.append(action)

    def module(self, action):
        if isinstance(action, type):
            actionClass = action(self)
            self.actions.append(actionClass)
            return actionClass
            
        else:
            self.actions.append(action)
            return classActions[action](self)

    def greet(self, greet):
        self.speakGreet = greet
        
    def farewell(self, farewell):
        self.speakFarewell = farewell
        
    def onSaid(self, what, open, close=None):
        if type(what) == tuple:
            for x in what:
                self._onSaid[x] = (open, close)
                
        else:
            self._onSaid[what] = (open, close)

    def speakTree(self, tree, farewell=None):
        # Register the opening stuff.
        greet = tree.keys()[0]
        if callable(greet) or type(greet) == str:
            self.greet(greet)
        else:
            self.speakTreeGreet = greet
            
            def _greet(npc, player):
                greet = npc.base.speakTreeGreet
                if type(greet) == tuple:
                    if len(greet) == 2:
                        # A callback included.
                        greet[1](npc=npc, player=player)
                        greet = greet[0]
                    elif len(greet) == 3:
                        if greet[0](npc=npc, player=player):
                            greet = greet[1]
                        else:
                            greet = greet[2]
                            

                                
                # The route ends with a string
                if type(greet) == str:
                    npc.sayTo(player, greet)
                    return
                                
                    
                # Function
                elif callable(greet):
                    greet(npc=npc, player=player)
                        
                # Route simply just ends
                elif greet == None:
                    return   
                    
            self.greet(_greet)
        
        root = tree[greet]
        
        # The callback function
        def openTree(npc, player):
            # The "currElm" holds the current level in the talking process we're on.
            # Currently "root" have been served as the greeting.
            currElm = root
            prevElm = None
            
            # Run until we run out of levels
            while True:
                response = (yield)
                if response in currElm:
                    nextElm = currElm[response]

                    if type(nextElm) == tuple:
                        if len(nextElm) == 2:
                            # A callback included.
                            nextElm[1](npc=npc, player=player)
                            nextElm = nextElm[0]
                        elif len(nextElm) == 3:
                            if nextElm[0](npc=npc, player=player):
                                nextElm = nextElm[1]
                            else:
                                nextElm = nextElm[2]
                        
                    # Proceed with next level.
                    if type(nextElm) == dict:
                        prevElm = currElm # Store this
                        key = nextElm.keys()[0]
                        currElm = nextElm[key]
                        npc.sayTo(player, key)
                            
                    # The route ends with a string
                    elif type(nextElm) == str:
                        npc.sayTo(player, nextElm)
                        return
                                
                    # Walk one level down.
                    elif nextElm == -1:
                        currElm = prevElm
                        npc.sayTo(player, currElm.keys()[0])
                    
                    # Function
                    elif callable(nextElm):
                        nextElm(npc=npc, player=player)
                        
                    # Route simply just ends
                    elif nextElm == None:
                        return
               
                # The not call
                elif "!" in currElm:
                    nextElm = currElm["!"]

                    if type(nextElm) == tuple:
                        if len(nextElm) == 2:
                            # A callback included.
                            nextElm[1](npc=npc, player=player)
                            nextElm = nextElm[0]
                        elif len(nextElm) == 3:
                            if nextElm[0](npc=npc, player=player):
                                nextElm = nextElm[1]
                            else:
                                nextElm = nextElm[2]
                        
                    # Proceed with next level.
                    if type(nextElm) == dict:
                        prevElm = currElm # Store this
                        key = nextElm.keys()[0]
                        currElm = nextElm[key]
                        npc.sayTo(player, key)
                            
                    # The route ends with a string
                    elif type(nextElm) == str:
                        npc.sayTo(player, nextElm)
                        return
                                
                    # Walk one level down.
                    elif nextElm == -1:
                        currElm = prevElm
                        npc.sayTo(player, currElm.keys()[0])
                    
                    # Function
                    elif callable(nextElm):
                        nextElm(npc=npc, player=player)
                        
                    # Route simply just ends
                    elif nextElm == None:
                        return

                # The any call. Only kicks in if this is not the end of the route tho.
                if "*" in currElm:
                    nextElm = currElm["*"]

                    if type(nextElm) == tuple:
                        if len(nextElm) == 2:
                            # A callback included.
                            nextElm[1](npc=npc, player=player)
                            nextElm = nextElm[0]
                        elif len(nextElm) == 3:
                            if nextElm[0](npc=npc, player=player):
                                nextElm = nextElm[1]
                            else:
                                nextElm = nextElm[2]
                        
                    # Proceed with next level.
                    if type(nextElm) == dict:
                        prevElm = currElm # Store this
                        key = nextElm.keys()[0]
                        currElm = nextElm[key]
                        npc.sayTo(player, key)
                            
                    # The route ends with a string
                    elif type(nextElm) == str:
                        npc.sayTo(player, nextElm)
                        return
                                
                    # Walk one level down.
                    elif nextElm == -1:
                        currElm = prevElm
                        npc.sayTo(player, currElm.keys()[0])
                    
                    # Function
                    elif callable(nextElm):
                        nextElm(npc=npc, player=player)
                        
                    # Route simply just ends
                    elif nextElm == None:
                        return
        
        # Override speaks
        self.speakTreeFunc = openTree
        
        # Register farewell
        if farewell:
            if callable(farewell) or type(farewell) == str:
                self.farewell(farewell)
            else:
                self.speakTreeFarewell = farewell
                
                def _farewell(npc, player):
                    farewell = npc.base.speakTreeFarewell
                    if type(farewell) == tuple:
                        if len(farewell) == 2:
                            # A callback included.
                            farewell[1](npc=npc, player=player)
                            farewell = farewell[0]
                        elif len(farewell) == 3:
                            if farewell[0](npc=npc, player=player):
                                farewell = farewell[1]
                            else:
                                farewell = farewell[2]
                                

                                    
                    # The route ends with a string
                    if type(farewell) == str:
                        npc.sayTo(player, farewell)
                        return
                                    
                        
                    # Function
                    elif callable(farewell):
                        farewell(npc=npc, player=player)
                            
                    # Route simply just ends
                    elif farewell == None:
                        return   
                        
                self.farewell(_farewell)
        
def chance(procent):
    def gen(npc):
        if 10 > random.randint(0, 100):
            return True
        else:
            return False
    return gen

class NPCBrain(MonsterBrain):
    @game.engine.loopInThread(2)
    def handleThink(self, npc, check=True):
        npc.noBrain = False
        # Are we alive?
        if not npc.alive:
            npc.noBrain = True
            return False # Stop looper 

        for feature in npc.base.brainFeatures:
            if feature in brainFeatures[0]:
                ret = brainFeatures[0][feature](self, npc)
                
                if ret in (True, False):
                    return ret

        for feature in npc.base.brainFeatures:
            if feature in brainFeatures[1]:
                ret = brainFeatures[1][feature](self, npc)

                if ret in (True, False):
                    return ret
                    
        # Are anyone watching?
        if check and not game.engine.getSpectators(npc.position, (11, 9), cache=False):
            monster.noBrain = True
            return False
            
        if npc.base.walkable and not npc.action and time.time() - npc.lastStep > npc.walkPer: # If no other action is available
            self.walkRandomStep(monster) # Walk a random step

brain = NPCBrain()
def genNPC(name, look, description=""):
    # First build the common creature data
    data = {}
    data["looktype"] = look[0]
    data["lookhead"] = look[1]
    data["lookbody"] = look[2]
    data["looklegs"] = look[3]
    data["lookfeet"] = look[4]
    data["lookaddons"] = 0
    data["corpse"] = look[5]
    data["health"] = 150
    data["healthmax"] = 150
    data["name"] = name
    data["description"] = description or "%s." % name
    
    # Then npc only data
    npcs[name] = NPCBase(brain, data)

    return npcs[name]

def getNPC(name):
    if name in npcs:
        return npcs[name]
    else:
        return None
        
def regBrainFeature(name, function, priority=1):
    if not name in brainFeatures[priority]:
        brainFeatures[priority][name] = function
    else:
        print "Warning, brain feature %s exists!" % name
        
def regClassAction(name, myClass):
    classActions[name] = myClass
