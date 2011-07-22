from packet import TibiaPacket
from game import enum, engine
from game.map import placeCreature, removeCreature, getTile
from twisted.python import log
import config
from collections import deque
import game.scriptsystem
from game.item import Item
from twisted.internet.defer import inlineCallbacks, deferredGenerator, waitForDeferred, Deferred
from twisted.internet import reactor
from game.creature import Creature, uniqueId
import copy
import game.resource

class TibiaPlayer(Creature):
    def __init__(self, client, data):
        Creature.__init__(self, data, [50,50,7])
        self.client = client
        self.inventory = [Item(8820), Item(2125), Item(1987), Item(2463), None, Item(7449), None, None, None, Item(2546, 20), None]
        self.modes = [0,0,0]
        self.gender = 0
        self.knownCreatures = []
        self.openContainers = []

    def generateClientID(self):
        return 0x10000000 + uniqueId()
        
    def sendFirstPacket(self):
        stream = TibiaPacket(0x0A)

        stream.uint32(self.clientId()) # Cid
        stream.uint16(0x0032) # Speed
        stream.uint8(1) # Rule violations?

        stream.uint8(0x64) # Map description
        stream.position(self.position)
        stream.map_description((self.position[0] - 8, self.position[1] - 6, self.position[2]), 18, 14, self)

        for slot in xrange(enum.SLOT_FIRST,enum.SLOT_LAST):
            if self.inventory[slot-1]:
                stream.uint8(0x78)
                stream.uint8(slot)
            
                stream.item(self.inventory[slot-1])
                
        self.stream_status(stream)
        self.stream_skills(stream)
        
        stream.worldlight(enum.LIGHTLEVEL_WORLD, enum.LIGHTCOLOR_WHITE)
        stream.creaturelight(self.cid, enum.LIGHTLEVEL_WORLD, enum.LIGHTCOLOR_WHITE)
        stream.uint8(0xA2) # Icons
        stream.uint16(0) # TODO: Icons

        stream.magicEffect(self.position, 0x03)
        stream.send(self.client)
        
    def stream_status(self, stream):
        stream.uint8(0xA0)
        stream.uint16(self.data["health"])
        stream.uint16(self.data["healthmax"])
        stream.uint32(10000) # TODO: Free Capasity
        stream.uint32(self.data["cap"]) # TODO: Cap
        stream.uint64(self.data["experience"]) # TODO: Virtual cap? Experience
        stream.uint16(self.data["level"]) # TODO: Virtual cap? Level
        stream.uint8(0) # % to next level, TODO
        stream.uint16(self.data["mana"]) # mana
        stream.uint16(self.data["manamax"]) # mana max
        stream.uint8(self.data["maglevel"]) # TODO: Virtual cap? Manalevel
        stream.uint8(1) # TODO: Virtual cap? ManaBase
        stream.uint8(0) # % to next level, TODO
        stream.uint8(self.data["soul"]) # TODO: Virtual cap? Soul
        stream.uint16(self.data["stamina"] / (1000 * 60)) # Stamina minutes
        stream.uint16(0x0032) # Speed
        
        stream.uint16(0x00) # Condition

    def stream_skills(self, stream):
        stream.uint8(0xA1) # Skill type
        for x in xrange(0,7): # 7 skill types
            stream.uint8(1) # Value / Level
            stream.uint8(1) # Base
            stream.uint8(0) # %
            
            
    def turn(self, direction):
        if self.direction is direction:
	    return
	    
        self.direction = direction
        
        # Make package
        stream = TibiaPacket(0x6B)
        stream.position(self.position)
        stream.uint8(self.stackpos)
        stream.uint16(0x63)
        stream.uint32(self.clientId())
        stream.uint8(direction)
		
        # Send to everyone
        # Actually, since we only got one player, jsut send to us
        stream.send(self.client)

    def move(self, direction):
        import data.map.info
        self.direction = direction
        
        # Make packet
        stream = TibiaPacket(0x6D)
        stream.position(self.position)
        stream.uint8(getTile(self.position).findCreatureStackpos(self))
        
        removeCreature(self, self.position)
        
        # Recalculate position
        position = self.position[:] # Important not to remove the : here, we don't want a reference!
        if direction is 0:
            position[1] = self.position[1] - 1
        elif direction is 1:
            position[0] = self.position[0] + 1
        elif direction is 2:
            position[1] = self.position[1] + 1
        elif direction is 3:
            position[0] = self.position[0] - 1
        elif direction is 4:
            position[1] = self.position[1] + 1
            position[0] = self.position[0] - 1
        elif direction is 5:
            position[1] = self.position[1] + 1
            position[0] = self.position[0] + 1
        elif direction is 6:
            position[1] = self.position[1] - 1
            position[0] = self.position[0] - 1
        elif direction is 7:
            position[1] = self.position[1] - 1
            position[0] = self.position[0] + 1
            
        # We don't walk out of the map!
        if position[0] < 1 or position[1] < 1 or position[0] > data.map.info.width or position[1] > data.map.info.height:
           self.cancelWalk()
           return False
          
        if position[1] is 52:
           self.message("Turbo speed in effect!")
           self.setSpeed(1500)
           
          
        stream.position(position)
        placeCreature(self, position)
        
        self.position = position
        
        if len(self.scripts["onNextStep"]):
            for script in self.scripts["onNextStep"]:
                script()
                self.scripts["onNextStep"].remove(script)
                
            
        # Send to everyone        
        stream.sendto(game.engine.getSpectators(position)) 
        
        if direction < 4:
            self.updateMap(direction)
        else:
            stream = TibiaPacket()
            if direction & 2 == 2:
                # North
                self.updateMap(0, stream)
            else:
                # South
                self.updateMap(2, stream)
            if direction & 1 == 1:
                # East
                self.updateMap(1, stream)
            else:
                # West
                self.updateMap(3, stream)
            stream.send(self.client)
        return True # Required for auto walkings
        
    def teleport(self, position):
        # 4 steps, remove item (creature), send new map and cords, and effects 
        stream = TibiaPacket(0x6C)
        stream.position(self.position)
        stream.uint8(1)
        
        stream.uint8(0x64)
        stream.position(position)
        removeCreature(self, self.position)
        placeCreature(self, position)
        stream.map_description((position[0] - 8, position[1] - 6, position[2]), 18, 14, self)
        
        
        self.position = position
        
        
        stream.magicEffect(self.position, 0x02)
        
        stream.send(self.client)
    def pong(self):
        TibiaPacket(0x1E).send(self.client)
    
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
                openId = position[1] - 64
                for bag in self.openContainers:
                    if bag.openId == openId and bag.container.getThing(position[2]):
                        return bag.container.getThing(position[2])

        # Option 4, find any item the player might posess
        if sid:
            # Inventory
            bags = []
            itemFound = None
            for item in self.inventory:
                if item.itemId is sid:
                    itemFound = item
                    break
                elif item.containerSize:
                    bags.append(item)
                    
            # Bags
            for bag in bags.pop(0):
                for item in bag.items:
                    if item.itemId is sid:
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
            elif self.inventory[2]:
                openId = position[1] - 64
                for bag in self.openContainers:
                    if bag.openId == openId and bag.container.getThing(position[2]):
                        return (2, bag.container.getThing(position[2]), bag)

        # Option 4, find any item the player might posess
        if sid:
            return None # TODO
            
    def getContainer(self, openId):
         for bag in self.openContainers:
             if bag.openId == openId:
                 return bag
                 
    def updateMap(self, direction, streamX=None):
        stream = streamX
        if not streamX:
            stream = TibiaPacket()
        stream.uint8(0x65 + direction)
        if direction is 0:
            stream.map_description((self.position[0] - 8, self.position[1] - 5, self.position[2]), 18, 1, self)
        elif direction is 1:
            stream.map_description((self.position[0] + 9, self.position[1] - 6, self.position[2]), 1, 14, self)
        elif direction is 2:
            stream.map_description((self.position[0] - 8, self.position[1] + 7, self.position[2]), 18, 1, self)
        elif direction is 3:
            stream.map_description((self.position[0] - 7, self.position[1] - 6, self.position[2]), 1, 14, self)

        if not streamX:
            stream.send(self.client)
        
        
    def setModes(self, attack, chase, secure):
        self.modes[0] = attack
        self.modes[1] = chase
        self.modes[2] = secure
        
    def setSpeed(self, speed):
        if speed is not self.speed:
            if speed > 1500:
                speed = 1500
            self.speed = speed
            stream = TibiaPacket(0x8F)
            stream.uint32(self.clientId())
            stream.uint16(speed)
            stream.send(self.client)
            
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
        
    def magicEffect(self, pos, type):
        stream = TibiaPacket()
        stream.magicEffect(pos, type)
        stream.send(self.client)
        
    def shoot(self, fromPos, toPos, type):
        stream = TibiaPacket()
        stream.shoot(fromPos, toPos, type)
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
        
    def refreshOutfit(self):
        stream = TibiaPacket(0x8E)
        stream.uint32(self.clientId())
        stream.outfit(self.outfit, self.addon, self.mount if self.mounted else 0x00)
        stream.sendto(game.engine.getSpectators(self.position))

    def changeMountStatus(self, mounted):
        mount = game.resource.getMount(self.mount)
        if mount:
            self.mounted = mounted
        
            if mount.speed:
                self.setSpeed((self.speed + mount.speed) if mounted else (self.speed - mount.speed))
            self.refreshOutfit()
    
    def updateContainer(self, container, parent=False, update=True):
        self.openContainer(container, parent, update)
        
    def openContainer(self, container, parent=False, update=False):
        if update or not container in self.openContainers:
            stream = TibiaPacket(0x6E)
            if not update:
                container.openId = len(self.openContainers)
            self.openContainers.append(container)
            
            stream.uint8(container.openId)
            
            stream.uint16(container.cid)
            stream.string(container.name())
            
            stream.uint8(container.containerSize)
            stream.uint8(parent)
            stream.uint8(len(container.container.items))
            
            for item in container.container.items:
                stream.item(item)
                
            stream.send(self.client)
            
    def closeContainer(self, container):
        if container in self.openContainers:
            stream = TibiaPacket(0x6F)
            stream.uint8(container.openId)
            self.openContainers.remove(container)
            container.openId = None
            stream.send(self.client)

    def closeContainerId(self, openId):
        for container in self.openContainers:
            if container.openId is openId:
                self.closeContainer(container)
                break

    def arrowUpContainer(self, openId):
        bagFound = None
        for bag in self.openContainers:
            if bag.openId == openId:
                bagFound = bag
                break
                
        if bagFound.parent:
            bagFound.parent.openId = bag.openId
            bagFound.openId = None
            self.openContainers.remove(bagFound)
            self.updateContainer(bagFound.parent, True if bagFound.parent.parent else False)

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
                        if container in self.openContainers:
                            stream.updateContainerItem(container.openId, slot, itemX)
                            
                        if not count:
                            break
                    
                    elif recursive and itemX.containerSize:
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
                
            if recursive and info and info.openId != None:
                stream.addContainerItem(info.openId, item)
                    
            else:
                if container.openId != None:
                    stream.addContainerItem(container.openId, item)
        
        if not streamX:
            stream.send(self.client)
            
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
            game.scriptsystem.get("talkaction").run(text, self, endCallback, text)
            
        if len(text.split(" ")) > 1:
            game.scriptsystem.get("talkactionFirstWord").run(text.split(" ", 1)[0], self, part1, text.split(" ", 1)[1])
        else:
            part1()

    def handleAutoWalk(self, packet):
        steps = packet.uint8()
        log.msg("Steps: %d" % steps)
        walkPattern = deque()
        for x in xrange(0, steps):
            direction = packet.uint8()
            log.msg("direction %d" % direction)
            if direction is 1:
                walkPattern.append(1) # East
            elif direction is 2:
                walkPattern.append(7) # Northeast
            elif direction is 3:
                walkPattern.append(0) # North
            elif direction is 4:
                walkPattern.append(6) # Northwest          
            elif direction is 5:
                walkPattern.append(3) # West
            elif direction is 6:
                walkPattern.append(4) # Southwest
            elif direction is 7:
                walkPattern.append(2) # South
            elif direction is 8:
                walkPattern.append(5) # Southeast           
            else:
                continue # We don't support them
                
        game.engine.autoWalkCreature(self, walkPattern)
    
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
        restoreItem = None
        oldItem = None
        renew = False
        stack = True
        
        isCreature = False
        if clientId < 100:
            isCreature = True
        if not isCreature:
            # Remove item:
            currItem = self.findItemWithPlacement(toPosition)

            if currItem and not (currItem[1].stackable or currItem[1].containerSize):
                currItem = None
                
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
                if toPosition[0] == 0xFFFF and toPosition[1] < 64 and toPosition[1] != game.enum.SLOT_DEPOT and toPosition[1] != oldItem[1].slotId():
                    self.notPossible()
                    return
                    
                if "stackable" in game.item.items[sid(clientId)] and count < 100:
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
                if toPosition[0] == 0xFFFF and toPosition[1] < 64 and toPosition[1] != game.enum.SLOT_DEPOT and toPosition[1] != oldItem[1].slotId():
                    self.notPossible()
                    return
                    
                if "stackable" in game.item.items[sid(clientId)] and count < 100:
                    renew = True
                    oldItem[1].reduceCount(count)
                    if oldItem[1].count:
                        if oldItem[0] == 1:
                            stream.addInventoryItem(fromPosition[1], oldItem[1])
                        elif oldItem[0] == 2:
                            stream.updateContainerItem(oldItem[2].openId, fromPosition[2], oldItem[1])
                    else:
                        if oldItem[0] == 1:
                            self.inventory[fromPosition[1]-1] = None
                            stream.removeInventoryItem(fromPosition[1])
                        elif oldItem[0] == 2:
                            oldItem[2].container.removeItem(oldItem[1])
                            stream.removeContainerItem(oldItem[2].openId, fromPosition[2])
                else:
                    if oldItem[0] == 1:
                        self.inventory[fromPosition[1]-1] = None
                        stream.removeInventoryItem(fromPosition[1])
                    elif oldItem[0] == 2:
                        oldItem[2].container.removeItem(oldItem[1])
                        stream.removeContainerItem(oldItem[2].openId, fromPosition[2])
                
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
                if findItem and "stackable" in game.item.items[sid(clientId)] and count < 100 and findItem[1].count + count <= 100:
                    newItem.count += findItem[1].count
                    stream.removeTileItem(toPosition, findItem[0])
                    game.map.getTile(toPosition).removeItem(findItem[1])
                    
                toStackPos = game.map.getTile(toPosition).placeItem(newItem)
                stream.addTileItem(toPosition, toStackPos, newItem )
                
                if not renew and newItem.containerSize and newItem.openId is not None:
                    self.closeContainer(newItem)
                stream.sendto(game.engine.getSpectators(toPosition))

            else:
                
                if currItem and currItem[1].containerSize:
                    ret = self.itemToContainer(currItem[1], oldItem[1], count=count, stack=stack)

                else:
                    stream = TibiaPacket()
                    if toPosition[1] < 64:
                        if "stackable" in game.item.items[sid(clientId)] and self.inventory[toPosition[1]-1] and self.inventory[toPosition[1]-1].itemId == sid(clientId) and (self.inventory[toPosition[1]-1].count + count <= 100):
                            self.inventory[toPosition[1]-1].count += count
                        else:       
                            self.inventory[toPosition[1]-1] = Item(sid(clientId), count) if renew else oldItem[1]
                        stream.addInventoryItem(toPosition[1], self.inventory[toPosition[1]-1])
                    else:
                        container = self.getContainer(toPosition[1]-64)

                        self.itemToContainer(container, oldItem[1], count=count, stack=stack, streamX=stream)                  
                    if not fromMap and restoreItem:
                        stream.addInventoryItem(fromPosition[1], restoreItem[1])
                        self.inventory[fromPosition[1]-1] = restoreItem[1]
                    stream.send(self.client)
        else:
            if game.map.getTile(toPosition).creatures():
                self.notEnoughRoom()
                return
                
            creature = game.map.getTile(fromPosition).getThing(fromStackPos)    
            if abs(creature.position[0]-self.position[0]) > 1 or abs(creature.position[1]-self.position[1]) > 1:
                walkPattern = game.engine.calculateWalkPattern(creature.position, toPosition)
                if len(walkPattern) > 1:
                    self.outOfRange()
                else:
                    game.engine.autoWalkCreatureTo(self, creature.position, -1, lambda: game.engine.autoWalkCreature(creature, walkPattern))
            else:
                game.engine.autoWalkCreatureTo(creature, toPosition)
            
    def handleLookAt(self, packet):
        from game.item import sid, cid, items
        position = packet.position()
        map = False
        if position[0] != 0xFFFF:
            map = True 
            
        clientId = packet.uint16()
        stackpos = packet.uint8()
        itemId = sid(clientId)
        
        if not itemId:
            return self.notPossible()
        item = self.findItem(position, stackpos)    
        if item:
            if itemId != item.itemId:
                return self.notPossible()
            
            # TODO propper description handling
            self.message("You see %s%s. %s" % (items[itemId]["article"]+" " if items[itemId]["article"] else "", items[itemId]["name"], items[itemId]["description"] if "description" in items[itemId] else ""))
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
            
    def handleUseItem(self, packet):
        game.engine.explainPacket(packet)
        position = packet.position()

        clientId = packet.uint16() # Junk I tell you :p
        stackpos = packet.uint8()
        index = packet.uint8()
        item = self.findItem(position, stackpos)
        
        if item:
            game.scriptsystem.get('useItem').run(item.itemId, self, None, item, position, index)
            
        