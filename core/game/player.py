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

import game.vocation
global anyPlayer
anyPlayer = CreatureBase()

class TibiaPlayer(Creature):
    def __init__(self, client, data):
        Creature.__init__(self, data, [int(data['posx']),int(data['posy']),int(data['posz'])])
        self.client = client
        self.inventory = [Item(8820), Item(2125), Item(1987), Item(2463), None, Item(7449), None, None, None, Item(2546, 20), None]
        self.speed = 220
        self.modes = [0,0,0]
        self.gender = 0
        self.base = anyPlayer
        self.knownCreatures = []
        self.openContainers = []
        self.doingSoulGain = False
        
        vocation = self.getVocation()
        level = 1
        while True:
            if config.totalExpFormula(level) > self.data["experience"]:
                break
            level += 1
        
        maglevel = 1
        while True:
            if config.totalMagicLevelFormula(maglevel, vocation.mlevel) > self.data["manaspent"]:
                break
            maglevel += 1
        self.data["maglevel"] = maglevel
        self.setLevel(level, False)
        self.speed = min(220.0 + (2 * int(data["level"])-1), 1500.0)
    

            
        

    def generateClientID(self):
        return 0x10000000 + uniqueId()

    def isPlayer(self):
        return True
        
    def sendFirstPacket(self):
        
        stream = TibiaPacket(0x0A)

        stream.uint32(self.clientId()) # Cid
        stream.uint16(self.speed) # Speed
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
        
        stream.worldlight(enum.LIGHTLEVEL_WORLD, enum.LIGHTCOLOR_WHITE)
        stream.creaturelight(self.cid, enum.LIGHTLEVEL_WORLD, enum.LIGHTCOLOR_WHITE)
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
        stream.uint32(self.data["capasity"]) # TODO: Free Capasity
        stream.uint32(self.data["capasity"]) # TODO: Cap
        stream.uint64(self.data["experience"]) # TODO: Virtual cap? Experience
        stream.uint16(self.data["level"]) # TODO: Virtual cap? Level
        stream.uint8(config.levelFormula(self.data["level"]+1) / self.data["experience"]) # % to next level, TODO
        stream.uint16(self.data["mana"]) # mana
        stream.uint16(self.data["manamax"]) # mana max
        stream.uint8(self.data["maglevel"]) # TODO: Virtual cap? Manalevel
        stream.uint8(1) # TODO: Virtual cap? ManaBase
        stream.uint8(0) # % to next level, TODO
        stream.uint8(self.data["soul"]) # TODO: Virtual cap? Soul
        stream.uint16(self.data["stamina"] / (1000 * 60)) # Stamina minutes
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
        for x in xrange(0,7): # 7 skill types
            stream.uint8(1) # Value / Level
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
        print "Find"
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
        print "Replace"
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
        self.data["level"] = level
        
        self.data["healthmax"] = vocation.maxHP(self.data["level"])
        self.data["manamax"] = vocation.maxMana(self.data["level"])
        self.data["capasity"] = vocation.maxCapasity(self.data["level"])
        
        if self.data["health"] > self.data["healthmax"]:
            self.data["health"] = self.data["healthmax"]
            
        if self.data["mana"] > self.data["manamax"]:
            self.data["mana"] = self.data["manamax"]
        
        if send: self.refreshStatus()
        
    def modifyExperience(self, exp):
        up = True
        if exp < 0:
            up = False
            
        self.data["experience"] += exp
        
        if up:
            level = 0
            while True:
                if config.totalExpFormula(self.data["level"]+level) > self.data["experience"]:
                    break
                level += 1
            if level:
                self.setLevel(self.data["level"]+level)
        else:
            level = 0
            while True:
                if config.totalExpFormula(self.data["level"]-level) > self.data["experience"]:
                    break
                level += 1
            if level:
                self.setLevel(self.data["level"]-level)            

    # Soul
    def soulGain(self):
        def doSoulGain(self, gainOverX):
            self.modifySoul(1)
            if self.doingSoulGain - gainOverX >= time.time():
                game.engine.safeCallLater(gainOverX, doSoulGain, gainOverX)
            else:
                self.doingSoulGain = False
                
        if self.doingSoulGain:
            self.doingSoulGain = time.time() + config.soulGain
        else:
            self.doingSoulGain = time.time() + config.soulGain
            gainTime = self.getVocation().soulticker
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
        
        if self.targetMode == 1 and self.modes[1] != 1 and chase == 1:
            game.engine.autoWalkCreatureTo(self, self.target.position, -1, False)
            self.target.scripts["onNextStep"].append(self.__followCallback)
            
        self.modes[1] = chase
        self.modes[2] = secure
        print self.modes
        
        
            
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
        
    def message(self, message, msgType=enum.MSG_STATUS_DEFAULT):
        stream = TibiaPacket(0xB4)
        stream.uint8(msgType)
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
    
    def textWindow(self, item, canWrite=False, maxLen=0xFF, text="", writtenBy="", date=""):
        stream = TibiaPacket(0x96)
        stream.uint32(0x100)
        stream.uint16(item.itemId)
        if canWrite:
            stream.uint16(len(text)+maxLen)
            stream.string(text)
        else:
            stream.uint16(len(text))
            stream.string(text)
        
        stream.string(writtenBy)
        stream.string(date)
        
        stream.send(self.client)
        
    def stopAutoWalk(self):
        try:
            engine.walkerEvents[self.clientId()].cancel()
            del engine.walkerEvents[self.clientId()]
        except:
            pass
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
    
    def closeChannel(self, id):
        channel = game.chat.getChannel(id)
        channel.removeMember(self)
        
    # Compelx packets
    def handleSay(self, packet):
        channelType = packet.uint8()
        channelId = 0
        if channelType in (enum.MSG_CHANNEL_MANAGEMENT, enum.MSG_CHANNEL, enum.MSG_CHANNEL_HIGHLIGHT):
            channelId = packet.uint16()
            
        text = packet.string()
        def endCallback():
	  if len(text) > config.maxLengthOfSay:
	      self.message("Message too long")
	      return
	  log.msg("chat  type %d" % channelType)
	  stream = TibiaPacket(0xAA)
	  stream.uint32(1)
	  stream.string(self.data["name"])
	  stream.uint16(self.data["level"])
	  stream.uint8(enum.MSG_CHANNEL if channelId else enum.MSG_SPEAK_SAY)
	  if channelId:
	      stream.uint16(channelId)
	  else:
	      stream.position(self.position)
	  stream.string(text)
	  stream.send(self.client)

        def part1():
            game.scriptsystem.get("talkaction").run(text, self, endCallback, text=text)
            
        if len(text.split(" ")) > 1:
            game.scriptsystem.get("talkactionFirstWord").run(text.split(" ", 1)[0], self, part1, text=text.split(" ", 1)[1])
        else:
            part1()

    def handleAutoWalk(self, packet):
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
            def afterScript():
                extra = ""
                # TODO propper description handling
                if config.debugItems:
                    extra = "(ItemId: %d, Cid: %d)" % (thing.itemId, clientId)
                self.message("You see %s%s. %s%s" % (items[thing.itemId]["article"]+" " if items[thing.itemId]["article"] else "", items[thing.itemId]["name"], items[thing.itemId]["description"] if "description" in items[thing.itemId] else "", extra))

            game.scriptsystem.get('lookAt').run(thing, self, afterScript, position=position, stackpos=stackpos)
        else:
            self.notPossible()
            
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
            
    def handleAttack(self, packet):
        cid = packet.uint32()
        print "CreatureID %d" %  cid
        if self.targetMode == 1:
            self.targetMode = 0
            self.target = None
            return
            
        if cid in allCreatures:
            print allCreatures[cid].position
            self.target = allCreatures[cid]
            self.targetMode = 1
        else:
            self.notPossible()
            
        if self.modes[1] == game.enum.CHASE:
            game.engine.autoWalkCreatureTo(self, self.target.position, -1, False)
            self.target.scripts["onNextStep"].append(self.__followCallback)

    def __followCallback(self, who):
        if self.target == who:
            game.engine.autoWalkCreatureTo(self, self.target.position, -1, False)
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
            game.engine.autoWalkCreatureTo(self, self.target.position, -1, False)
            self.target.scripts["onNextStep"].append(self.__followCallback)
        else:
            self.notPossible()
        