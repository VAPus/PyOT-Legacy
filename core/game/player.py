from packet import TibiaPacket
from game import enum, engine
from game.map import placeCreature, removeCreature, getTile
from twisted.python import log
import config
from collections import deque
import game.scriptsystem
from game.item import Item
from twisted.internet.defer import inlineCallbacks, deferredGenerator, waitForDeferred, Deferred
from game.creature import Creature
import copy
import game.resource

class TibiaPlayer(Creature):
    def __init__(self, client, data):
        Creature.__init__(self, data, [50,50,7], client.client_id)
        self.client = client
        self.inventory = [Item(8820), Item(2125), Item(1987), Item(2463), None, Item(7449), None, None, None, Item(2546, 20), None]
        self.modes = [0,0,0]
        self.gender = 0

    def sendFirstPacket(self):
        stream = TibiaPacket(0x0A)
        stream.uint32(self.clientId()) # Cid
        stream.uint16(0x0032) # Speed
        stream.uint8(1) # Rule violations?

        stream.uint8(0x64) # Map description
        stream.position(self.position)
        stream.map_description((self.position[0] - 8, self.position[1] - 6, self.position[2]), 18, 14)

        for slot in xrange(enum.SLOT_FIRST,enum.SLOT_LAST):
            if self.inventory[slot-1]:
                stream.uint8(0x78)
                stream.uint8(slot)
            
                stream.item(self.inventory[slot-1])
                
        self.stream_status(stream)
        self.stream_skills(stream)
        
        stream.worldlight(enum.LIGHTLEVEL_WORLD, enum.LIGHTCOLOR_WHITE)
        stream.creaturelight(self.client.client_id, enum.LIGHTLEVEL_WORLD, enum.LIGHTCOLOR_WHITE)
        stream.uint8(0xA2) # Icons
        stream.uint16(0) # TODO: Icons

        stream.magicEffect(self.position, 0x02)
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
        stream.uint8(self.stackpos)
        
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
        stream.map_description((position[0] - 8, position[1] - 6, position[2]), 18, 14)
        
        
        self.position = position
        
        
        stream.magicEffect(self.position, 0x02)
        
        stream.send(self.client)
    def pong(self):
        TibiaPacket(0x1E).send(self.client)
        
    def updateMap(self, direction, streamX=None):
        stream = streamX
        if not streamX:
            stream = TibiaPacket()
        stream.uint8(0x65 + direction)
        if direction is 0:
            stream.map_description((self.position[0] - 8, self.position[1] - 5, self.position[2]), 18, 1)
        elif direction is 1:
            stream.map_description((self.position[0] + 8, self.position[1] - 6, self.position[2]), 1, 14)
        elif direction is 2:
            stream.map_description((self.position[0] - 8, self.position[1] + 6, self.position[2]), 18, 1)
        elif direction is 3:
            stream.map_description((self.position[0] - 7, self.position[1] - 6, self.position[2]), 1, 14)

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
        
    def say(self, message):
        stream = TibiaPacket(0xAA)
        stream.uint32(1)
        stream.string(self.data["name"])
        stream.uint16(self.data["level"])
        stream.uint8(enum.MSG_SPEAK_SAY)
        stream.position(self.position)
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
    
    def refreshOutfit(self):
        stream = TibiaPacket(0x8E)
        stream.uint32(self.clientId())
        stream.outfit(self.outfit, self.addon, self.mount if self.mounted else 0x00)
        stream.sendto(game.engine.getSpectators(self.position))

    def changeMountStatus(self, mounted):
        self.mounted = mounted
        if game.resource.reverseMounts[self.mount].speed:
            self.setSpeed((self.speed + game.resource.reverseMounts[self.mount].speed) if mounted else (self.speed - game.resource.reverseMounts[self.mount].speed))
        self.refreshOutfit()
        
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
     
    def handleMoveItem(self, packet):
        from game.item import Item, sid, items
        fromPosition = [packet.uint16()]
        fromMap = False
        toMap = False
        if fromPosition[0] == 0xFFFF:
            # From hands
            fromInventoryPos = packet.uint8()
            packet.pos += 2 # 0x0000

        else:
            # From map
            fromMap = True
            fromPosition.append(packet.uint16())
            fromPosition.append(packet.uint8())
        
        clientId = packet.uint16()
        fromStackPos = packet.uint8()
        toPosition = [packet.uint16()]
        if toPosition[0] == 0xFFFF:
            # to hands
            toInventoryPos = packet.uint8()
            packet.pos += 2
        else:
            toMap = True
            toPosition.append(packet.uint16())
            toPosition.append(packet.uint8())            

        count = packet.uint8()
        restoreItem = None
        oldItem = None
        
        isCreature = False
        if clientId < 100:
            isCreature = True
        if not isCreature:
            # Remove item:
            if fromMap:
                stream = TibiaPacket()
                if "stackable" in game.item.items[sid(clientId)] and count < 100:
                    oldItem = game.map.getTile(fromPosition).getThing(fromStackPos)
                    oldItem.reduceCount(count)
                    if oldItem.count:
                        stream.updateTileItem(fromPosition, fromStackPos, oldItem)
                    else:
                        stream.removeTileItem(fromPosition, fromStackPos)
                        game.map.getTile(fromPosition).removeClientItem(clientId, fromStackPos)
                        print "taking stackpos = %d" % fromStackPos
                else:
                    
                    stream.removeTileItem(fromPosition, fromStackPos)
                    game.map.getTile(fromPosition).removeClientItem(clientId, fromStackPos)
                    print "taking stackpos = %d" % fromStackPos
                stream.sendto(game.engine.getSpectators(fromPosition))
                
            else:
                stream = TibiaPacket()
                if not toMap and self.inventory[toInventoryPos-1]:
                    # Store item for the last switch action
                    restoreItem = copy.deepcopy(self.inventory[toInventoryPos-1]) # Note, since python will assume reference, we got to use copy here
                    stream.removeInventoryItem(toInventoryPos)
                    self.inventory[toInventoryPos-1] = None
                
                
                if "stackable" in game.item.items[sid(clientId)] and count < 100:
                    oldItem = self.inventory[fromInventoryPos-1]
                    oldItem.reduceCount(count)
                    if oldItem.count:
                        stream.addInventoryItem(fromInventoryPos, oldItem)
                    else:
                        self.inventory[fromInventoryPos-1] = None
                        stream.removeInventoryItem(fromInventoryPos)
                else:
                    self.inventory[fromInventoryPos-1] = None
                    stream.removeInventoryItem(fromInventoryPos)
                
                stream.send(self.client)
            if toMap:
                stream = TibiaPacket()

                newItem = Item(sid(clientId), count)
                findItem = game.map.getTile(toPosition).findClientItem(clientId, True) # Find item for stacking
                if findItem and "stackable" in game.item.items[sid(clientId)] and count < 100 and findItem[1].count + count <= 100:
                    newItem.count += findItem[1].count
                    stream.removeTileItem(toPosition, findItem[0])
                    game.map.getTile(toPosition).removeItem(findItem[1])
                    
                toStackPos = game.map.getTile(toPosition).placeItem(newItem)
                stream.addTileItem(toPosition, toStackPos, newItem )
                print "Sending stackpos = %d" % toStackPos
                stream.sendto(game.engine.getSpectators(toPosition))

            else:
                stream = TibiaPacket()
                if "stackable" in game.item.items[sid(clientId)] and self.inventory[toInventoryPos-1] and (self.inventory[toInventoryPos-1].count + count <= 100):
                    self.inventory[toInventoryPos-1].count += count
                else:       
                    self.inventory[toInventoryPos-1] = Item(sid(clientId), count)
                stream.addInventoryItem(toInventoryPos, self.inventory[toInventoryPos-1])

                if not fromMap and restoreItem:
                    stream.addInventoryItem(fromInventoryPos, restoreItem)
                    self.inventory[fromInventoryPos-1] = restoreItem
                stream.send(self.client)
        else:
            creature = game.map.getTile(fromPosition).getThing(fromStackPos)
            if abs(creature.position[0]-self.position[0]) > 1 or abs(creature.position[1]-self.position[1]) > 1:
                game.engine.autoWalkCreatureTo(self, creature.position, 1, lambda: game.engine.autoWalkCreatureTo(creature, toPosition))
            else:
                game.engine.autoWalkCreatureTo(creature, toPosition)
            
    def handleLookAt(self, packet):
        from game.item import sid, cid, items
        position = [packet.uint16()]
        map = False
        if position[0] == 0xFFFF:
            # From hands
            inventoryPos = packet.uint8()
            packet.pos += 2 # 0x0000

        else:
            # From map
            map = True
            position.append(packet.uint16())
            position.append(packet.uint8())    
            
        clientId = packet.uint16()
        stackpos = packet.uint8()
        itemId = sid(clientId)
        if not itemId:
            return self.notPossible()
            
        if not map and inventoryPos and self.inventory[inventoryPos-1]:
            if itemId != self.inventory[inventoryPos-1].itemId:
                return self.notPossible()
            
            # TODO propper description handling
            self.message("You see %s%s. %s" % (items[itemId]["article"]+" " if items[itemId]["article"] else "", items[itemId]["name"], items[itemId]["description"] if "description" in items[itemId] else ""))
        else:
            # TODO: is the item there?
            self.message("You see %s%s. %s" % (items[itemId]["article"]+" " if items[itemId]["article"] else "", items[itemId]["name"], items[itemId]["description"] if "description" in items[itemId] else ""))
            
            
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
        mount = packet.uint8() != 0
        self.changeMountStatus(mount)
        
    def handleUseItem(self, packet):
        position = packet.position()
        print position
        clientId = packet.uint16()
        stackpos = packet.uint8()
        junk = packet.uint8() # To be supported
        if position[0] == 0xFFFF:
            print self.inventory[position[1]-1].attributes()