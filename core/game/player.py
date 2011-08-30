from packet import TibiaPacket
from game import enum, engine
from game.map import placeCreature, removeCreature, getTile
from twisted.python import log
import config
from collections import deque
import game.scriptsystem
from game.item import Item
from twisted.internet.defer import deferredGenerator, waitForDeferred, Deferred
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
        
        # Direction
        self.direction = self.data["direction"]
        del self.data["direction"]

        # Inventory
        if self.data['inventory']:
            self.inventory = self.unpickleInventory(self.data['inventory'])
        else:
            self.inventory = [Item(8820), Item(2125), Item(1987), Item(2463), None, Item(7449), None, None, None, Item(2546, 20), None]
        del self.data['inventory']
        
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
        if self.data["skills"]:
            self.skills = otjson.loads(self.data["skills"])
        else:
            self.skills = []
            for i in xrange(game.enum.SKILL_FIRST, game.enum.SKILL_LAST+1):
                self.skills.append(1)
            
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
    def sendFirstPacket(self):
        
        stream = TibiaPacket(0x0A)

        stream.uint32(self.clientId()) # Cid
        stream.uint16(config.drawingSpeed) # Drawing speed
        stream.uint8(1) # Rule violations?

        stream.uint8(0x64) # Map description
        stream.position(self.position)
        stream.mapDescription((self.position[0] - 8, self.position[1] - 6, self.position[2]), 18, 14, self)

        for slot in xrange(enum.SLOT_FIRST,enum.SLOT_LAST):
            if self.inventory[slot-1]:
                stream.uint8(0x78)
                stream.uint8(slot)
            
                stream.item(self.inventory[slot-1])
                
        self.refreshStatus(stream)
        self.refreshSkills(stream)
        
        stream.worldlight(game.engine.getLightLevel(), enum.LIGHTCOLOR_WHITE)
        stream.creaturelight(self.cid, 0,0)
        stream.uint8(0xA2) # Icons
        stream.uint16(0) # TODO: Icons

        stream.magicEffect(self.position, 0x03)
        stream.send(self.client)
        
    def refreshStatus(self, streamX=None):
        if not streamX:
            stream = TibiaPacket()
        else:
            stream = streamX
        stream.uint8(0xA0)
        stream.uint16(self.data["health"])
        stream.uint16(self.data["healthmax"])
        stream.uint32(self.data["capasity"] * 100) # TODO: Free Capasity
        stream.uint32(self.data["capasity"] * 100) # TODO: Cap
        stream.uint64(self.data["experience"]) # TODO: Virtual cap? Experience
        if self.data["level"] > 0xFFFF:
            stream.uint16(0xFFFF)
        else:
            stream.uint16(self.data["level"]) # TODO: Virtual cap? Level
        stream.uint8(math.ceil(float(config.levelFormula(self.data["level"]+1)) / self.data["experience"])) # % to next level, TODO
        stream.uint16(self.data["mana"]) # mana
        stream.uint16(self.data["manamax"]) # mana max
        stream.uint8(self.data["maglevel"]) # TODO: Virtual cap? Manalevel
        stream.uint8(1) # TODO: Virtual cap? ManaBase
        stream.uint8(0) # % to next level, TODO
        stream.uint8(self.data["soul"]) # TODO: Virtual cap? Soul
        stream.uint16(min(42 * 60, self.data["stamina"] / 60)) # Stamina minutes
        stream.uint16(self.speed) # Speed
        
        stream.uint16(0x00) # Condition

        if not streamX:
            stream.send(self.client)
            
    def refreshSkills(self, streamX=None):
        if not streamX:
            stream = TibiaPacket()
        else:
            stream = streamX        
        stream.uint8(0xA1) # Skill type

        for x in xrange(game.enum.SKILL_FIRST, game.enum.SKILL_LAST+1):
            stream.uint8(self.skills[x]) # Value / Level
            stream.uint8(1) # Base
            stream.uint8(0) # %
        if not streamX:
            stream.send(self.client)            
            

    def pong(self):
        TibiaPacket(0x1E).send(self.client)

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
            bags = []
            itemFound = None
            for item in self.inventory:
                if item.itemId == sid:
                    itemFound = item
                    break
                elif item.containerSize:
                    bags.append(item)
                    
            # Bags
            for bag in bags.pop(0):
                for item in bag.items:
                    if item.itemId == sid:
                        itemFound = item
                        break
                    elif item.containerSize:
                        bags.append(item)
                        
            return itemFound
            
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
            return None # TODO

    def findItemById(self, itemId, count=0):
        items = []
        foundCount = 0
        stream = TibiaPacket()
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
            stream.send(self.client)
            return items[0][1]
        else:
            newItem = game.item.Item(itemId, count)
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
                else:
                    if item[0] == 1:
                        self.inventory[item[2]+1-1] = None
                        stream.removeInventoryItem(item[2]+1)
                    elif item[0] == 2:
                        item[2].container.removeItem(item[1])
                        stream.removeContainerItem(self.openContainers.index(item[2]), item[3])
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
                self.inventory[position[1]-1] = item
                self.updateInventory(position[1])
            
            # Option 3, the bags, if there is one ofcource
            elif self.inventory[2]:
                try:
                    bag = self.openContainers[position[1] - 64]
                except:
                    return
                    
                bag.container.items[position[2]] = item
                stream = TibiaPacket()
                stream.updateContainerItem(position[1] - 64, position[2], item)
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
                self.inventory[position[1]-1] = None
                self.updateInventory(position[1])
            
            # Option 3, the bags, if there is one ofcource
            elif self.inventory[2]:
                try:
                    bag = self.openContainers[position[1] - 64]
                except:
                    return
                    
                del bag.container.items[position[2]]
                stream = TibiaPacket()
                stream.removeContainerItem(position[1] - 64, position[2])
                stream.send(self.client)
                
    def getContainer(self, openId):
        try:
            return self.openContainers[openId]
        except:
            return

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
            self.data["capasity"] = vocation.maxCapasity(self.data["level"])
            
            if self.data["health"] > self.data["healthmax"]:
                self.data["health"] = self.data["healthmax"]
                
            if self.data["mana"] > self.data["manamax"]:
                self.data["mana"] = self.data["manamax"]
            
            if send:
                if level > oldLevel:
                    self.message("You advanced from level %d to Level %d." % (oldLevel, level), game.enum.MSG_EVENT_ADVANCE)
                elif level < oldLevel:
                    self.message("You were downgraded from level %d to Level %d." % (oldLevel, level), game.enum.MSG_EVENT_ADVANCE)
                self.refreshStatus()
        
    def modifyExperience(self, exp):
        up = True
        if exp < 0:
            up = False
        
        self.data["experience"] += exp
        
        if up:
            level = 0
            self.message("You gained %d experience points." % exp, game.enum.MSG_EXPERIENCE, color=config.experienceMessageColor, value=exp)
            while True:
                if config.totalExpFormula(self.data["level"]+level) > self.data["experience"]:
                    break
                level += 1
            if level:
                self.setLevel(self.data["level"]+level)
        else:
            level = 0
            self.message("You lost %d experience points." % exp, game.enum.MSG_EXPERIENCE, color=config.experienceMessageColor, value=exp)
            while True:
                if config.totalExpFormula(self.data["level"]-level) > self.data["experience"]:
                    break
                level += 1
            if level:
                self.setLevel(self.data["level"]-level)            
        self.refreshStatus()
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
        stream = TibiaPacket(0xA4)
        stream.uint8(icon)
        stream.uint32(cooldown * 1000)
        stream.uint8(0xA5)
        stream.uint8(group)
        stream.uint32(cooldown * 1000)
        
        stream.send(self.client)        
        t = time.time()  + cooldown
        self.cooldowns[icon] = t
        self.cooldowns[group << 8] = t
    def cooldownIcon(self, icon, cooldown):
        self.cooldowns[icon] = time.time() + cooldown
        stream = TibiaPacket(0xA4)
        stream.uint8(icon)
        stream.uint32(cooldown * 1000)
        stream.send(self.client)
        
    def cooldownGroup(self, group, cooldown):
        self.cooldowns[group << 8] = time.time() + cooldown
        stream = TibiaPacket(0xA5)
        stream.uint8(group)
        stream.uint32(cooldown * 1000)
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
            self.target.scripts["onNextStep"].append(self.__followCallback)
            
        self.modes[1] = chase
        self.modes[2] = secure
        
        
            
    def setTarget(self, targetId=0):
        stream = TibiaPacket(0xA3)
        stream.uint32(targetId)
        stream.send(self.client)
        
    def cancelWalk(self, direction=None):
        stream = TibiaPacket(0xB5)
        stream.uint8(direction if direction is not None else self.direction)
        stream.send(self.client)
        
    def tutorial(self, tutorialId):
        stream = TibiaPacket(0xDC)
        stream.uint8(tutorialId)
        stream.send(self.client)
        
    def mapMarker(self, position, typeId, desc=""):
        stream = TibiaPacket(0xDD)
        stream.position(position)
        stream.uint8(typeId)
        stream.string(desc)
        stream.send(self.client)
        
    def message(self, message, msgType=enum.MSG_STATUS_DEFAULT, color=0, value=0, pos=None):
        stream = TibiaPacket(0xB4)
        stream.uint8(msgType)
        if msgType in (enum.MSG_DAMAGE_DEALT, enum.MSG_DAMAGE_RECEIVED, enum.MSG_DAMAGE_OTHERS):
            if pos:
                stream.position(pos)
            else:
                stream.position(self.position)
            stream.uint32(value)
            stream.uint8(color)
            stream.uint32(0)
            stream.uint8(0)
        elif msgType in (enum.MSG_EXPERIENCE, enum.MSG_EXPERIENCE_OTHERS, enum.MSG_HEALED, enum.MSG_HEALED_OTHERS):
            if pos:
                stream.position(pos)
            else:
                stream.position(self.position)
            stream.uint32(value)
            stream.uint8(color)
            
        stream.string(message)
        stream.send(self.client)
        
        

    def outfitWindow(self):
        stream = TibiaPacket(0xC8)
        
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
        
        mounts = []
        for mount in game.resource.mounts:
            # TODO, can use
            mounts.append(mount)
            
        stream.uint8(len(mounts))
        for mount in mounts:
            stream.uint16(mount.cid)
            stream.string(mount.name)

        stream.send(self.client)
    
    def textWindow(self, item, canWrite=False, maxLen=0xFF, text="", writtenBy="", timestamp=0):
        stream = TibiaPacket(0x96)
        
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
        stream = TibiaPacket(0x15)
        stream.string(text)
        stream.send(self.client)
    
    def notPossible(self):
        self.message("Sorry, not possible.", enum.MSG_STATUS_SMALL)

    def outOfRange(self):
        self.message("Destination is out of range.", enum.MSG_STATUS_SMALL)

    def notEnoughRoom(self):
        self.message("There is not enough room.", enum.MSG_STATUS_SMALL)
        
    def exhausted(self):
        self.message("You are exhausted.", enum.MSG_STATUS_SMALL)

    def needMagicItem(self):
        self.message("You need a magic item to cast this spell.", enum.MSG_STATUS_SMALL)
    
    def notEnough(self, word):
        self.message("You do not have enough %s." % word, enum.MSG_STATUS_SMALL)

    def onlyOnCreatures(self):
        self.message("You can only use it on creatures.", enum.MSG_STATUS_SMALL)
        
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
            stream = TibiaPacket(0x6E)
            
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
        stream = TibiaPacket(0x6F)
        stream.uint8(index)
        del self.openContainers[index]
        container.opened = False
        stream.send(self.client)


    def closeContainerId(self, openId):
        try:
            container = self.openContainers[openId]
            stream = TibiaPacket(0x6F)
            stream.uint8(openId)
            del self.openContainers[openId]
            container.opened = False
            stream.send(self.client)
            return True
            
        except:
            return False

    def arrowUpContainer(self, openId):
        bagFound = self.openContainers[openId]
                
        if bagFound.parent:
            bagFound.parent.opened = True
            bagFound.opened = False
            self.openContainers[openId] = bagFound.parent
            self.updateContainer(self.openContainers[openId], True if self.openContainers[openId].parent else False)

    # Item to container
    def itemToContainer(self, container, item, count=None, recursive=True, stack=True, streamX=None):
        stream = streamX
        if not streamX:
            stream = TibiaPacket()
        
        if not count:
            count = 1 if item.count == None else item.count
        
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
        
        if not streamX:
            stream.send(self.client)
            
        return True

    def itemToUse(self, item):
        # Means, right hand, left hand, ammo or bag. Stackable only
        if not self.inventory[4]:
            self.inventory[4] = item
            stream = TibiaPacket()
            stream.addInventoryItem(5, self.inventory[4])
            stream.send(self.client)
            return True
        elif self.inventory[4].itemId == item.itemId and self.inventory[4].count < 100:
            prevCount = self.inventory[4].count
            self.inventory[4].count = min(100, prevCount + item.count)
            item.count = (prevCount + item.count) - self.inventory[4].count
            stream = TibiaPacket()
            stream.addInventoryItem(5, self.inventory[4])
            stream.send(self.client)            
        if item.count:
            if not self.inventory[5]:
                self.inventory[5] = item
                stream = TibiaPacket()
                stream.addInventoryItem(6, self.inventory[5])
                stream.send(self.client)
                return True
            elif self.inventory[5].itemId == item.itemId and self.inventory[5].count < 100:
                prevCount = self.inventory[5].count
                self.inventory[5].count = min(100, prevCount + item.count)
                item.count = (prevCount + item.count) - self.inventory[5].count  
                stream = TibiaPacket()
                stream.addInventoryItem(6, self.inventory[5])
                stream.send(self.client)
                
        if item.count:
            if not self.inventory[9]:
                self.inventory[9] = item
                stream = TibiaPacket()
                stream.addInventoryItem(10, self.inventory[0])
                stream.send(self.client)
                return True
            elif self.inventory[9].itemId == item.itemId and self.inventory[9].count < 100:
                prevCount = self.inventory[5].count
                self.inventory[9].count = min(100, prevCount + item.count)
                item.count = (prevCount + item.count) - self.inventory[9].count  
                stream = TibiaPacket()
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
            
        stream = TibiaPacket()
        stream.addInventoryItem(slot, self.inventory[slot-1])
        stream.send(self.client)
        
        return True

    def updateInventory(self, slot):
        stream = TibiaPacket()
        if self.inventory[slot-1].stackable and not self.inventory[slot-1].count:
            stream.removeInventoryItem(slot)
        else:
            stream.addInventoryItem(slot, self.inventory[slot-1])
        stream.send(self.client)        
    # Channel system
    def openChannels(self):
        stream = TibiaPacket(0xAB)
        channels = game.chat.getChannels(self)
        stream.uint8(len(channels))
        for channel in channels:
            stream.uint16(channel.id)
            stream.string(channel.name)
            
        stream.send(self.client)
    
    def openChannel(self, id):
        stream = TibiaPacket(0xAC)
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
        stream = TibiaPacket(0xB2)
        stream.uint16(id)
        stream.string(between.name())
        stream.send(self.client)
        return id
        
    def closePrivateChannel(self, between):
        if between.name() in self._openChannels:
            betweenObj = self._openChannels[between.name()]
            stream = TibiaPacket(0xB3)
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
        stream = TibiaPacket(0xAA)
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
        stream = TibiaPacket(0x28)
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
    def unpickleInventory(self, inventoryData):
        return pickle.loads(inventoryData)
        
    # Saving
    def pickleInventory(self):
        t = time.time()
        d = pickle.dumps(self.inventory, pickle.HIGHEST_PROTOCOL)
        print "pickle inventory took %f. Length is %d" % (time.time() - t, len(d))
        return d
        
    def _saveQuery(self):
        return "UPDATE `players` SET `skills`= %s, `storage` = %s, `experience` = %s, `manaspent` = %s, `mana`= %s, `health` = %s, `soul` = %s, `stamina` = %s, `direction` = %s, `posx` = %s, `posy` = %s, `posz` = %s, `inventory` = %s WHERE `id` = %s", (otjson.dumps(self.skills), otjson.dumps(self.storage), self.data["experience"], self.data["manaspent"], self.data["mana"], self.data["health"], self.data["soul"], self.data["stamina"] * 1000, self.direction, self.position[0], self.position[1], self.position[2], self.pickleInventory(), self.data["id"])

    @deferredGenerator
    def save(self):
        r = waitForDeferred(sql.conn.runOperation(*self._saveQuery()))
        yield r
        r = r.getResult()

    @deferredGenerator
    def saveSkills(self):
        yield waitForDeferred(sql.conn.runOperation("UPDATE `players` SET `skills`= %s WHERE `id` = %d", (otjson.dumps(self.skills), self.data["id"])))
    
    @deferredGenerator
    def saveExperience(self):
        yield waitForDeferred(sql.conn.runOperation("UPDATE `players` SET `experience`= %d, `manaspent` = %d WHERE `id` = %d", (self.data["experience"], self.data["manaspent"], self.data["id"])))
    
    @deferredGenerator
    def saveStorage(self):
        yield waitForDeferred(sql.conn.runOperation("UPDATE `players` SET `storage`= %s WHERE `id` = %d", (otjson.dumps(self.storage), self.data["id"])))

    # Shopping
    def setTrade(self, npc):
        if not self.openTrade:
            self.openTrade = npc

            
    def closeTrade(self):
        if self.openTrade:
            stream = TibiaPacket(0x7C)
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
        
    # Compelx packets
    def handleSay(self, packet):
        channelType = packet.uint8()
        channelId = 0
        reciever = ""
        if channelType in (enum.MSG_CHANNEL_MANAGEMENT, enum.MSG_CHANNEL, enum.MSG_CHANNEL_HIGHLIGHT):
            channelId = packet.uint16()
        elif channelType in (enum.MSG_PRIVATE_TO, enum.MSG_GAMEMASTER_PRIVATE_TO):
            reciever = packet.string()
            print "..."+reciever+"..."

        text = packet.string()
        
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

    def handleAutoWalk(self, packet):
        game.engine.explainPacket(packet)
        if self.target:
            self.target = None
        self.stopAction()    
        steps = packet.uint8()

        walkPattern = deque()
        for x in xrange(0, steps):
            direction = packet.uint8()
            if direction == 1:
                walkPattern.append(1) # East
            elif direction == 2:
                walkPattern.append(7) # Northeast
            elif direction == 3:
                walkPattern.append(0) # North
            elif direction == 4:
                walkPattern.append(6) # Northwest          
            elif direction == 5:
                walkPattern.append(3) # West
            elif direction == 6:
                walkPattern.append(4) # Southwest
            elif direction == 7:
                walkPattern.append(2) # South
            elif direction == 8:
                walkPattern.append(5) # Southeast           
            else:
                continue # We don't support them
                
        game.engine.autoWalkCreature(self, walkPattern)

    def handleWalk(self, direction):
        if self.target:
            self.target = None

        try:
            game.engine.autoWalkCreature(self, deque([direction]))
        except game.errors.ImpossibleMove:
            print "Player got a impossible move, ignoring"
            # This is a impossible move
            
    @deferredGenerator
    def handleMoveItem(self, packet):
        from game.item import Item, sid, items
        fromPosition = packet.position()
        fromMap = False
        toMap = False
        if fromPosition[0] != 0xFFFF:
            # From map
            fromMap = True
        
        clientId = packet.uint16()
        fromStackPos = packet.uint8()
        toPosition = packet.position()
        if toPosition[0] != 0xFFFF:
            toMap = True
           
        count = packet.uint8()
        oldItem = None
        renew = False
        stack = True
        
        isCreature = False
        if clientId < 100:
            isCreature = True
        if not isCreature:
            # Remove item:
            currItem = self.findItemWithPlacement(toPosition)

            """if currItem and currItem[1] and not ((currItem[1].stackable and currItem[1].itemId == sid(clientId)) or currItem[1].containerSize):
                currItem[1] = None
            """
            if fromMap:
                
                walkPattern = game.engine.calculateWalkPattern(self.position, fromPosition, -1)
                if len(walkPattern):
                    def sleep(seconds):
                        d = Deferred()
                        reactor.callLater(seconds, d.callback, seconds)
                        return d
                    
                    walking = [True]
                    game.engine.autoWalkCreature(self, deque(walkPattern), lambda: walking.pop())
                    while walking:
                        yield waitForDeferred(sleep(0.05))
                            
                    
                stream = TibiaPacket()
                oldItem = self.findItemWithPlacement(fromPosition, fromStackPos)

                # Before we remove it, can it be placed there?
                if toPosition[0] == 0xFFFF and toPosition[1] < 64 and toPosition[1] not in (game.enum.SLOT_DEPOT, game.enum.SLOT_AMMO) and toPosition[1] != game.enum.SLOT_BACKPACK and toPosition[1] != oldItem[1].slotId():
                    self.notPossible()
                    return
                    
                if oldItem[1].stackable and count < 100:
                    renew = True
                    oldItem[1].reduceCount(count)
                    if oldItem[1].count:
                        stream.updateTileItem(fromPosition, fromStackPos, oldItem[1])
                    else:
                        stream.removeTileItem(fromPosition, fromStackPos)
                        game.map.getTile(fromPosition).removeItem(oldItem[1])
                else:
                    stream.removeTileItem(fromPosition, fromStackPos)
                    game.map.getTile(fromPosition).removeClientItem(clientId, fromStackPos)
                stream.sendto(game.engine.getSpectators(fromPosition))
                
            else:
                stream = TibiaPacket()
                        
                oldItem = self.findItemWithPlacement(fromPosition)
                
                # Before we remove it, can it be placed there?
                if toPosition[0] == 0xFFFF and toPosition[1] < 64 and toPosition[1] not in (game.enum.SLOT_DEPOT, game.enum.SLOT_AMMO) and toPosition[1] != game.enum.SLOT_BACKPACK and toPosition[1] != oldItem[1].slotId():
                    self.notPossible()
                    return
                    
                if oldItem[1].stackable and count < 100:
                    renew = True
                    oldItem[1].count -= count
                    if oldItem[1].count > 0:
                        if oldItem[0] == 1:
                            stream.addInventoryItem(fromPosition[1], oldItem[1])
                        elif oldItem[0] == 2:
                            stream.updateContainerItem(self.openContainers.index(oldItem[2]), fromPosition[2], oldItem[1])
                    else:
                        if oldItem[0] == 1:
                            self.inventory[fromPosition[1]-1] = None
                            stream.removeInventoryItem(fromPosition[1])
                        elif oldItem[0] == 2:
                            oldItem[2].container.removeItem(oldItem[1])
                            stream.removeContainerItem(self.openContainers.index(oldItem[2]), fromPosition[2])
                else:
                    if oldItem[0] == 1:
                        self.inventory[fromPosition[1]-1] = None
                        stream.removeInventoryItem(fromPosition[1])
                    elif oldItem[0] == 2:
                        oldItem[2].container.removeItem(oldItem[1])
                        stream.removeContainerItem(self.openContainers.index(oldItem[2]), fromPosition[2])
                
                if toPosition[1] == fromPosition[1]:
                    stack = False
                    
                stream.send(self.client)
            if toMap:
                stream = TibiaPacket()
                if renew:
                    newItem = Item(sid(clientId), count)
                else:
                    newItem = oldItem[1]
                findItem = game.map.getTile(toPosition).findClientItem(clientId, True) # Find item for stacking
                if findItem and newItem.stackable and count < 100 and findItem[1].count + count <= 100:
                    newItem.count += findItem[1].count
                    stream.removeTileItem(toPosition, findItem[0])
                    game.map.getTile(toPosition).removeItem(findItem[1])
                    
                toStackPos = game.map.getTile(toPosition).placeItem(newItem)
                stream.addTileItem(toPosition, toStackPos, newItem )
                
                if not renew and newItem.containerSize and newItem.opened:
                    self.closeContainer(newItem)
                stream.sendto(game.engine.getSpectators(toPosition))

            else:
                
                if currItem and currItem[1] and currItem[1].containerSize:
                    ret = self.itemToContainer(currItem[1], Item(sid(clientId), count) if renew else oldItem[1], count=count, stack=stack)

                elif currItem and (currItem[0] == 2) and not currItem[1] and currItem[2]:
                    ret = self.itemToContainer(currItem[2], Item(sid(clientId), count) if renew else oldItem[1], count=count, stack=stack)
                else:
                    stream = TibiaPacket()
                    if toPosition[1] < 64:
                        if oldItem[1].stackable and self.inventory[toPosition[1]-1] and self.inventory[toPosition[1]-1].itemId == sid(clientId) and (self.inventory[toPosition[1]-1].count + count <= 100):
                            self.inventory[toPosition[1]-1].count += count
                        else:       
                            self.inventory[toPosition[1]-1] = Item(sid(clientId), count) if renew else oldItem[1]
                        stream.addInventoryItem(toPosition[1], self.inventory[toPosition[1]-1])
                    else:
                        container = self.getContainer(toPosition[1]-64)
                        try:
                            container.container.items[toPosition[2]] = Item(sid(clientId), count) if renew else oldItem[1]
                            stream.updateContainerItem(toPosition[1]-64, toPosition[2], container.container.items[toPosition[2]])
                        except:
                            self.itemToContainer(container, Item(sid(clientId), count) if renew else oldItem[1], count=count, stack=stack, streamX=stream)                  
                    if renew and currItem and currItem[1]:
                        if fromPosition[1] < 64:
                            self.inventory[fromPosition[1]-1] = currItem[1]
                            stream.addInventoryItem(fromPosition[1], self.inventory[fromPosition[1]-1])
                        else:
                            self.itemToContainer(self.inventory[2], currItem[1])

                    stream.send(self.client)
        else:
            if game.map.getTile(toPosition).creatures():
                self.notEnoughRoom()
                return
                
            creature = game.map.getTile(fromPosition).getThing(fromStackPos) 
            toTile = game.map.getTile(toPosition)
            for i in toTile.getItems():
                if i.solid:
                    self.notPossible()
                    return
            if abs(creature.position[0]-self.position[0]) > 1 or abs(creature.position[1]-self.position[1]) > 1:
                walkPattern = game.engine.calculateWalkPattern(creature.position, toPosition)
                if len(walkPattern) > 1:
                    self.outOfRange()
                else:
                    game.engine.autoWalkCreatureTo(self, creature.position, -1, True, lambda: game.engine.autoWalkCreature(creature, deque(walkPattern)))
            else:
                game.engine.autoWalkCreatureTo(creature, toPosition)
            
    def handleLookAt(self, packet):
        from game.item import sid, cid, items
        position = packet.position()
        print "Look at"
        print position
            
        clientId = packet.uint16()
        stackpos = packet.uint8()

        thing = self.findItem(position, stackpos)     
        
        if thing:
            if isinstance(thing, game.item.Item):
                def afterScript():
                    extra = ""
                    # TODO propper description handling
                    if config.debugItems:
                        extra = "(ItemId: %d, Cid: %d)" % (thing.itemId, clientId)
                    self.message(thing.description() + extra, game.enum.MSG_INFO_DESCR)
            elif isinstance(thing, Creature):
                def afterScript():
                    if self == thing:
                        self.message(thing.description(True), game.enum.MSG_INFO_DESCR)
                    else:
                        self.message(thing.description(), game.enum.MSG_INFO_DESCR)
            game.scriptsystem.get('lookAt').run(thing, self, afterScript, position=position, stackpos=stackpos)
        else:
            self.notPossible()

    def handleLookAtTrade(self, packet):
        from game.item import sid
        clientId = packet.uint16()
        count = packet.uint8()
        
        item = game.item.Item(sid(clientId), count)
        self.message(item.description(), game.enum.MSG_INFO_DESCR)
        del item
        
    def handleRotateItem(self, packet):
        position = packet.position() # Yes, we don't support backpack rotations
        clientId = packet.uint16()
        stackpos = packet.uint8()
        
        # TODO: WalkTo
        item = game.map.getTile(position).getThing(stackpos)
        game.engine.transformItem(item, item.rotateTo, position, stackpos)
        
    def handleSetOutfit(self, packet):
        self.outfit = [packet.uint16(), packet.uint8(), packet.uint8(), packet.uint8(), packet.uint8()]
        self.addon = packet.uint8()
        self.mount = packet.uint16() # Not really supported
        self.refreshOutfit()
    
    def handleSetMounted(self, packet):
        if self.mount:
            mount = packet.uint8() != 0
            self.changeMountStatus(mount)
        else:
            self.outfitWindow()
            
    def handleUse(self, packet):
        position = packet.position()

        clientId = packet.uint16() # Junk I tell you :p
        stackpos = packet.uint8()
        index = packet.uint8()
        thing = self.findItem(position, stackpos)

        if thing:
            game.scriptsystem.get('use').run(thing, self, None, position=position, stackpos=stackpos, index=index)

    def handleUseWith(self, packet):
        game.engine.explainPacket(packet)
        position = packet.position()
        clientId = packet.uint16() # Junk I tell you :p
        stackpos = packet.uint8()
        
        onPosition = packet.position()
        onId = packet.uint16()
        onStack = packet.uint8()
        
        thing = self.findItem(position, stackpos)
        
        if thing:
            game.scriptsystem.get('useWith').run(thing, self, None, position=position, stackpos=stackpos, onPosition=onPosition, onId=onId, onStackpos=onStack)

    def attackTarget(self):
        if self.target and self.inRange(self.target.position, 1, 1):
            if not self.inventory[5]:
                self.message("Fist is not supported, targetcheck failed!")
            else:
                
                if not self.target.data["health"]:
                    self.target = None
                else:
                    dmg = -1 * random.randint(0, round(config.meleeDamage(self.inventory[5].attack, 1, self.data["level"], 1)))
                    self.target.onHit(self, dmg, game.enum.PHYSICAL)
                
                
        if self.target:        
            self.targetChecker = reactor.callLater(config.meleeAttackSpeed, self.attackTarget)
                
    def handleAttack(self, packet):
        cid = packet.uint32()
        print "CreatureID %d" %  cid
        if self.targetMode == 1:
            self.targetMode = 0
            self.target = None
            try:
                self.targetChecker.cancel()
            except:
                pass
            return
            
        if cid in allCreatures:
            print allCreatures[cid].position
            self.target = allCreatures[cid]
            self.targetMode = 1
        else:
            self.notPossible()
            
        if self.modes[1] == game.enum.CHASE:
            game.engine.autoWalkCreatureTo(self, self.target.position, -1, True)
            self.target.scripts["onNextStep"].append(self.__followCallback)

        try:
            self.targetChecker.cancel()
        except:
            pass        
        self.attackTarget()
        
    def __followCallback(self, who):
        if self.target == who:
            game.engine.autoWalkCreatureTo(self, self.target.position, -1, True)
            self.target.scripts["onNextStep"].append(self.__followCallback)
            
    def handleFollow(self, packet):
        cid = packet.uint32()
        
        if self.targetMode == 2:
            self.targetMode = 0
            self.target = None
            return
            
        if cid in allCreatures:
            self.target = allCreatures[cid]
            self.targetMode = 2
            game.engine.autoWalkCreatureTo(self, self.target.position, -1, True)
            self.target.scripts["onNextStep"].append(self.__followCallback)
        else:
            self.notPossible()

    def handleUpdateContainer(self, packet):
        openId = packet.uint8()
        
        parent = False
        try:
            parent = bool(container.parent)
        except:
            pass
        self.openContainer(self.openContainers[openId], parent=parent, update=True)
        
    def handlePlayerBuy(self, packet):
        from game.item import sid
        if not self.openTrade:
            return
            
        clientId = packet.uint16()
        count = packet.uint8()
        amount = packet.uint8()
        ignoreCapasity = packet.uint8()
        withBackpack = packet.uint8()
        
        self.openTrade.buy(self, sid(clientId), count, amount, ignoreCapasity, withBackpack)
        
    def handlePlayerSale(self, packet):
        from game.item import sid
        if not self.openTrade:
            return
            
        clientId = packet.uint16()
        count = packet.uint8()
        amount = packet.uint8()
        ignoreEquipped = packet.uint8() 
        
        self.openTrade.sell(self, sid(clientId), count, amount, ignoreEquipped)

    def handleWriteBack(self, packet):
        windowId = packet.uint32()
        text = packet.string()
        
        if windowId in self.windowHandlers:
            self.windowHandlers[windowId](text)