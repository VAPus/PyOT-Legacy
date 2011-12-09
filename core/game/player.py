from game import enum, engine
from game.map import placeCreature, removeCreature, getTile, Position
from twisted.python import log
import config
from collections import deque
import game.scriptsystem
from game.item import Item
from twisted.internet import reactor, defer
from game.creature import Creature, CreatureBase, uniqueId, allCreatures
import time

import game.resource
import game.chat
import game.pathfinder
import sql
import game.vocation
import random
import math
import otjson
import datetime
try:
    import cPickle as pickle
except:
    import pickle

global anyPlayer
anyPlayer = CreatureBase()
allPlayers = {}
allPlayersObject = allPlayers.viewvalues() # Quick speedup

class Player(Creature):
    def __init__(self, client, data):
        Creature.__init__(self, data, Position(int(data['posx']),int(data['posy']),int(data['posz'])))
        self.client = client
        
        self.speed = 220
        self.modes = [0,0,0]
        self.gender = 0
        self.base = anyPlayer
        self.knownCreatures = set()
        self.openContainers = []
        self.doingSoulGain = False
        self.data["stamina"] = self.data["stamina"] / 1000 # OT milisec to pyot seconds
        self.targetChecker = None
        self._openChannels = {}
        self.idMap = []
        self.openTrade = None
        self.isTradingWith = None
        self.tradeItems = []
        self.startedTrade = False
        self.tradeAccepted = False
        
        self.windowTextId = 0
        self.windowHandlers = {}
        self.partyObj = None
        self.solid = not config.playerWalkthrough

        # Rates
        self.rates = [config.experienceRate, 60, config.lootDropRate, config.lootMaxRate, 1] # 0 => Experience rate, 1 => Stamina loose rate, 2 => drop rate, 3 => drop rate (max items), 4 => regain rate
        self.inventoryWeight = 0
        
        # Direction
        self.direction = self.data["direction"]
        #del self.data["direction"]

        # Inventory
        self.inventoryCache = {}
        if self.data['inventory']:
            self.unpickleInventory(self.data['inventory'])
            
            # Call on equip
            for x in xrange(0, len(self.inventory)):
                item = self.inventory[x]
                if item:
                    game.scriptsystem.get("equip").run(self, item, slot = x+1)
                
        else:
            self.inventory = [Item(8820), Item(2125), Item(1987), Item(2463), None, Item(7449), None, None, None, Item(2546, 20), None]
            for item in self.inventory:
                if item:
                    weight = item.weight
                    if weight:
                        self.inventoryWeight += weight * (item.count or 1)
                    try:
                        self.inventoryCache[item.itemId].append(item)
                        self.inventoryCache[item.itemId][0] += item.count or 1
                    except:
                        self.inventoryCache[item.itemId] = [item.count or 1, item]
                    
        #del self.data['inventory']
        
        # Depot, (yes, we load it here)
        if self.data['depot']:
            self.depot = pickle.loads(self.data['depot'])
        else:
            self.depot = {} # {depotId : inventoryList}
            
        #del self.data['depot']
        
        # Calculate level from experience
        vocation = self.getVocation()
        level = int(config.levelFromExpFormula(self.data["experience"]))
        
        # Calculate magic level from manaspent
        self.data["maglevel"] = int(config.magicLevelFromManaFormula(self.data["manaspent"], vocation.mlevel))
        
        self.setLevel(level, False)
        self.speed = min(220.0 + (2 * data["level"]-1), 1500.0)

        # Storage & skills
        try:
            self.skills = otjson.loads(self.data["skills"])
            if len(self.skills) != (game.enum.SKILL_LAST*2)+1:
                raise
        except:
            self.skills = []
            for i in xrange(game.enum.SKILL_FIRST, (game.enum.SKILL_LAST*2)+2):
                self.skills.append(10)
            
        #del self.data["skills"]
        
        if self.data["storage"]:
            self.storage = otjson.loads(self.data["storage"])
        else:
            self.storage = {}
            
        #del self.data["storage"]
        
        # Storage states
        self.saveStorage = False
        self.saveInventory = False
        self.saveDepot = False
        self.saveSkills = False
        self.saveData = False
        self.doSave = True
        
    def generateClientID(self):
        return 0x10000000 + uniqueId()

    def isPlayer(self):
        return True

    def isPushable(self, by):
        return config.playerIsPushable

    def isAttackable(self, by):
        return True

    def actionIds(self):
        return ('creature', 'player') # Static actionID
        
    def sexPrefix(self):
        if self.data["sex"] == 1:
            return "He"
        else:
            return "She"
            
    def description(self, isSelf=False):
        if isSelf:
            output = "You see yourself. You are %s." % self.getVocation().description()
        else:
            output = "You see %s (Level %d). %s is %s." % (self.name(), self.data["level"], self.sexPrefix(), self.getVocation().description())
        return output
        
    def packet(self, *args):
        try:
            return self.client.protocol.Packet(*args)
        except:
            return None

    def ip(self):
        if self.client:
            return self.client.transport.getPeer().host
    
    def sendFirstPacket(self):
        if not self.data["health"]:
            self.data["health"] = 1
            
        stream = self.packet(0x0A)

        stream.uint32(self.clientId()) # Cid
        stream.uint16(config.drawingSpeed) # Drawing speed
        stream.uint8(1) # Rule violations?

        #stream.violation(0)
        
        stream.uint8(0x64) # Map description
        stream.position(self.position)
        stream.mapDescription(Position(self.position.x - 8, self.position.y - 6, self.position.z), 18, 14, self)

        for slot in xrange(enum.SLOT_FIRST,enum.SLOT_LAST):
            if self.inventory[slot-1]:
                stream.uint8(0x78)
                stream.uint8(slot)
            
                stream.item(self.inventory[slot-1])
            else:
                stream.uint8(0x79)
                stream.uint8(slot)
                
        self.refreshStatus(stream)
        self.refreshSkills(stream)
        
        stream.worldlight(game.engine.getLightLevel(), enum.LIGHTCOLOR_WHITE)
        stream.creaturelight(self.cid, 0,0)
        self.refreshConditions(stream)

        stream.magicEffect(self.position, 0x03)
        stream.send(self.client)
        
        self.sendVipList()
        
        # Stamina loose
        if self.data["stamina"]:
            def loseStamina():
                if self.client:
                    self.data["stamina"] -= 60
                    if self.data["stamina"] < 0:
                        self.data["stamina"] = 0
                    else:
                        game.engine.safeCallLater(self.rates[1], loseStamina)
                    
                    if self.data["stamina"] < (42*3600):
                        self.refreshStatus()
                    
            game.engine.safeCallLater(self.rates[1], loseStamina)
        
    def refreshStatus(self, streamX=None):
        if not streamX:
            if self.client:
                stream = self.packet()
            else:
                return False # No client
        else:
            stream = streamX
            
        stream.status(self)

        if not streamX:
            stream.send(self.client)

    def refreshConditions(self, streamX=None):
        if not streamX:
            if self.client:
                stream = self.packet()
            else:
                return False # No client
        else:
            stream = streamX
        
        send = 0
        for conId in self.conditions:
            try:
                conId = int(conId)
                send += conId
            except:
                pass
            
        stream.icons(send)

        if not streamX:
            stream.send(self.client)
            
    def refreshSkills(self, streamX=None):
        if not streamX:
            stream = self.packet()
        else:
            stream = streamX
            
        stream.skills(self)

        if not streamX:
            stream.send(self.client)            
            

    def pong(self):
        self.packet(0x1E).send(self.client)

    def getVocation(self):
        return game.vocation.getVocationById(self.data["vocation"])
    
    def getVocationId(self):
        return self.data["vocation"]
        
    def freeCapasity(self):
        return max(self.data["capasity"] - self.inventoryWeight, 0)
        
    def findItem(self, position, sid=None):
        # Option 1, from the map:
        if position:
            if position.x != 0xFFFF:
                if isinstance(position, StackPosition):
                    print "findItem - stackpos"
                    return position.getThing()
                else:
                    raise AttributeError("Position is not a subclass of StackPosition, but points to a map position.")
            
            # Option 2, the inventory
            elif position.y < 64:
                return self.inventory[position.y-1]
            
            # Option 3, the bags, if there is one ofcource
            else:
                try:
                    bag = self.openContainers[position.y - 64]
                except:
                    return
                    
                item = bag.container.getThing(position.z)
                return item

        # Option 4, find any item the player might posess
        if sid:
            # Inventory
            try:
                return self.inventoryCache[sid][-1]
            except:
                return None
            
    def findItemWithPlacement(self, position, sid=None):
        # Option 1, from the map:
        if position:
            if position.x != 0xFFFF:
                if isinstance(position, StackPosition):
                    thing = position.getThing()
                    return (0, thing, position.getTile()) if isinstance(thing, game.item.Item) else None
                else:
                    raise AttributeError("Position is not a subclass of StackPosition, but points to a map position.")
                
            # Option 2, the inventory
            elif position.y < 64:
                return (1, self.inventory[position.y-1]) if self.inventory[position.y-1] else None
            
            # Option 3, the bags, if there is one ofcource
            else:
                try:
                    bag = self.openContainers[position.y - 64]
                except:
                    return
                item = bag.container.getThing(position.z)
                return (2, item, bag)

        # Option 4, find any item the player might posess
        if sid:
            # Inventory
            try:
                itemFound = self.inventoryCache[sid][-1]
                if item.container:
                    return (3, itemFound, itemFound.container)
            except:
                return None

    def findItemById(self, itemId, count=0):
        items = []
        foundCount = 0
        stream = self.packet()
        # From inventory?
        for item in self.inventory:
            if item and item.itemId == itemId:
                items.append((1, item, self.inventory.index(item)))
                if count:
                    foundCount += item.count
                    
                    if foundCount >= count: break
                else:
                    break
        

        if (not len(items) or foundCount < count) and self.inventory[3]:
            bags = [self.inventory[2]]
            for bag in bags:
                index = 0
                for item in bag.container.items:
                    if item.itemId == itemId:
                        items.append((2, item, bag, index))
                        if count:
                            foundCount += item.count
                            
                            if foundCount >= count: break
                        else:
                            break
                    elif item.containerSize:
                        bags.append(item)
                    index += 1

        if count and foundCount < count:
            return None
        elif not items:
            return None
        elif items and not count:
            if items[0][0] == 1:
                self.inventory[items[0][3]] = None
                stream.removeInventoryItem(items[0][2]+1)

            elif items[0][0] == 2:
                items[0][2].container.removeItem(items[0][1])
                try:
                    stream.removeContainerItem(self.openContainers.index(items[0][2]), items[0][3])
                except:
                    pass
            
            # Update cached data
            if self.removeCache(items[0][1]):
                self.refreshStatus(stream)
            
            stream.send(self.client)
            return items[0][1]
        else:
            newItem = game.item.Item(itemId, count)
            sendUpdate = False
            for item in items:
                if not count:
                    break
                precount = item[1].count
                item[1].reduceCount(min(item[1].count, count))
                count = precount - item[1].count
                if item[1].count:
                    if item[0] == 1:
                        stream.addInventoryItem(item[2]+1, item[1])
                    elif item[0] == 2:
                        try:
                            stream.updateContainerItem(self.openContainers.index(item[2]), item[3], item[1])
                        except:
                            pass

                    # Update cached data
                    if self.removeCache(item[1]) and not sendUpdate:
                        sendUpdate = True
                    
                else:
                    if item[0] == 1:
                        self.inventory[item[2]+1-1] = None
                        stream.removeInventoryItem(item[2]+1)
                    elif item[0] == 2:
                        item[2].container.removeItem(item[1])
                        stream.removeContainerItem(self.openContainers.index(item[2]), item[3])
                        
                    # Update cached data
                    if self.removeCache(item[1]) and not sendUpdate:
                        sendUpdate = True
            
            if sendUpdate:
                self.refreshStatus(stream)
            stream.send(self.client)
            return newItem

    def replaceItem(self, position, item):
        # Option 1, from the map:
        if position:
            if position.x != 0xFFFF:
                tile = position.getTile()
                tile.things[position.stackpos] = item
                game.engine.updateTile(position, tile)
                
            # Option 2, the inventory
            elif position.y < 64:
                sendUpdate = False
                currItem = self.inventory[position.y-1]
                if currItem:
                    # Update cached data
                    if self.removeCache(currItem):
                        sendUpdate = True
                        
                ret = self.addCache(item)
                if ret:
                    sendUpdate = True
                    self.inventory[position.y-1] = item
                elif ret == False:
                    self.inventory[position.y-1] = None
                    tile = game.map.getTile(self.position)
                    tile.placeItem(item)
                    self.tooHeavy()
                    
                if sendUpdate:
                    self.refreshStatus()
                
                self.updateInventory(position.y)
            
            # Option 3, the bags, if there is one ofcource
            else:
                update = False
                try:
                    bag = self.openContainers[position.y - 64]
                except:
                    return
                
                try:
                    self.inventoryCache[bag.itemId].index(bag)
                    currItem = bag.container.items[position.z]
                    if currItem:
                        if self.removeCache(currItem):
                            update = True
                    
                    ret = self.addCache(item, bag)
                    if ret == False:
                        del bag.container.items[position.z]
                    elif ret == True:    
                        update = True
                        bag.container.items[position.z] = item
                        
                    stream = self.packet()
                    stream.updateContainerItem(position.y - 64, position.z, item)
                    if update:
                        self.refreshStatus(stream)
                    stream.send(self.client)
                except:  
                    bag.container.items[position.z] = item
                    stream = self.packet()
                    stream.updateContainerItem(position.y - 64, position.z, item)
                    stream.send(self.client)
                    
    def modifyItem(self, thing, position, mod):
        try:
            thing.count += mod
        except:
            pass
        
        if thing.count > 0:
            self.replaceItem(position, thing)
        else:
            self.removeItem(position)
                
    def removeItem(self, position):
        # Option 1, from the map:
        if position:
            if position.x != 0xFFFF:
                tile = position.getTile()
                del tile.things[stackpos]
                game.engine.updateTile(position, tile)
                
            # Option 2, the inventory
            elif position.y < 64:
                if self.removeCache(self.inventory[position.y-1]):
                    self.refreshStatus()
                self.inventory[position.y-1] = None
                self.updateInventory(position.y)
            
            # Option 3, the bags, if there is one ofcource
            elif self.inventory[2]:
                update = False
                try:
                    bag = self.openContainers[position.y - 64]
                except:
                    return
                
                try:
                    self.inventoryCache[bag.itemId].index(bag)
                    currItem = bag.container.items[position.z]
                    if currItem:
                        if self.removeCache(currItem):
                            update = True
                except:
                    pass
                
                del bag.container.items[position.z]
                stream = self.packet()
                stream.removeContainerItem(position.y - 64, position.z)
                if update:
                    self.refreshStatus(stream)
                stream.send(self.client)
                
    def getContainer(self, openId):
        print openId
        
        try:
            print self.openContainers[openId]
            return self.openContainers[openId]
        except:
            return

    def removeCache(self, item):
        # Update cached data
        try:
            print "Remove from cache ", item
            try:
                del item.inContainer
                del item.inPlayer
            except:
                pass
            
            self.inventoryCache[item.itemId].remove(item)
            self.inventoryCache[item.itemId][0] -= item.count or 1
            weight = item.weight
            
            # Save
            self.saveInventory = True
            
            if weight:
                self.inventoryWeight -= weight * (item.count or 1)
                return True
        except:
            pass
        
    def addCache(self, item, container=None):
        weight = item.weight
        if weight:
            self.inventoryWeight += weight * (item.count or 1)
            if self.inventoryWeight < 0:
                self.inventoryWeight -= weight * (item.count or 1)
                return False
        try:
            print "Add to cache ",item
            self.inventoryCache[item.itemId].append(item)
            self.inventoryCache[item.itemId][0] += item.count or 1
        except:
            self.inventoryCache[item.itemId] = [item.count or 1, item]
        
        if container:
            item.inContainer = container
        item.inPlayer = self
        
        # Save
        self.saveInventory = True
            
        if weight:
            return True
                
    def modifyCache(self, item, count):
        if not count: return
        
        try:
            self.inventoryCache[item.itemId][0] += count
            weight = item.weight
            
            # Save
            self.saveInventory = True
            
            if weight:
                self.inventoryWeight += weight * (count)
                return True
                
        except:
            pass
        
    # Experience & level
    def setLevel(self, level, send=True):
        vocation = self.getVocation()
        try:
            oldLevel = self.data["level"]
        except:
            oldLevel = 0
        if oldLevel != level:
            self.saveData = True
            self.data["level"] = level
            
            self.data["healthmax"] = vocation.maxHP(self.data["level"])
            self.data["manamax"] = vocation.maxMana(self.data["level"])
            self.data["capasity"] = vocation.maxCapasity(self.data["level"]) * 100
            
            if self.data["health"] > self.data["healthmax"]:
                self.data["health"] = self.data["healthmax"]
                
            if self.data["mana"] > self.data["manamax"]:
                self.data["mana"] = self.data["manamax"]
            
            if send:
                if level > oldLevel:
                    self.message("You advanced from level %d to Level %d." % (oldLevel, level), 'MSG_EVENT_ADVANCE')
                elif level < oldLevel:
                    self.message("You were downgraded from level %d to Level %d." % (oldLevel, level), 'MSG_EVENT_ADVANCE')
                self.refreshStatus()

    def modifyLevel(self, mod):
        self.setLevel(self.data["level"] + mod)
    
    def modifyMagicLevel(self, mod):
        self.data["maglevel"] += mod
        self.refreshStatus()
        
    def modifyExperience(self, exp):
        up = True
        if exp < 0:
            up = False
        
        self.data["experience"] += exp
        
        self.saveData = True
        
        if up:
            level = 0
            self.message("You gained %d experience points." % exp, 'MSG_EXPERIENCE', color=config.experienceMessageColor, value=exp, pos=self.position)
            while True:
                if config.totalExpFormula(self.data["level"]+level) > self.data["experience"]:
                    break
                level += 1
            if level:
                self.setLevel(self.data["level"]+level)
        else:
            level = 0
            self.message("You lost %d experience points." % exp, 'MSG_EXPERIENCE', color=config.experienceMessageColor, value=exp)
            while True:
                if config.totalExpFormula(self.data["level"]-level) > self.data["experience"]:
                    break
                level += 1
            if level:
                self.setLevel(self.data["level"]-level)            
        self.refreshStatus()

    # Mana & soul
    def setMana(self, mana):
        if self.data["health"] > 0:
            self.saveData = True
            self.data["mana"] = mana
            self.refreshStatus()
            return True
        return False
        
    def modifyMana(self, mana):
        return self.setMana(min(self.data["mana"] + mana, self.data["manamax"]))
        
    def modifySpentMana(self, mana, refresh=False):
        self.data["manaspent"] += mana
        self.saveData = True
        if self.data["manaspent"] > int(config.magicLevelFormula(self.data["maglevel"], vocation.mlevel)):
            self.modifyMagicLevel(1)
        elif refresh:
            self.refreshStatus()
        
        
    def setSoul(self, soul):
        if self.data["health"] > 0:
            self.saveData = True
            self.data["soul"] = soul
            self.refreshStatus()
            return True
        return False
        
    def modifySoul(self, soul):
        return self.setSoul(self.data["soul"] + soul)
        
    # Skills
    def addSkillLevel(self, skill, levels):
        self.skills[skill] += levels
        self.skills[skill + game.enum.SKILL_LAST + 1] += levels
        goal = config.skillFormula(self.skills[skill], self.getVocation().meleeSkill)
        self.setStorage('__skill%d' % skill, 0)
        self.setStorage('__skillGoal%d' % skill, goal)
        
        self.refreshSkills()
        self.saveSkills = True
        
    def tempAddSkillLevel(self, skill, level):
        self.skills[skill + game.enum.SKILL_LAST + 1] = self.skills[skill] + levels
        self.refreshSkills()
        self.saveSkills = True
        
    def tempRemoveSkillLevel(self, skill):
        self.skills[skill + game.enum.SKILL_LAST + 1] = self.skills[skill]
        self.refreshSkills()
        self.saveSkills = True
        
    def getActiveSkill(self, skill):
        return self.skills[skill + game.enum.SKILL_LAST + 1]

    def skillAttempt(self, skillType):
        key = '__skill%d' % skillType
        goalKey = '__skillGoal%s' % skillType
        
        try:
            self.modifyStorage(key, 1)
            
        except:
            # Happends on new members using new weapons
            self.setStorage(key, 1)
        
        skill = self.getStorage(key, 0)
        skillGoal = self.getStorage(goalKey, 0)
        if skill >= skillGoal:
            self.addSkillLevel(skillType, 1)
            self.setStorage(key, skillGoal - skill)
            
        self.refreshSkills() 
    # Soul
    def soulGain(self):
        def doSoulGain(gainOverX):
            self.modifySoul(1)
            if self.doingSoulGain - gainOverX >= time.time():
                game.engine.safeCallLater(gainOverX, doSoulGain, gainOverX)
            else:
                self.doingSoulGain = False
                
        if self.doingSoulGain > time.time():
            self.doingSoulGain += (config.soulGain)
        else:
            self.doingSoulGain = time.time() + (config.soulGain)
            gainTime = self.getVocation().soulticks * self.getRegainRate()
            game.engine.safeCallLater(gainTime, doSoulGain, gainTime)
    # Spells
    def cooldownSpell(self, icon, group, cooldown, groupCooldown=None):
        if groupCooldown == None: groupCooldown = cooldown
        
        stream = self.packet()
        stream.cooldownIcon(icon, cooldown)
        
        stream.cooldownGroup(group, groupCooldown)
        
        stream.send(self.client)        
        t = time.time()  + cooldown
        self.cooldowns[icon] = t
        self.cooldowns[group << 8] = t
        
    def cooldownIcon(self, icon, cooldown):
        self.cooldowns[icon] = time.time() + cooldown
        stream = self.packet()
        stream.cooldownIcon(icon, cooldown)
        stream.send(self.client)
        
    def cooldownGroup(self, group, cooldown):
        self.cooldowns[group << 8] = time.time() + cooldown
        stream = self.packet()
        stream.cooldownGroup(group, cooldown)
        stream.send(self.client)

    def canDoSpell(self, icon, group):
        t = time.time()
        group = group << 8
        if not group in self.cooldowns or self.cooldowns[group] < t:
            if not icon in self.cooldowns or self.cooldowns[icon] < t:
                return True
        return False
        
    def setModes(self, attack, chase, secure):
        def end():
            self.modes[0] = attack
            
            if self.target and self.targetMode == 1 and self.modes[1] != 1 and chase == 1:
                game.engine.autoWalkCreatureTo(self, self.target.position, -1, True)
                self.target.scripts["onNextStep"].append(self.followCallback)
                
            self.modes[1] = chase
            self.modes[2] = secure
            print "Modes", self.modes
        game.scriptsystem.get('modeChange').run(self, end, attack=attack, chase=chase, secure=secure)
        
        
            
    def setTarget(self, targetId=0):
        stream = self.packet(0xA3)
        stream.uint32(targetId)
        stream.send(self.client)
        
    def cancelWalk(self, direction=None):
        stream = self.packet(0xB5)
        stream.uint8(direction if direction is not None else self.direction)
        stream.send(self.client)
        
    def tutorial(self, tutorialId):
        stream = self.packet(0xDC)
        stream.uint8(tutorialId)
        stream.send(self.client)
        
    def mapMarker(self, position, typeId, desc=""):
        stream = self.packet(0xDD)
        stream.position(position)
        stream.uint8(typeId)
        stream.string(desc)
        stream.send(self.client)
        
    def message(self, message, msgType='MSG_INFO_DESCR', color=0, value=0, pos=None):
        stream = self.packet()
        stream.message(self, message, msgType, color, value, pos)
        stream.send(self.client)
    
    def orangeStatusMessage(self, message, msgType="MSG_STATUS_CONSOLE_ORANGE", color=0, value=0, pos=None):
        stream = self.packet()
        stream.message(self, message, msgType, color, value, pos)
        stream.send(self.client)        

    def outfitWindow(self):
        stream = self.packet(0xC8)
        
        # First the current outfit
        stream.outfit(self.outfit, self.addon, self.mount)
        looks = []
        for outfit in game.resource.outfits:
            if len(looks) == stream.maxOutfits:
                break
            if outfit and self.canWearOutfit(outfit.name):
                looks.append(outfit)
                
        if looks:        
            stream.uint8(len(looks))
            for outfit in looks:
                look = outfit.getLook(self.gender)
                stream.uint16(look[0])
                stream.string(outfit.name)
                stream.uint8(self.getAddonsForOutfit(outfit.name))
        else:
            # Send the current outfit only
            stream.uint8(1)
            stream.uint16(self.outfit[0])
            stream.string("Current outfit")
            stream.uint8(self.addon)
            
        if config.allowMounts:
            mounts = []
            for mount in game.resource.mounts:
                if len(mounts) == stream.maxMounts:
                    break
                if mount and self.canUseMount(mount.name):
                    mounts.append(mount)
                
            stream.uint8(len(mounts))
            for mount in mounts:
                stream.uint16(mount.cid)
                stream.string(mount.name)
        else:
            stream.uint8(0)
            
        stream.send(self.client)

    def setWindowHandler(self, windowId, callback):
        self.windowHandlers[windowId] = callback
        
    def textWindow(self, item, canWrite=False, maxLen=0xFF, text="", writtenBy="", timestamp=0):
        stream = self.packet(0x96)
        
        self.windowTextId += 1
        item._windowTextId = self.windowTextId
        
        stream.uint32(self.windowTextId)
        
        stream.uint16(item.cid)
        if canWrite:
            stream.uint16(maxLen)
            stream.string(text)
        else:
            stream.uint16(len(text))
            stream.string(text)
        
        stream.string(writtenBy)
        if timestamp:
            timestamp = datetime.datetime.fromtimestamp(timestamp)

            stream.string("%d/%d/%d - %d:%d" % (timestamp.day, timestamp.month, timestamp.year, timestamp.hour, timestamp.minute))
        else:
            stream.string("")
        
        stream.send(self.client)
        return self.windowTextId

    def houseWindow(self, text):
        stream = self.packet(0x97)
        self.windowTextId += 1
        
        stream.uint8(0) # Unused in PyOT
        stream.uint32(self.windowTextId)
        stream.string(text)
        stream.send(self.client)
        
        return self.windowTextId
        
    def stopAutoWalk(self):
        ret = self.stopAction()

        self.cancelWalk(self.direction)
    
    def windowMessage(self, text):
        stream = self.packet(0x15)
        stream.string(text)
        stream.send(self.client)
    
    def cancelMessage(self, message):
        self.message(message, 'MSG_STATUS_SMALL')
        
    def notPossible(self):
        self.cancelMessage("Sorry, not possible.")

    def notPickupable(self):
        self.cancelMessage("You cannot take this object.")
        
    def tooHeavy(self):
        self.cancelMessage("This object is too heavy for you to carry.")
        
    def outOfRange(self):
        self.cancelMessage("Destination is out of range.")

    def notEnoughRoom(self):
        self.cancelMessage("There is not enough room.")
        
    def exhausted(self):
        self.cancelMessage("You are exhausted.")

    def needMagicItem(self):
        self.cancelMessage("You need a magic item to cast this spell.")
    
    def notEnough(self, word):
        self.cancelMessage("You do not have enough %s." % word)

    def onlyOnCreatures(self):
        self.cancelMessage("You can only use it on creatures.")
        
    def updateContainer(self, container, parent=False, update=True):
        if parent and update:
            self.openContainers[self.openContainers.index(container.parent)] = container # Replace it in structure
        self.openContainer(container, parent, update)

    def updateAllContainers(self):
        for container in self.openContainers:
            parent = False
            try:
                parent = bool(container.parent)
            except:
                pass
            self.openContainer(container, parent=parent, update=True)
        stream = self.packet()
        for slot in xrange(enum.SLOT_FIRST,enum.SLOT_LAST):
            if self.inventory[slot-1]:
                stream.uint8(0x78)
                stream.uint8(slot)
            
                stream.item(self.inventory[slot-1])
            else:
                stream.uint8(0x79)
                stream.uint8(slot)
        stream.send(self.client)
        
    def openContainer(self, container, parent=False, update=False):
        if update or not container in self.openContainers:
            stream = self.packet(0x6E)
            
            if not update:
                container.opened = True
                self.openContainers.append(container)
            
            stream.uint8(self.openContainers.index(container))
            
            stream.uint16(container.cid)
            stream.string(container.rawName())
            
            stream.uint8(container.containerSize)
            stream.uint8(parent)
            stream.uint8(len(container.container.items))
            
            for item in container.container.items:
                stream.item(item)
                
            stream.send(self.client)
            
    def closeContainer(self, container):
        try:
            index = self.openContainers.index(container)
        except:
            container.opened = False
            return
            
        def end():
            try:
                stream = self.packet(0x6F)
                stream.uint8(index)
                self.openContainers.remove(container)
                container.opened = False
                stream.send(self.client)
            except:
                pass
        
        def callOpen(): game.scriptsystem.get('use').run(container, self, end, position=StackPosition(0xFFFF, 0, 0, 0), index=index)
        
        game.scriptsystem.get('close').run(container, self, callOpen, index=index)


    def closeContainerId(self, openId):
        try:
            container = self.openContainers[openId]
            
            def end():
                stream = self.packet(0x6F)
                stream.uint8(openId)
                del self.openContainers[openId]
                container.opened = False
                stream.send(self.client)
            
            game.scriptsystem.get('close').run(container, self, end, index=openId)
            return True
            
        except:
            return False

    def arrowUpContainer(self, openId):
        bagFound = self.openContainers[openId]
                
        if bagFound.parent:
            bagFound.parent.opened = True
            bagFound.opened = False
            self.openContainers[openId] = bagFound.parent
            
            def end():
                self.updateContainer(self.openContainers[openId], True if self.openContainers[openId].parent else False)
                
            game.scriptsystem.get('close').run(bagFound, self, end, index=openId)
            

    # Item to container
    def addItem(self, item, placeOnGround=True):
        ret = None
        if self.inventory[2]:
            try:
                ret = self.itemToContainer(self.inventory[2], item)
            except:
                ret = False
        else:
            ret = False
            
        if ret == False and not self.inventory[9]:
            if self.addCache(item) != False:
                self.inventory[9] = item
                stream = self.packet()
                stream.addInventoryItem(10, self.inventory[9])
                stream.send(self.client)            
                return True
        if ret == False and placeOnGround:
            tile = game.map.getTile(self.position)
            tile.placeItem(item)
            game.engine.updateTile(self.position, tile)
            return True
        elif ret == False:
            return False

        return True
            
    def itemToContainer(self, container, item, count=None, recursive=True, stack=True, placeOnGround=True, streamX=None):
        stream = streamX
        update = False
        
        if not streamX:
            stream = self.packet()
        
        if not count:
            count = 1 if item.count == None else item.count
        
        try:
            self.inventoryCache[container.itemId].index(container)
            update = True
        except:
            pass
        
        # Find item to stack with
        if stack and item.stackable and count < 100:
            slot = 0
            bags = [container]
            for bag in bags:
                for itemX in container.container.items:
                    if itemX.itemId == item.itemId and itemX.count < 100:
                        total = itemX.count + count
                        Tcount = min(total, 100)
                        count = total - Tcount
                        if update:
                            ret = self.modifyCache(itemX, itemX.count - Tcount)
                            if ret == False:
                                tile = game.map.getTile(self.position)
                                tile.placeItem(item)
                                game.engine.updateTile(self.position, tile)
                                self.tooHeavy()
                                return
                                
                        itemX.count = Tcount        

                        
                        # Is it a open container, if so, send item update
                        if bag in self.openContainers:
                            stream.updateContainerItem(self.openContainers.index(bag), slot, itemX)
                        

                            
                        if not count:
                            break
                    
                    elif recursive and itemX.containerSize and itemX != bag:
                        bags.append(itemX) # Found a container for recursive
                    
                    slot += 1
                
                if not count:
                    break
                    
                slot = 0
  
        if count:
            # Add item
            if self.inventoryWeight - ((item.weight or 0) * (item.count or 1)) < 0:
                self.tooHeavy()
                return False
                
            if recursive:
                info = container.container.placeItemRecursive(item)
            else:
                info = container.container.placeItem(item)
            
            if item.decayCreature:
                item.decayCreature = self
                
            if item.decayPosition:
                item.decayPosition = (0xFFFF, 65)
                
            if info == None:
                return False # Not possible
                
            if recursive and info and info.opened:
                stream.addContainerItem(self.openContainers.index(info), item)
                    
            elif container.opened:
                stream.addContainerItem(self.openContainers.index(container), item)
            
            if update:
                self.addCache(item, container)
                
        if not streamX:
            if update:
                self.refreshStatus(stream)
            stream.send(self.client)
            
        return True

    def itemToUse(self, item):
        # Means, right hand, left hand, ammo or bag. Stackable only
        if not self.inventory[4]:
            self.inventory[4] = item
            stream = self.packet()
            stream.addInventoryItem(5, self.inventory[4])
            stream.send(self.client)
            return True
        elif self.inventory[4].itemId == item.itemId and self.inventory[4].count < 100:
            prevCount = self.inventory[4].count
            self.inventory[4].count = min(100, prevCount + item.count)
            item.count = (prevCount + item.count) - self.inventory[4].count
            stream = self.packet()
            stream.addInventoryItem(5, self.inventory[4])
            stream.send(self.client)            
        if item.count:
            if not self.inventory[5]:
                self.inventory[5] = item
                stream = self.packet()
                stream.addInventoryItem(6, self.inventory[5])
                stream.send(self.client)
                return True
            elif self.inventory[5].itemId == item.itemId and self.inventory[5].count < 100:
                prevCount = self.inventory[5].count
                self.inventory[5].count = min(100, prevCount + item.count)
                item.count = (prevCount + item.count) - self.inventory[5].count  
                stream = self.packet()
                stream.addInventoryItem(6, self.inventory[5])
                stream.send(self.client)
                
        if item.count:
            if not self.inventory[9]:
                self.inventory[9] = item
                stream = self.packet()
                stream.addInventoryItem(10, self.inventory[0])
                stream.send(self.client)
                return True
            elif self.inventory[9].itemId == item.itemId and self.inventory[9].count < 100:
                prevCount = self.inventory[5].count
                self.inventory[9].count = min(100, prevCount + item.count)
                item.count = (prevCount + item.count) - self.inventory[9].count  
                stream = self.packet()
                stream.addInventoryItem(10, self.inventory[9])
                stream.send(self.client) 
                
        if item.count and self.inventory[2]:
            return self.itemToContainer(self.inventory[2], item)
        elif item.count:
            return False
        return True
    # Item To inventory slot
    def itemToInventory(self, item, slot=None, stack=True):
        if slot == None:
            slot = item.slotId()
            if not slot:
                return False
        
        if stack and item.stackable and item.itemId == self.inventory[slot-1].itemId and self.inventory[slot-1].count+item.count <= 100:
            self.inventory[slot-1].count += item.count
        else:
            self.inventory[slot-1] = item
            
        stream = self.packet()
        stream.addInventoryItem(slot, self.inventory[slot-1])
        stream.send(self.client)
        
        return True

    def updateInventory(self, slot):
        stream = self.packet()
        if self.inventory[slot-1].stackable and not self.inventory[slot-1].count:
            stream.removeInventoryItem(slot)
        else:
            stream.addInventoryItem(slot, self.inventory[slot-1])
        stream.send(self.client)        
    # Channel system
    def openChannels(self):
        stream = self.packet(0xAB)
        channels = game.chat.getChannels(self)
        
        channels2 = game.scriptsystem.get("requestChannels").runSync(self, channels=channels)

        if type(channels2) == dict:
            channels = channels2
            
        stream.uint8(len(channels))
        for channelId in channels:
            stream.uint16(channelId)
            stream.string(channels[channelId].name)
            
        stream.send(self.client)
    
    def openChannel(self, id):
        
        if game.scriptsystem.get("joinChannel").runSync(self, None, channelId=id):
            stream = self.packet(0xAC)
            channel = game.chat.getChannel(id)
            
            if not channel:
                print id
                return self.cancelMessage("Channel not found.")
                
            stream.uint16(id)
            stream.string(channel.name)
            
            # TODO: Send members for certain channels
            stream.uint32(0)
            
            stream.send(self.client)
            channel.addMember(self)

    def openPrivateChannel(self, between):
        # Self open
        if not self.isChannelOpen(between):
            self._openChannels[between.name()] = [0xFFFF, between]
            if between.isPlayer():
                stream = self.packet(0xAD)
            else:    
                stream = self.packet(0xB2)
                stream.uint16(0xFFFF)
                
            stream.string(between.name())
            stream.send(self.client)
        
        # Notify between if required.
        if not between.isChannelOpen(self):
            between.openPrivateChannel(self)
            
        return 0xFFFF
        
    def closePrivateChannel(self, between):
        if between.name() in self._openChannels:
            betweenObj = self._openChannels[between.name()]
            stream = self.packet(0xB3)
            stream.uint16(betweenObj[0])
            stream.send(self.client)
        
    def closeChannel(self, id):
        channel = game.chat.getChannel(id)
        channel.removeMember(self)
        
        game.scriptsystem.get("leaveChannel").run(self, None, channelId=id)

    def isChannelOpen(self, between):
        try:
            return self._openChannels[between.name()]
        except:
            return False
            
    def channelMessage(self, text, channelType="MSG_CHANNEL", channelId=0):
        try:
            members = game.chat.getChannel(channelId).members
        except:
            members = []
            
        members2 = game.scriptsystem.get("getChannelMembers").runSync(channelId, self, None, channelId=channelId, text=text, type=channelType, members=members)
        if not members and type(members2) != list:
            return False
            
        elif type(members2) == list:
            members = members2
            
        if not members:
            return False # No members
                    
        for player in members:
            stream = player.packet(0xAA)
            stream.uint32(1)
            stream.string(self.data["name"])
            if self.isPlayer():
                stream.uint16(self.data["level"])
            else:
                stream.uint16(0)
            stream.uint8(stream.enum(channelType))
            if channelType in ("MSG_CHANNEL_MANAGEMENT", "MSG_CHANNEL", "MSG_CHANNEL_HIGHLIGHT"):
                stream.uint16(channelId)
            
            stream.string(text)
            stream.send(player.client)
            
        return True

    def privateChannelMessage(self, text, receiver, channelType="MSG_CHANNEL"):
        player = game.engine.getPlayer(receiver)
        stream = player.packet(0xAA)
        stream.uint32(1)
        stream.string(self.data["name"])
        stream.uint16(self.data["level"])
        stream.uint8(stream.enum(channelType))
        stream.string(text)
        stream.send(player.client)
            
        return True
        
    def isPrivate(self, name):
        try:
            return self.openChannels[name]
        except:
            pass

    def notifyPrivateSay(self, sayer, text):
        pass # Not supported yet
        
    # Death stuff
    def sendReloginWindow(self, percent=0):
        stream = self.packet(0x28)
        stream.uint8(percent)
        stream.send(self.client)
        
    def onDeath(self):
        
        self.sendReloginWindow()
            
        tile = game.map.getTile(self.position)

        corpse = game.item.Item(3058)
        game.scriptsystem.get("death").runSync(self, self.lastDamager, corpse=corpse)
        if not self.alive and self.data["health"] < 1:
            corpse.decay(self.position)
            splash = game.item.Item(game.enum.FULLSPLASH)
            splash.fluidSource = game.enum.FLUID_BLOOD
            splash.decay(self.position)
            
            tile.placeItem(corpse)
            tile.placeItem(splash)
            
            try:
                tile.removeCreature(self)
            except:
                pass
            for spectator in game.engine.getSpectators(self.position, ignore=[self]):
                stream = spectator.packet(0x69)
                stream.position(pos)
                stream.tileDescription(tile)
                stream.uint8(0x00)
                stream.uint8(0xFF)
                stream.send(spectator)
        
    def onSpawn(self):
        if not self.data["health"]:
            self.data["health"] = self.data["healthmax"]
            self.data["mana"] = self.data["manamax"]
            game.scriptsystem.get("respawn").run(self)
            import data.map.info
            self.teleport(data.map.info.towns[self.data['town_id']][1])

    # Damage calculation:
    def damageToBlock(self, dmg, type):
        if type == game.enum.MELEE:
            # Armor and defence
            armor = 0
            defence = 0
            for item in self.inventory:
                if item:
                    armor += item.armor or 0
                    defence += item.defence or 0
            
            # Reduce armor to fit action + set defence still
            defRate = 10
            if self.modes[1] == game.enum.OFFENSIVE:
                armor = armor * 0.5
                defRate = 5
            elif self.modes[1] == game.enum.BALANCED:
                armor = armor * 0.75
                defRate = 7
                
            # Recalculate damage by defence rate
            dmg = dmg - ((defence * defRate) / 100.0) - (dmg / 100) * armor
                
            return dmg - armor
        return dmg

    # Loading:
    def __buildInventoryCache(self, container):
        for item in container.container.items:
            weight = item.weight
            
            item.inContainer = container # Funny call to simplefy lookups
            item.inPlayer = self
            
            if item.decayCreature:
                item.decayCreature = self
            if weight:
                self.inventoryWeight += weight * (item.count or 1)
            try:
                self.inventoryCache[item.itemId].append(item)
                self.inventoryCache[item.itemId][0] += item.count or 1
            except:
                self.inventoryCache[item.itemId] = [item.count or 1, item]
                
            if item.container:
                self.__buildInventoryCache(item)
                
    def unpickleInventory(self, inventoryData):
        try:
            self.inventory = pickle.loads(inventoryData)
        except:
            print "Broken inventory (blame MySQL, it usually means you killed the connection in the middle of a save)"
            self.inventory = [Item(8820), Item(2125), Item(1987), Item(2463), None, Item(7449), None, None, None, Item(2546, 20), None]
            
        # Generate the inventory cache
        for item in self.inventory:
            if isinstance(item, game.item.Item):
                weight = item.weight
                if item.decayCreature:
                    item.decayCreature = self
                if weight:
                    self.inventoryWeight += weight * (item.count or 1)
                try:
                    self.inventoryCache[item.itemId].append(item)
                    self.inventoryCache[item.itemId][0] += item.count or 1
                except:
                    self.inventoryCache[item.itemId] = [item.count or 1, item]
                
                if item.container:
                    self.__buildInventoryCache(item)
        
    # Saving
    def pickleInventory(self):
        return game.engine.fastPickler(self.inventory)
        
    def pickleDepot(self):
        return game.engine.fastPickler(self.depot)
        
    def _saveQuery(self, force=False):
        print self.doSave
        if not self.doSave:
            return
            
        depot = ""
        storage = ""
        skills = ""
        inventory = ""
        
        if self.saveDepot or force:
            depot = ", `depot` = '%s'" % self.pickleDepot()
            self.saveDepot = False
            
        if self.saveStorage or force:
            storage = ", `storage` = '%s'" % otjson.dumps(self.storage)
            self.saveStorage = False
            
        if self.saveSkills or force:
            skills = ", `skills` = '%s'" % otjson.dumps(self.skills)
            self.saveSkills = False
            
        if self.saveInventory or force:
            inventory = ", `inventory` = '%s'" % self.pickleInventory()
            self.saveInventory = False
            
        extra = "%s%s%s%s" % (depot, storage, skills, inventory)
        
        if self.saveData or extra or force: # Don't save if we 1. Change position, or 2. Just have stamina countdown
            return "UPDATE `players` SET `experience` = %s, `manaspent` = %s, `mana`= %s, `health` = %s, `soul` = %s, `stamina` = %s, `direction` = %d, `posx` = %d, `posy` = %d, `posz` = %d"+ extra +" WHERE `id` = %d", (self.data["experience"], self.data["manaspent"], self.data["mana"], self.data["health"], self.data["soul"], self.data["stamina"] * 1000, self.direction, self.position.x, self.position.y, self.position.z, self.data["id"])

    def save(self, force=False):
        if self.doSave:
            argc = self._saveQuery(force)
            if argc:
                sql.conn.runOperation(*argc)

    def saveSkills(self):
        sql.conn.runOperation("UPDATE `players` SET `skills`= %s WHERE `id` = %d", (otjson.dumps(self.skills), self.data["id"]))
    

    def saveExperience(self):
        sql.conn.runOperation("UPDATE `players` SET `experience`= %d, `manaspent` = %d WHERE `id` = %d", (self.data["experience"], self.data["manaspent"], self.data["id"]))
    

    def saveStorage(self):
        sql.conn.runOperation("UPDATE `players` SET `storage`= %s WHERE `id` = %d", (otjson.dumps(self.storage), self.data["id"]))

    # Shopping
    def setTrade(self, npc):
        if not self.openTrade:
            self.openTrade = npc

            
    def closeTrade(self):
        if self.openTrade:
            stream = self.packet(0x7C)
            stream.send(self.client)
            self.openTrade = None
        else:
            stream = self.packet(0x7F)
            stream.send(self.client)            

    def getMoney(self):
        if not self.inventory[2]:
            return 0
    
        money = 0
        for item in self.inventory[2].container.getRecursive():
            currency = item.currency
            if currency:
                money += currency * item.count
        
        return money
        
    def removeMoney(self, amount):
        moneyItems = []
        money = 0
        for item, bag, pos in self.inventory[2].container.getRecursiveWithBag():
            currency = item.currency
            if currency:
                money += currency * item.count   
                moneyItems.append((item, bag, pos))
                if money >= amount:
                    break
                    
        if money >= amount:
            removedMoney = 0
            for i in moneyItems[:-1]:
                removedMoney += i[0].currency * i[0].count
                i[1].removeItem(i[0])
            
            last = moneyItems[-1]
            count = 0
            currency = last[0].currency
            for i in xrange(last[0].count):
                removedMoney += currency
                count += 1
                if removedMoney >= amount:
                    last[0].count -= count
                    if last[0].count <= 0:
                        last[1].removeItem(last[0])
                    break
            
            addBack = removedMoney - amount
            if addBack: # Add some money back
                for x in game.enum.MONEY_MAP:
                    if addBack >= x[1]:
                        coins = int(addBack / x[1])
                        addBack = addBack % x[1]
                        while coins:
                            count = min(100, coins)
                            self.itemToContainer(self.inventory[2], game.item.Item(x[0], count))
                            coins -= count
                            
                    if not addBack:
                        break
            self.updateAllContainers()
            return amount
            
        else:
            return 0

    def addMoney(self, amount):
        for x in game.enum.MONEY_MAP:
            if amount >= x[1]:
                coins = int(amount / x[1])
                amount = amount % x[1]
                while coins:
                    count = min(100, coins)
                    self.itemToContainer(self.inventory[2], game.item.Item(x[0], count))
                    coins -= count
                if not amount:
                    break
        return True

    # Storage
    def setStorage(self, field, value):
        self.storage[field] = value
        self.saveStorage = True
        
    def getStorage(self, field, default=None):
        try:
            return self.storage[field]
        except:
            return default

    def modifyStorage(self, field, change):
        self.storage[field] += change
        self.saveStorage = True

    def removeStorage(self, field):
        try:
            del self.storage[field]
            self.saveStorage = True
        except:
            pass

    # Depot stuff
    def getDepot(self, depotId):
        if depotId in self.depot:
            return self.depot[depotId]
        else:
            return []
            
    def setDepot(self, depotId, storage):
        self.depot[depotId] = storage
        self.saveDepot = True
        
    # Stuff from protocol:
    def handleSay(self, channelType, channelId, reciever, text):
        if len(text) > config.maxLengthOfSay:
            self.message("Message too long")
            return
            
        splits = text.split(" ")
        mode = channelType
        if channelId == 1:
            if splits[0] == "#y":
                mode = game.enum.MSG_SPEAK_YELL
                del splits[0]
            elif splits[0] == "#w":
                mode = game.enum.MSG_SPEAK_WHISPER
                del splits[0]

        def endCallback():
            
            if channelType in (game.enum.MSG_SPEAK_SAY, game.enum.MSG_SPEAK_YELL, game.enum.MSG_SPEAK_WHISPER):
                if mode == game.enum.MSG_SPEAK_SAY:
                    self.say(' '.join(splits[0:]))
                    
                elif mode == game.enum.MSG_SPEAK_YELL:
                    self.yell(' '.join(splits[0:]))
                
                elif mode == game.enum.MSG_SPEAK_WHISPER:
                    self.whisper(' '.join(splits[0:]))
            
            elif channelType == game.enum.MSG_CHANNEL:
                self.channelMessage(text, "MSG_CHANNEL", channelId)
            
            #elif channelType == game.enum.MSG_PRIVATE_TO:
                self.privateChannelMessage(text, reciever, "MSG_PRIVATE_FROM")
                
            for creature in game.engine.getCreatures(self.position):
                creature.playerSay(self, text, channelType, channelId or reciever)

        def part1():
            game.scriptsystem.get("talkaction").run(text, self, endCallback, text=' '.join(splits[0:]))
            
        if len(splits) > 1:
            game.scriptsystem.get("talkactionFirstWord").run(splits[0], self, part1, text=' '.join(splits[1:]))
        else:
            part1()   
            
    def attackTarget(self):
        if self.target and self.target.isAttackable(self) and self.inRange(self.target.position, 1, 1):
            if not self.target.data["health"]:
                self.target = None
            else:
                factor = 1
                if self.modes[1] == game.enum.BALANCED:
                    factor = 0.75
                elif self.modes[1] == game.enum.DEFENSIVE:
                    factor = 0.5 
                    
                if not self.inventory[5]:
                    skillType = game.enum.SKILL_FIST
                    dmg = -random.randint(0, round(config.meleeDamage(1, self.getActiveSkill(skillType), self.data["level"], factor)))
                    
                else:
                    skillType = self.inventory[5].weaponType
                    dmg = -random.randint(0, round(config.meleeDamage(self.inventory[5].attack, self.getActiveSkill(skillType), self.data["level"], factor)))
                    
                    # Critical hit
                    if config.criticalHitRate > random.randint(1, 100):
                        dmg = dmg * config.criticalHitMultiplier
                        self.criticalHit()
                        
                if dmg != 0:
                    self.target.onHit(self, dmg, game.enum.MELEE)
                    self.skillAttempt(skillType)
                        
        if self.target:        
            self.targetChecker = reactor.callLater(config.meleeAttackSpeed, self.attackTarget)

    def criticalHit(self):
        self.message("You strike a critical hit!", 'MSG_STATUS_CONSOLE_RED')
        
    def setAttackTarget(self, cid):
        if self.targetMode == 1 and self.target:
            self.targetMode = 0
            self.target = None
            try:
                self.targetChecker.cancel()
            except:
                pass
            return
            
        if cid in allCreatures:
            if allCreatures[cid].isAttackable(self):
                target = allCreatures[cid]
                ret = game.scriptsystem.get('target').runSync(self, target, attack=True)
                if ret == False:
                   return
                elif ret != None:
                    self.target = ret
                else:
                    self.target = target
                    
                self.targetMode = 1
            else:
                return
        else:
            return self.notPossible()
        
        if not self.target:
            return self.notPossible()
            
        
        if self.modes[1] == game.enum.CHASE:
            print "did"
            game.engine.autoWalkCreatureTo(self, self.target.position, -1, True)
            self.target.scripts["onNextStep"].append(self.followCallback)

        try:
            self.targetChecker.cancel()
        except:
            pass        
        self.attackTarget()
        
    def followCallback(self, who):
        if self.target == who:
            game.engine.autoWalkCreatureTo(self, self.target.position, -1, True)
            self.target.scripts["onNextStep"].append(self.followCallback)
            
    def setFollowTarget(self, cid):
        if self.targetMode == 2:
            self.targetMode = 0
            self.target = None
            return
            
        if cid in allCreatures:
            target = allCreatures[cid]
            ret = game.scriptsystem.get('target').run(self, target, attack=True)
            if ret == False:
                return
            elif ret != None:
                self.target = ret
            else:
                self.target = target
                    
            self.targetMode = 2
            game.engine.autoWalkCreatureTo(self, self.target.position, -1, True)
            self.target.scripts["onNextStep"].append(self.followCallback)
        else:
            self.notPossible()
            
    # Skull and emblems and such
    def square(self, creature, color=27):
        stream = self.packet(0x86)
        stream.uint32(creature.cid)
        stream.uint8(color)
        stream.send(self.client)

    # Quest system
    def beginQuest(self, questIdentifier):
        quests = self.getStorage('__quests')
        if not quests:
            quests = {}
            
        quests[questIdentifier] = [1, 0, False, time.time(), False] # Mission, completed steps, startTime, endTime
        
        self.setStorage('__quests', quests)

        if config.sendTutorialSignalUponQuestLogUpdate:
            self.tutorial(3)
            
    def progressQuest(self, questIdentifier):
        quests = self.getStorage('__quests')
        quests[questIdentifier][1] += 1
        self.setStorage('__quests', quests)

        if config.sendTutorialSignalUponQuestLogUpdate:
            self.tutorial(3)
            
    def progressQuestMission(self, questIdentifier):
        quests = self.getStorage('__quests')
        quests[questIdentifier][0] += 1
        self.setStorage('__quests', quests)

        if config.sendTutorialSignalUponQuestLogUpdate:
            self.tutorial(3)
            
    def finishQuest(self, questIdentifier):
        quests = self.getStorage('__quests')
        quests[questIdentifier][1] += 1 # Finish the last step
        quests[questIdentifier][2] = True
        quests[questIdentifier][4] = time.time()
        self.setStorage('__quests', quests)
        
        if config.sendTutorialSignalUponQuestLogUpdate:
            self.tutorial(3)
        
    def questLog(self):
        quests = self.getStorage('__quests')
        if not quests:
            quests = {}
        
        game.scriptsystem.get("questLog").runSync(self, None, questLog=quests)
        
        # Vertify the quests
        for quest in quests.copy():
            try:
                game.resource.getQuest(quest)
            except:
                print "Debug, ending quest %s" % quest
                del quests[quest]
                self.setStorage('__quests', quests)
        
        stream = self.packet(0xF0)
        stream.uint16(len(quests))
        for quest in quests:
            questObj = game.resource.getQuest(quest)
            if not questObj.missions:
                stream.uint16(0)
            stream.uint16(game.resource.reverseQuests[quest]+1)
            stream.string(questObj.name)
            stream.uint8(quests[quest][2])
        
        stream.send(self.client)
        
    def questLine(self, questIdentifier):
        quests = self.getStorage('__quests')
        questObj = game.resource.getQuest(questIdentifier)
        stream = self.packet(0xF1)
        stream.uint16(game.resource.reverseQuests[questIdentifier]+1)

        stream.uint8(questObj.missions[quests[questIdentifier][0]-1][1] + questObj.missions[quests[questIdentifier][0]-1][2])
        print questObj.missions[quests[questIdentifier][0]-1][1] + questObj.missions[quests[questIdentifier][0]-1][2]
        for i in xrange(quests[questIdentifier][0]):
            for x in xrange(questObj.missions[i][1], questObj.missions[i][2]):
                print x
                stream.string(questObj.missions[i][0] + (' (completed)' if quests[questIdentifier][1] > x else ''))
                stream.string(questObj.descriptions[x])
        
        stream.send(self.client)
        
    def questProgress(self, questIdentifier):
        quests = self.getStorage('__quests')
        try:
            return quests[questIdentifier][1]
        except:
            return 0
            
    def questStarted(self, questIdentifier):
        quests = self.getStorage('__quests')
        try:
            quests[questIdentifier]
            return True
        except:
            return False
            
    def questCompleted(self, questIdentifier):
        quests = self.getStorage('__quests')
        try:
            return quests[questIdentifier][2]
        except:
            return False
            
    # VIP system
    def getVips(self):
        vips = self.getStorage('__vips')
        if not vips:
            return []
        return vips

    @defer.inlineCallbacks
    def sendVipList(self):
        vips = self.getStorage('__vips')
        if not vips:
            return
 
        result = yield sql.conn.runQuery("SELECT `id`, `name` FROM players WHERE `id` IN (%s)" % (tuple(vips)))
        if result:
            stream = self.packet()
            for player in result:
                online = bool(player[1] in allPlayers and allPlayers[player[1]].client)
                stream.vip(player[0], player[1], online)
                if online:
                    pkg = allPlayers[player[1]].packet()
                    pkg.vipLogin(self.data["id"])
                    pkg.send(allPlayers[player[1]].client)
            stream.send(self.client)
            
    def addVip(self, playerId):
        vips = self.getStorage('__vips')
        if not vips:
            vips = [playerId]
        else:
            try:
                vips.index(playerId)
                return
            except:
                vips.append(playerId)
            
        self.setStorage('__vips', vips)
        self.sendVipList()

    @defer.inlineCallbacks
    def addVipByName(self, name):
        result = yield game.engine.getPlayerIDByName(name)
        if result:
            self.addVip(result)
            
    def removeVip(self, playerId):
        vips = self.getStorage('__vips')
        if not vips:
            return
        else:
            try:
                vips.remove(playerId)
            except:
                return
            
        self.setStorage('__vips', vips)
        #self.sendVipList()

    @defer.inlineCallbacks
    def removeVipByName(self, name):
        result = yield game.engine.getPlayerIDByName(name)
        if result:
            self.removeVip(result)
            
    def isVip(self, playerId):
        vips = self.getStorage('__vips')
        if not vips:
            return False
        else:
            try:
                vips.index(playerId)
                return True
            except:
                return False    
    # Exit
    def exit(self, message):
        stream = self.packet()
        stream.exit(message)
        stream.send(self.client)
        
    # Cleanup the knownCreatures
    def removeKnown(self, creature):
        cid = 0
        try:
            self.knownCreatures.remove(creature)
            creature.knownBy(self)
            cid = creature.cid
        except:
            pass
        return cid
        
    def checkRemoveKnown(self):
        dead = []
        for creature in self.knownCreatures:
            if not self.canSee(creature.position, radius=(16,16)):
                return self.removeKnown(creature)
            elif creature.data["health"] < 1:
                dead.append(creature)
        try:
            return self.removeKnown(dead.pop())
        except:
            return None
            
    # Outfit and mount
    def canWearOutfit(self, name):
        return self.getStorage('__outfit%s' % game.resource.reverseOutfits[name])
    
    def addOutfit(self, name):
        self.setStorage('__outfit%s' % game.resource.reverseOutfits[name], True)
        
    def removeOutfit(self, name):
        self.removeStorage('__outfit%s' % game.resource.reverseOutfits[name])
    
    def getAddonsForOutfit(self, name):
        return self.getStorage('__outfitAddons%s' % game.resource.reverseOutfits[name])
        
    def addOutfitAddon(self, name, addon):
        addons = self.getAddonsForOutfit(name)
        if addons & addon == addon:
            return
        else:
            addons += addon
            self.setStorage('__outfitAddons%s' % game.resource.reverseOutfits[name], addons)
            
    def removeOutfitAddon(self, name, addon):
        addons = self.getAddonsForOutfit(name)
        if addons & addon == addon:
            addons -= addon
            self.setStorage('__outfitAddons%s' % game.resource.reverseOutfits[name], addons)  
        else:
            return
    def canUseMount(self, name):
        return self.getStorage('__mount%s' % game.resource.reverseMounts[name])
    
    def addMount(self, name):
        self.setStorage('__mount%s' % game.resource.reverseMounts[name], True)
        
    def removeMount(self, name):
        self.removeStorage('__mount%s' % game.resource.reverseMounts[name])
        

    # Rates
    def getExperienceRate(self):
        return self.rates[0]
    def setExperienceRate(self, rate):
        self.rates[0] = rate
    def getRegainRate(self):
        return self.rates[4]
    def setRegainRate(self, rate):
        self.rates[4] = rate
        
    # Guild & party
    def guild(self):
        try:
            return game.guild.guilds[self.data["guild_id"]]
        except:
            return None
            
    def party(self):
        # We use party() here because we might need to check for things. this is a TODO or to-be-refactored.
        return self.partyObj
        
    # Trade
    def tradeItemRequest(self, between, items, confirm=False):
        if confirm:
            stream = self.packet(0x7D)
        else:
            stream = self.packet(0x7E)
            
        stream.string(between.name())
        _items = []
        itemCount = 0
        for item in items:
            _items.append(item)
            itemCount += 1
            if itemCount != 255 and item.containerSize:
                for i in item.container.items:
                    stream.item(i)
                    itemCount += 1
                    if itemCount == 255:
                        break
            elif itemCount == 255:
                break
                
        stream.uint8(itemCount)
        for i in _items:
            stream.item(i)
            
        stream.send(self.client)
        
    # Spell learning
    def canUseSpell(self, name):
        return self.getStorage("__ls%s" % name)
        
    def learnSpell(self, name):
        return self.setStorage("__ls%s" % name, True)
        
    def unlearnSpell(self, name):
        return self.setStorage("__ls%s" % name, False)