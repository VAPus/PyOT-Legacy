from game import enum, engine
from game.map import placeCreature, removeCreature, getTile
from twisted.python import log
import config
from collections import deque
import game.scriptsystem
from game.item import Item
from twisted.internet import reactor
from game.creature import Creature, CreatureBase, uniqueId, allCreatures
import time

import game.resource

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

class TibiaPlayer(Creature):
    def __init__(self, client, data):
        Creature.__init__(self, data, [int(data['posx']),int(data['posy']),int(data['posz'])])
        self.client = client
        
        self.speed = 220
        self.modes = [0,0,0]
        self.gender = 0
        self.base = anyPlayer
        self.knownCreatures = []
        self.openContainers = []
        self.doingSoulGain = False
        self.data["stamina"] = self.data["stamina"] / 1000 # OT milisec to pyot seconds
        self.targetChecker = None
        self._openChannels = {}
        self.idMap = []
        self.openTrade = None
        self.windowTextId = 0
        self.windowHandlers = {}
        
        self.solid = not config.playerWalkthrough

        self.inventoryWeight = 0
        # Direction
        self.direction = self.data["direction"]
        del self.data["direction"]

        # Inventory
        self.inventoryCache = {}
        if self.data['inventory']:
            self.unpickleInventory(self.data['inventory'])
        else:
            self.inventory = [Item(8820), Item(2125), Item(1987), Item(2463), None, Item(7449), None, None, None, Item(2546, 20), None]
            for item in self.inventory:
                if isinstance(item, game.item.Item):
                    weight = item.weight
                    if weight:
                        self.inventoryWeight += weight * (item.count or 1)
                    try:
                        self.inventoryCache[item.itemId].append(item)
                        self.inventoryCache[item.itemId][0] += item.count or 1
                    except:
                        self.inventoryCache[item.itemId] = [item.count or 1, item]
                    
                    if item.containerSize:
                        self.__buildInventoryCache(item.container)
        del self.data['inventory']
        
        # Depot, (yes, we load it here)
        if self.data['depot']:
            self.depot = pickle.loads(self.data['depot'])
        else:
            self.depot = {} # {depotId : inventoryList}
            
        del self.data['depot']
        
        # Calculate level from experience
        vocation = self.getVocation()
        level = 0
        bit = 32
        cache = 2**bit
        while bit:
            if config.totalExpFormula(level + cache) > self.data["experience"]:
                bit -= 1
                if bit == 0:
                    if config.totalExpFormula(level + 1) > self.data["experience"]:
                        level += 1
                    break
                else:
                    cache = 2 ** bit
            else:
                level += cache
        
        # Calculate magic level from manaspent
        maglevel = 0
        bit = 12
        cache = 2 ** bit
        while bit:
            if config.totalMagicLevelFormula(maglevel + cache, vocation.mlevel) > self.data["manaspent"]:
                bit -= 1
                if bit == 0:
                    if config.totalMagicLevelFormula(maglevel + 1, vocation.mlevel) > self.data["manaspent"]:
                        maglevel += 1
                    break
                else:
                    cache = 2 ** bit
            else:
                maglevel += cache

        self.data["maglevel"] = maglevel
        self.setLevel(level, False)
        self.speed = min(220.0 + (2 * data["level"]-1), 1500.0)

        # Stamina loose
        if self.data["stamina"]:
            def loseStamina():
                self.data["stamina"] -= 60
                if self.data["stamina"] < 0:
                    self.data["stamina"] = 0
                else:
                    game.engine.safeCallLater(60, loseStamina)
                
                if self.data["stamina"] < (42*3600):
                    self.refreshStatus()
                    
            game.engine.safeCallLater(60, loseStamina)
        

        # Storage & skills
        try:
            self.skills = otjson.loads(self.data["skills"])
            if len(self.skills) != (game.enum.SKILL_LAST*2)+1:
                raise
        except:
            self.skills = []
            for i in xrange(game.enum.SKILL_FIRST, (game.enum.SKILL_LAST*2)+2):
                self.skills.append(10)
            
        del self.data["skills"]
        
        if self.data["storage"]:
            self.storage = otjson.loads(self.data["storage"])
        else:
            self.storage = {}
            
        del self.data["storage"]
        
    def generateClientID(self):
        return 0x10000000 + uniqueId()

    def isPlayer(self):
        return True

    def sexPrefix():
        if self.data["sex"] == 1:
            return "He"
        else:
            return "She"
            
    def description(self, isSelf=False):
        if isSelf:
            output = "You see yourself. You are %s." % self.getVocation().description()
        else:
            output = "You see %s (Level %d). %s is %s." % (self.name, self.data["level"], self.sexPrefix(), self.getVocation().description())
        return output
        
    def packet(self, *args):
        return self.client.protocol.Packet(*args)
        
    def sendFirstPacket(self):
        
        stream = self.packet(0x0A)

        stream.uint32(self.clientId()) # Cid
        stream.uint16(config.drawingSpeed) # Drawing speed
        stream.uint8(1) # Rule violations?

        #stream.violation(0)
        
        stream.uint8(0x64) # Map description
        stream.position(self.position)
        stream.mapDescription((self.position[0] - 8, self.position[1] - 6, self.position[2]), 18, 14, self)

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
        stream.icons(0)

        stream.magicEffect(self.position, 0x03)
        stream.send(self.client)
        
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
        
    def findItem(self, position, stackpos=1, sid=None):
        # Option 1, from the map:
        if position:
            if position[0] != 0xFFFF:
                return game.map.getTile(position).getThing(stackpos)
            
            # Option 2, the inventory
            elif position[1] < 64:
                return self.inventory[position[1]-1]
            
            # Option 3, the bags, if there is one ofcource
            elif self.inventory[2]:
                try:
                    bag = self.openContainers[position[1] - 64]
                except:
                    return
                    
                item = bag.container.getThing(position[2])
                return item

        # Option 4, find any item the player might posess
        if sid:
            # Inventory
            try:
                return self.inventoryCache[sid][-1]
            except:
                return None
            
    def findItemWithPlacement(self, position, stackpos=1, sid=None):
        # Option 1, from the map:
        if position:
            if position[0] != 0xFFFF:
                return (0, game.map.getTile(position).getThing(stackpos), game.map.getTile(position)) if isinstance(game.map.getTile(position).getThing(stackpos), game.item.Item) else None
            
            # Option 2, the inventory
            elif position[1] < 64:
                return (1, self.inventory[position[1]-1]) if self.inventory[position[1]-1] else None
            
            # Option 3, the bags, if there is one ofcource
            else:
                try:
                    bag = self.openContainers[position[1] - 64]
                except:
                    return
                item = bag.container.getThing(position[2])
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
                for item in bag.container.items:
                    if item.itemId == itemId:
                        items.append((2, item, bag, bag.container.items.index(item)))
                        if count:
                            foundCount += item.count
                            
                            if foundCount >= count: break
                        else:
                            break
                    elif item.containerSize:
                        bags.append(item)
        

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

    def replaceItem(self, position, stackpos, item):
        # Option 1, from the map:
        if position:
            if position[0] != 0xFFFF:
                tile = game.map.getTile(position)
                tile.things[stackpos] = item
                game.engine.updateTile(position, tile)
                
            # Option 2, the inventory
            elif position[1] < 64:
                sendUpdate = False
                currItem = self.inventory[position[1]-1]
                if currItem:
                    # Update cached data
                    if self.removeCache(currItem):
                        sendUpdate = True
                self.inventory[position[1]-1] = item
                if self.addCache(item):
                    sendUpdate = True
                    
                if sendUpdate:
                    self.refreshStatus()
                
                self.updateInventory(position[1])
            
            # Option 3, the bags, if there is one ofcource
            elif self.inventory[2]:
                update = False
                try:
                    bag = self.openContainers[position[1] - 64]
                except:
                    return
                
                try:
                    self.inventoryCache[bag.itemId].index(bag)
                    currItem = bag.container.items[position[2]]
                    if currItem:
                        if self.removeCache(currItem):
                            update = True
                            
                    if self.addCache(item):
                        update = True
                except:
                    pass
                
                bag.container.items[position[2]] = item
                stream = self.packet()
                stream.updateContainerItem(position[1] - 64, position[2], item)
                if update:
                    self.refreshStatus(stream)
                stream.send(self.client)
            
    def removeItem(self, position, stackpos):
        # Option 1, from the map:
        if position:
            if position[0] != 0xFFFF:
                tile = game.map.getTile(position)
                del tile.things[position[2]]
                game.engine.updateTile(position, tile)
                
            # Option 2, the inventory
            elif position[1] < 64:
                if self.removeCache(self.inventory[position[1]-1]):
                    self.refreshStatus()
                self.inventory[position[1]-1] = None
                self.updateInventory(position[1])
            
            # Option 3, the bags, if there is one ofcource
            elif self.inventory[2]:
                update = False
                try:
                    bag = self.openContainers[position[1] - 64]
                except:
                    return
                
                try:
                    self.inventoryCache[bag.itemId].index(bag)
                    currItem = bag.container.items[position[2]]
                    if currItem:
                        if self.removeCache(currItem):
                            update = True
                except:
                    pass
                
                del bag.container.items[position[2]]
                stream = self.packet()
                stream.removeContainerItem(position[1] - 64, position[2])
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
            self.inventoryCache[item.itemId].remove(item)
            self.inventoryCache[item.itemId][0] -= item.count or 1
            weight = item.weight
            if weight:
                self.inventoryWeight -= weight * (item.count or 1)
                print "3"
                return True
        except:
            pass
        
    def addCache(self, item):
        try:
            print "Add to cache ",item
            self.inventoryCache[item.itemId].append(item)
            self.inventoryCache[item.itemId][0] += item.count or 1
        except:
            self.inventoryCache[item.itemId] = [item.count or 1, item]
            
        weight = item.weight
        if weight:
            self.inventoryWeight += weight * (item.count or 1)
            return True
            
    def modifyCache(self, item, count):
        if not count: return
        
        try:
            self.inventoryCache[itemId][0] += count
            weight = item.weight
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
        
    def modifyExperience(self, exp):
        up = True
        if exp < 0:
            up = False
        
        self.data["experience"] += exp
        
        if up:
            level = 0
            self.message("You gained %d experience points." % exp, 'MSG_EXPERIENCE', color=config.experienceMessageColor, value=exp)
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

    # Skills
    def addSkillLevel(self, skill, levels):
        self.skills[skill] += levels
        self.skills[skill + game.enum.SKILL_LAST + 1] += levels
        goal = config.skillFormula(self.getVocation().meleeSkill, self.skills[skill])
        self.setStorage('__skill%d' % skill, 0)
        self.setStorage('__skillGoal%d' % skill, goal)
        
        self.refreshSkills()

    def tempAddSkillLevel(self, skill, level):
        self.skills[skill + game.enum.SKILL_LAST + 1] = self.skills[skill] + levels
        self.refreshSkills()
        
    def tempRemoveSkillLevel(self, skill):
        self.skills[skill + game.enum.SKILL_LAST + 1] = self.skills[skill]
        self.refreshSkills()

    def getActiveSkill(self, skill):
        return self.skills[skill + game.enum.SKILL_LAST + 1]
        
    # Soul
    def soulGain(self):
        def doSoulGain(gainOverX):
            self.modifySoul(1)
            if self.doingSoulGain - gainOverX >= time.time():
                game.engine.safeCallLater(gainOverX, doSoulGain, gainOverX)
            else:
                self.doingSoulGain = False
                
        if self.doingSoulGain:
            self.doingSoulGain = time.time() + config.soulGain
        else:
            self.doingSoulGain = time.time() + config.soulGain
            gainTime = self.getVocation().soulticks
            game.engine.safeCallLater(gainTime, doSoulGain, gainTime)
    # Spells
    def cooldownSpell(self, icon, group, cooldown):
        stream = self.packet()
        stream.cooldownIcon(icon, cooldown)
        
        stream.cooldownGroup(group, cooldown)
        
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
        self.modes[0] = attack
        
        if self.target and self.targetMode == 1 and self.modes[1] != 1 and chase == 1:
            game.engine.autoWalkCreatureTo(self, self.target.position, -1, True)
            self.target.scripts["onNextStep"].append(self.followCallback)
            
        self.modes[1] = chase
        self.modes[2] = secure
        
        
            
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
        
    def message(self, message, msgType='MSG_STATUS_DEFAULT', color=0, value=0, pos=None):
        stream = self.packet()
        stream.message(message, msgType, color, value, pos)
        stream.send(self.client)
        
        

    def outfitWindow(self):
        stream = self.packet(0xC8)
        
        # First the current outfit
        stream.outfit(self.outfit, self.addon, self.mount)
        looks = []
        for outfit in game.resource.outfits:
            # TODO, can wear
            looks.append(outfit)
                
        stream.uint8(len(looks))
        for outfit in looks:
            look = outfit.getLook(self.gender)
            stream.uint16(look[0])
            stream.string(outfit.name)
            stream.uint8(3) # TODO addons
        
        if config.allowMounts:
            mounts = []
            for mount in game.resource.mounts:
                # TODO, can use
                mounts.append(mount)
                
            stream.uint8(len(mounts))
            for mount in mounts:
                stream.uint16(mount.cid)
                stream.string(mount.name)
        else:
            stream.uint8(0)
            
        stream.send(self.client)
    
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
        
    def stopAutoWalk(self):
        ret = self.stopAction()

        self.cancelWalk(self.direction)
    
    def windowMessage(self, text):
        stream = self.packet(0x15)
        stream.string(text)
        stream.send(self.client)
    
    def notPossible(self):
        self.message("Sorry, not possible.", 'MSG_STATUS_SMALL')

    def outOfRange(self):
        self.message("Destination is out of range.", 'MSG_STATUS_SMALL')

    def notEnoughRoom(self):
        self.message("There is not enough room.", 'MSG_STATUS_SMALL')
        
    def exhausted(self):
        self.message("You are exhausted.", 'MSG_STATUS_SMALL')

    def needMagicItem(self):
        self.message("You need a magic item to cast this spell.", 'MSG_STATUS_SMALL')
    
    def notEnough(self, word):
        self.message("You do not have enough %s." % word, 'MSG_STATUS_SMALL')

    def onlyOnCreatures(self):
        self.message("You can only use it on creatures.", 'MSG_STATUS_SMALL')
        
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
            
    def openContainer(self, container, parent=False, update=False):
        if update or not container in self.openContainers:
            stream = self.packet(0x6E)
            
            if not update:
                container.opened = True
                self.openContainers.append(container)
            
            stream.uint8(self.openContainers.index(container))
            
            stream.uint16(container.cid)
            stream.string(container.name())
            
            stream.uint8(container.containerSize)
            stream.uint8(parent)
            stream.uint8(len(container.container.items))
            
            for item in container.container.items:
                stream.item(item)
                
            stream.send(self.client)
            
    def closeContainer(self, container):
        index = self.openContainers.index(container)
        def end():
            stream = self.packet(0x6F)
            stream.uint8(index)
            self.openContainers.remove(container)
            container.opened = False
            stream.send(self.client)
        
        def callOpen(): game.scriptsystem.get('use').run(container, self, end, position=[0xFFFF, 0, 0], stackpos=0, index=index)
        
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
    def itemToContainer(self, container, item, count=None, recursive=True, stack=True, streamX=None):
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
                        itemX.count = min(itemX.count + count, 100)
                        count = total - itemX.count
                        
                        # Is it a open container, if so, send item update
                        if bag in self.openContainers:
                            stream.updateContainerItem(self.openContainers.index(bag), slot, itemX)
                        
                        if update:
                            self.replaceCache(itemX)
                            
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
            if recursive:
                info = container.container.placeItemRecursive(item)
            else:
                info = container.container.placeItem(item)
                
            if info == None:
                return # Not possible
                
            if recursive and info and info.opened:
                stream.addContainerItem(self.openContainers.index(info), item)
                    
            elif container.opened:
                stream.addContainerItem(self.openContainers.index(container), item)
            
            if update:
                self.addCache(item)
                
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
        stream.uint8(len(channels))
        for channel in channels:
            stream.uint16(channel.id)
            stream.string(channel.name)
            
        stream.send(self.client)
    
    def openChannel(self, id):
        stream = self.packet(0xAC)
        channel = game.chat.getChannel(id)
        stream.uint16(id)
        stream.string(channel.name)
        
        # TODO: Send members for certain channels
        stream.uint32(0)
        
        stream.send(self.client)
        channel.addMember(self)

    def openPrivateChannel(self, between):
        id = 0xFFFF
        self._openChannels[between.name()] = [id, between]
        stream = self.packet(0xB2)
        stream.uint16(id)
        stream.string(between.name())
        stream.send(self.client)
        return id
        
    def closePrivateChannel(self, between):
        if between.name() in self._openChannels:
            betweenObj = self._openChannels[between.name()]
            stream = self.packet(0xB3)
            stream.uint16(betweenObj[0])
            stream.send(self.client)
        
    def closeChannel(self, id):
        channel = game.chat.getChannel(id)
        channel.removeMember(self)

    def isChannelOpen(self, between):
        try:
            return self._openChannels[between.name()]
        except:
            return False
            
    def sendChannelMessage(self, by, text, type=game.enum.MSG_SPEAK_SAY, channelId=0):
        stream = self.packet(0xAA)
        stream.uint32(1)
        print by.data["name"]
        stream.string(by.data["name"])
        if by.isPlayer():
            stream.uint16(by.data["level"])
        else:
            stream.uint16(0)
        stream.uint8(type)
        if type in (enum.MSG_CHANNEL_MANAGEMENT, enum.MSG_CHANNEL, enum.MSG_CHANNEL_HIGHLIGHT):
            stream.uint16(channelId)
        
        print text
        stream.string(text)
        stream.send(self.client)
    def getPrivate(self, name):
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
        tile = game.map.getTile(self.position)

        corpse = game.item.Item(3058)
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
        game.engine.updateTile(self.position, tile)
        self.sendReloginWindow()
        
    def onSpawn(self):
        if not self.data["health"]:
            self.data["health"] = self.data["healthmax"]
            self.data["mana"] = self.data["manamax"]
            
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
        for item in container.items:
            weight = item.weight
            item.container = container # Funny call to simplefy lookups
            if weight:
                self.inventoryWeight += weight * (item.count or 1)
            try:
                self.inventoryCache[item.itemId].append(item)
                self.inventoryCache[item.itemId][0] += item.count or 1
            except:
                self.inventoryCache[item.itemId] = [item.count or 1, item]
                
    def unpickleInventory(self, inventoryData):
        self.inventory = pickle.loads(inventoryData)
        print self.inventory
        # Generate the inventory cache
        for item in self.inventory:
            if isinstance(item, game.item.Item):
                weight = item.weight
                if weight:
                    self.inventoryWeight += weight * (item.count or 1)
                try:
                    self.inventoryCache[item.itemId].append(item)
                    self.inventoryCache[item.itemId][0] += item.count or 1
                except:
                    self.inventoryCache[item.itemId] = [item.count or 1, item]
                
                if item.containerSize:
                    self.__buildInventoryCache(item.container)
        
    # Saving
    def pickleInventory(self):
        t = time.time()
        d = pickle.dumps(self.inventory, pickle.HIGHEST_PROTOCOL)
        print "pickle inventory took %f. Length is %d" % (time.time() - t, len(d))
        return d

    def pickleDepot(self):
        t = time.time()
        d = pickle.dumps(self.depot, pickle.HIGHEST_PROTOCOL)
        print "pickle player depot took %f. Length is %d" % (time.time() - t, len(d))
        return d
        
    def _saveQuery(self):
        return "UPDATE `players` SET `skills`= %s, `storage` = %s, `experience` = %s, `manaspent` = %s, `mana`= %s, `health` = %s, `soul` = %s, `stamina` = %s, `direction` = %s, `posx` = %s, `posy` = %s, `posz` = %s, `inventory` = %s, `depot` = %s WHERE `id` = %s", (otjson.dumps(self.skills), otjson.dumps(self.storage), self.data["experience"], self.data["manaspent"], self.data["mana"], self.data["health"], self.data["soul"], self.data["stamina"] * 1000, self.direction, self.position[0], self.position[1], self.position[2], self.pickleInventory(), self.pickleDepot(), self.data["id"])

    def save(self):
        sql.conn.runOperation(*self._saveQuery())

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
        
    def getStorage(self, field, default=None):
        try:
            return self.storage[field]
        except:
            return default

    def modifyStorage(self, field, change):
        self.storage[field] += change

    def removeStorage(self, field):
        try:
            del self.storage[field]
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
        
    # Stuff from protocol:
    def handleSay(self, channelType, channelId, reciever, text):
        if len(text) > config.maxLengthOfSay:
            self.message("Message too long")
            return
            
        splits = text.split(" ")
        if splits[0] == "#y":
            mode = game.enum.MSG_SPEAK_YELL
            del splits[0]
        elif splits[0] == "#w":
            mode = game.enum.MSG_SPEAK_WHISPER
            del splits[0]
        else:
            mode = channelType
        def endCallback():
            print channelType
            if channelType in (game.enum.MSG_SPEAK_SAY, game.enum.MSG_SPEAK_YELL, game.enum.MSG_SPEAK_WHISPER):
                if mode == game.enum.MSG_SPEAK_SAY:
                    self.say(' '.join(splits[0:]))
                    
                elif mode == game.enum.MSG_SPEAK_YELL:
                    self.yell(' '.join(splits[0:]))
                
                elif mode == game.enum.MSG_SPEAK_WHISPER:
                    self.whisper(' '.join(splits[0:]))
                    
            for creature in game.engine.getCreatures(self.position):
                creature.playerSay(self, text, channelType, channelId or reciever)

        def part1():
            game.scriptsystem.get("talkaction").run(text, self, endCallback, text=' '.join(splits[0:]))
            
        if len(splits) > 1:
            game.scriptsystem.get("talkactionFirstWord").run(splits[0], self, part1, text=' '.join(splits[1:]))
        else:
            part1()

    def attackTarget(self):
        if self.target and self.inRange(self.target.position, 1, 1):
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
                    dmg = -1 * random.randint(0, round(config.meleeDamage(1, self.getActiveSkill(skillType), self.data["level"], factor)))
                    
                else:
                    skillType = self.inventory[5].weaponType
                    dmg = -1 * random.randint(0, round(config.meleeDamage(self.inventory[5].attack, self.getActiveSkill(skillType), self.data["level"], factor)))
                    
                if dmg != 0:
                    self.target.onHit(self, dmg, game.enum.MELEE)
                    key = '__skill%d' % skillType
                    try:
                        self.modifyStorage(key, -1)
                        self.refreshSkills()
                    except:
                        # Happends on new members using new weapons
                        self.setStorage(key, 1)
                        self.refreshSkills()
                        
        if self.target:        
            self.targetChecker = reactor.callLater(config.meleeAttackSpeed, self.attackTarget)
            
    def setAttackTarget(self, cid):
        if self.targetMode == 1:
            self.targetMode = 0
            self.target = None
            try:
                self.targetChecker.cancel()
            except:
                pass
            return
            
        if cid in allCreatures:
            self.target = allCreatures[cid]
            self.targetMode = 1
        else:
            self.notPossible()
            
        if self.modes[1] == game.enum.CHASE:
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
            self.target = allCreatures[cid]
            self.targetMode = 2
            game.engine.autoWalkCreatureTo(player, self.target.position, -1, True)
            self.target.scripts["onNextStep"].append(self.followCallback)
        else:
            self.notPossible()
            
    # Skull and emblems and such
    def square(self, creature, color=27):
        stream = self.packet(0x86)
        stream.uint32(creature.cid)
        stream.uint8(color)
        stream.send(self.client)
        
    