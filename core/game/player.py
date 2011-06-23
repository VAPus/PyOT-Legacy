from core.packet import TibiaPacket
from core.game import enum, game
from core.game.map import placeCreature, removeCreature
from twisted.python import log
import config
from collections import deque
import core.game.scriptsystem
from twisted.internet.defer import inlineCallbacks, deferredGenerator, waitForDeferred, Deferred
from core.game.creature import Creature

class TibiaPlayer(Creature):
    def __init__(self, client, data):
        Creature.__init__(self, data, [50,50,7], client.client_id)
        self.client = client
        
    def sendFirstPacket(self):
        stream = TibiaPacket(0x0A)
        stream.uint32(self.clientId()) # Cid
        stream.uint16(0x0032) # Speed
        stream.uint8(1) # Rule violations?

        stream.uint8(0x64) # Map description
        stream.position(self.position)
        stream.map_description((self.position[0] - 8, self.position[1] - 6, self.position[2]), 18, 14)

        for slot in range(enum.SLOT_FIRST,enum.SLOT_LAST):
            stream.uint8(0x78)
            stream.uint8(slot)
            if slot is 3:
                stream.uint16(2853)
            elif slot is 1:
                stream.uint16(7992)
            elif slot is 2:
                stream.uint16(3008)
            elif slot is 4:
                stream.uint16(3357)
            elif slot is 5:
                stream.uint16(7449)
            elif slot is 10:
                stream.uint16(3449)
                stream.uint8(20)
        self.stream_status(stream)
        self.stream_skills(stream)
        
        stream.worldlight(enum.LIGHTLEVEL_WORLD, enum.LIGHTCOLOR_WHITE)
        stream.creaturelight(self.client.client_id, enum.LIGHTLEVEL_WORLD, enum.LIGHTCOLOR_WHITE)
        stream.uint8(0xA2) # Icons
        stream.uint16(0) # TODO: Icons

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
        for x in range(0,7): # 7 skill types
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
        stream.uint16(self.clientId())
        stream.uint8(direction)
		
        # Send to everyone
        # Actually, since we only got one player, jsut send to us
        stream.send(self.client)

    def move(self, direction):
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
        else:
            position[0] = self.position[0] - 1
          
        # We don't walk out of the map!
        if position[0] < 0 or position[1] < 0:
           self.cancelWalk()
           return False
        
        if position[1] is 48:
            self.cancelWalk()
            self.say("Sorry, I'm not allowed to walk up north :p")
            return False
          
        if position[1] is 52:
           self.message("Turbo speed in effect!")
           self.setSpeed(0x9999)
          
        stream.position(position)
        placeCreature(self, position)
        
        self.position = position
        # Send to everyone
        stream.send(self.client)
        
        self.updateMap(direction)
        
        # Hack stackpos
        if self.stackpos is 1:
            self.stackpos += 1
        
        return True # Required for auto walkings
    def pong(self):
        TibiaPacket(0x1E).send(self.client)
        
    def updateMap(self, direction):
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

        stream.send(self.client)
        
        
    def setModes(self, attack, chase, secure):
        self.modes[0] = attack
        self.modes[1] = chase
        self.modes[2] = secure
        
    def setSpeed(self, speed):
        if speed is not self.speed:
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
        
    def stopAutoWalk(self):
        try:
            core.game.game.walkerEvents[self.clientId()].cancel()
            del core.game.game.walkerEvents[self.clientId()]
        except:
            pass
        self.cancelWalk(self.direction)
    
    def windowMessage(self, text):
        stream = TibiaPacket(0x15)
        stream.string(text)
        stream.send(self.client)
        
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
            core.game.scriptsystem.get("talkaction").run(text, self, endCallback, text)
            
        if len(text.split(" ")) > 1:
            core.game.scriptsystem.get("talkactionFirstWord").run(text.split(" ", 1)[0], self, part1, text.split(" ", 1)[1])
        else:
            part1()
    def handleAutoWalk(self, packet):
        steps = packet.uint8()
        log.msg("Steps: %d" % steps)
        walkPattern = deque()
        for x in range(0, steps):
            direction = packet.uint8()
            log.msg("direction %d" % direction)
            if direction is 1:
                walkPattern.append(3) # East
            elif direction is 2:
                walkPattern.append(0) # North
                walkPattern.append(3) # East
            elif direction is 3:
                walkPattern.append(0) # North
            elif direction is 4:
                walkPattern.append(0) # North
                walkPattern.append(1) # West                
            elif direction is 5:
                walkPattern.append(1) # West
            elif direction is 6:
                walkPattern.append(2) # South
                walkPattern.append(1) # West
            elif direction is 7:
                walkPattern.append(2) # South
            elif direction is 8:
                walkPattern.append(2) # South
                walkPattern.append(3) # East               
            else:
                continue # We don't support them
                
        game.autoWalkCreature(self, walkPattern)
     