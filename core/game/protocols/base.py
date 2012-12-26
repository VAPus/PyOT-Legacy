# This is the "common protocol" in which all other sub protocols is based upon
from packet import TibiaPacket
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet import defer, reactor
from twisted.python import log
import game.enum
import game.map
enum = game.enum
import math
import config
import sys
import game.scriptsystem
from collections import deque
import game.resource
import game.item
import game.party
from struct import pack, unpack
import traceback

######################################
############# BASE PACKET ############
######################################

class BasePacket(TibiaPacket):
    maxKnownCreatures = 1300
    maxOutfits = 29
    maxMounts = 25
    protocolEnums = {}
    _ok_ = []
    """protocolEnums["MSG_NONE"] = 0
    protocolEnums["MSG_SPEAK_SAY"] = 0x01
    protocolEnums["MSG_SPEAK_WHISPER"] = 0x02
    protocolEnums["MSG_SPEAK_YELL"] = 0x03
    protocolEnums["MSG_SPEAK_MONSTER_SAY"] = 0x13
    protocolEnums["MSG_SPEAK_MONSTER_YELL"] = 0x14
    
    protocolEnums["MSG_STATUS_CONSOLE_RED"] = 0x12
    protocolEnums["MSG_EVENT_ORANGE"] = 0x13
    protocolEnums["MSG_STATUS_CONSOLE_ORANGE"] = 0x14
    protocolEnums["MSG_STATUS_WARNING"] = 0x15
    protocolEnums["MSG_EVENT_ADVANCE"] = 0x16
    protocolEnums["MSG_EVENT_DEFAULT"] = 0x17
    protocolEnums["MSG_STATUS_DEFAULT"] = 0x18
    protocolEnums["MSG_INFO_DESCR"] = 0x19
    protocolEnums["MSG_STATUS_SMALL"] = 0x1A
    protocolEnums["MSG_STATUS_CONSOLE_BLUE"] = 0x1B""" # TODO fix this!

    def enum(self, key):
        #return self.protocolEnums[key]
        return getattr(game.enum, key)
        
    # Position
    # Parameters is list(x,y,z)
    def position(self, position):
        self.raw(pack("<HHB", position.x, position.y, position.z))

    # Magic Effect
    def magicEffect(self, pos, type):
        self.raw(pack("<BHHBB", 0x83, pos.x, pos.y, pos.z, type))
   
    # Shoot
    def shoot(self, fromPos, toPos, type):
        self.uint8(0x85)
        self.position(fromPos)
        self.position(toPos)
        self.uint8(type)

    # Item
    # Parameters is of class Item or ItemID
    def item(self, item, count=None):
        if isinstance(item, game.item.Item):
            self.uint16(item.cid)
                
            if item.stackable:
                self.uint8(item.count or 1)
            elif item.type in (11,12):
                self.uint8(item.fluidSource or 0)
            if item.animation:
                self.uint8(0xFE)
            
        else:
            self.uint16(item)
            if count:
                self.uint8(count)
        
    # Map Description (the entier visible map)
    # Isn't "Description" a bad word for it?
    def mapDescription(self, position, width, height, player):
        skip = -1
        start = 7
        end = 0
        step = -1

        # Lower then ground level
        if position.z > 7:
            start = position.z - 2
            end = min(15, position.z + 2) # Choose the smallest of 15 and z + 2
            step = 1

        # Run the steps by appending the floor
        for z in xrange(start, (end+step), step):
            skip = self.floorDescription(position.x, position.y, z, width, height, position.z - z, skip, player)

        if skip >= 0:
            self.raw("%s\xFF" % chr(skip))
            
    # Floor Description (the entier floor)
    def floorDescription(self, _x, _y, _z, width, height, offset, skip, player):
        instanceId = player.position.instanceId
        
        for x in xrange(_x + offset, _x + width + offset):
            for y in xrange(_y + offset, _y + height + offset):
                tile = getTileConst(x, y, _z, instanceId)

                if tile:
                    if skip >= 0:
                        self.raw("%s\xFF" % chr(skip))
                    skip = 0
                    self.tileDescription(tile, player)
                else:
                    skip += 1
                    if skip == 0xFF:
                        self.raw("\xFF\xFF")
                        skip = -1
        return skip

    def tileDescription(self, tile, player):
        self.raw("\x00\x00")
        count = 0
        
        for item in tile.topItems():  
            self.raw(pack("<H", item.cid))
                    
            if item.stackable:
                self.raw(chr(item.count or 1))
            elif item.type in (11,12):
                self.raw(chr(item.fluidSource or 0))
            if item.animation:
                self.raw('\xFE')
            count += 1
            if count == 10:
                return
        
        if not tile.things: return

        for creature in tile.creatures():
            if creature.isMonster() and creature.hasCondition(CONDITION_INVISIBLE):
                continue
            known = False
            removeKnown = 0
            if player:
                known = creature in player.knownCreatures
                    
                if not known:
                    if len(player.knownCreatures) > self.maxKnownCreatures:
                        removeKnown = player.checkRemoveKnown()
                        if not removeKnown:
                            player.exit("Too many creatures in known list. Please relogin")
                            return
                    player.knownCreatures.add(creature)
                    creature.knownBy.add(player)
                    
                    self.creature(creature, known, removeKnown, player)
                else:
                    # Bugged?
                    if creature.creatureType != 0 and creature.brainEvent:
                        if player.client.version >= 953:
                            self.raw(pack("<HIBB", 99, creature.clientId(), creature.direction, creature.solid))
                        else:
                            self.raw(pack("<HIB", 99, creature.clientId(), creature.direction))
                    else:
                        self.creature(creature, True, creature.cid, player) # Not optimal!
            if creature.creatureType != 0 and not creature.brainEvent:
                creature.base.brain.beginThink(creature, False)
                    
            count += 1
            if count == 10:
                return
                
        for item in tile.bottomItems():
            self.raw(pack("<H", item.cid))
                    
            if item.stackable:
                self.raw(chr(item.count or 1))
            elif item.type in (11,12):
                self.raw(chr(item.fluidSource or 0))
            if item.animation:
                self.raw('\xFE')
            count += 1
            if count == 10:
                return
        
    def exit(self, message):
        self.uint8(0x14)
        self.string(message) # Error message

    def outfit(self, look, addon=0, mount=0):
        
        self.uint16(look[0])
        if look[0]:
            self.uint8(look[1])
            self.uint8(look[2])
            self.uint8(look[3])
            self.uint8(look[4])
            self.uint8(addon)
        else:
            self.uint16(look[1])
        if config.allowMounts:    
            self.uint16(mount) # Mount
        else:
            self.uint16(0)
            
    def creature(self, creature, known, removeKnown=0, player=None):
        if known:
            self.uint16(0x62)
            self.uint32(creature.clientId())
        else:
            self.uint16(0x61)
            self.uint32(removeKnown) # Remove known
            self.uint32(creature.clientId())
            self.uint8(creature.creatureType)
            self.string(creature.name())
            
        if not creature.getHideHealth():
            self.uint8(int(round((float(creature.data["health"]) / creature.data["healthmax"]) * 100))) # Health %
        else:
            self.uint8(0)
            
        self.uint8(creature.direction) # Direction
        self.outfit(creature.outfit, creature.addon, creature.mount if creature.mounted else 0x00)
        self.uint8(creature.lightLevel) # Light
        self.uint8(creature.lightColor) # Light
        self.uint16(int(creature.speed)) # Speed
        self.uint8(creature.getSkull(player)) # Skull
        self.uint8(creature.getShield(player)) # Party/Shield
        if not known:
            self.uint8(creature.getEmblem(player)) # Emblem
        self.uint8(creature.solid) # Can't walkthrough
        
    def worldlight(self, level, color):
        self.uint8(0x82)
        self.uint8(level)
        self.uint8(color)

    def creaturelight(self, cid, level, color):
        self.uint8(0x8D)
        self.uint32(cid)
        self.uint8(level)
        self.uint8(color)

    def removeInventoryItem(self, pos):
        self.uint8(0x79)
        self.uint8(pos)
        
    def addInventoryItem(self, pos, item):
        self.uint8(0x78)
        self.uint8(pos)
        self.item(item)

    def addContainerItem(self, openId, item):
        self.uint8(0x70)
        self.uint8(openId)
        self.item(item)
        
    def updateContainerItem(self, openId, slot, item):
        self.uint8(0x71)
        self.uint8(openId)
        self.uint8(slot)
        self.item(item)
       
    def removeContainerItem(self, openId, slot):
        self.uint8(0x72)
        self.uint8(openId)
        self.uint8(slot)
        
    def addTileItem(self, pos, stackpos, item):
        if stackpos > 9: return
        
        self.uint8(0x6A)
        self.position(pos)
        self.uint8(stackpos)
        self.item(item)

    def addTileCreature(self, pos, stackpos, creature, player=None, resend=False):
        if stackpos > 9: return
        
        self.uint8(0x6A)
        self.position(pos)
        self.uint8(stackpos)
        known = False
        removeKnown = 0
        if player:
            known = creature in player.knownCreatures
                    
            if not known:
                if len(player.knownCreatures) > self.maxKnownCreatures:
                    removeKnown = player.checkRemoveKnown()
                    if not removeKnown:
                        player.exit("Too many creatures in known list. Please relogin")
                        return
                player.knownCreatures.add(creature)
                creature.knownBy.add(player)
            elif resend:
                removeKnown = creature.clientId()
                known = False
            self.creature(creature, known, removeKnown, player)

    def moveUpPlayer(self, player, oldPos):
        self.uint8(0xBE)
        
        # Underground to surface
        if oldPos.z-1 == 7:
            skip = self.floorDescription(oldPos.x - 8, oldPos.y - 6, 5, 18, 14, 3, -1, player)
            skip = self.floorDescription(oldPos.x - 8, oldPos.y - 6, 4, 18, 14, 4, skip, player)
            skip = self.floorDescription(oldPos.x - 8, oldPos.y - 6, 3, 18, 14, 5, skip, player)
            skip = self.floorDescription(oldPos.x - 8, oldPos.y - 6, 2, 18, 14, 6, skip, player)
            skip = self.floorDescription(oldPos.x - 8, oldPos.y - 6, 1, 18, 14, 7, skip, player)
            skip = self.floorDescription(oldPos.x - 8, oldPos.y - 6, 0, 18, 14, 8, skip, player)

            if skip >= 0:
                self.uint8(skip)
                self.uint8(0xFF)
                
        elif oldPos.z-1 > 7: # Still underground
            skip = self.floorDescription(oldPos.x - 8, oldPos.y - 6, oldPos.z-3, 18, 14, 3, -1, player)
            
            if skip >= 0:
                self.uint8(skip)
                self.uint8(0xFF)
                
        self.uint8(0x68) # West
        self.mapDescription(Position(oldPos.x - 8, oldPos.y + 1 - 6, oldPos.z-1), 1, 14, player)
        
        self.uint8(0x65) # North
        self.mapDescription(Position(oldPos.x - 8, oldPos.y - 6, oldPos.z-1), 18, 1, player)
         
    def moveDownPlayer(self, player, oldPos):
        self.uint8(0xBF)
        if oldPos.z+1 == 8:
            skip = self.floorDescription(oldPos.x - 8, oldPos.y - 6, oldPos.z+1, 18, 14, -1, -1, player)
            skip = self.floorDescription(oldPos.x - 8, oldPos.y - 6, oldPos.z+2, 18, 14, -2, skip, player)
            skip = self.floorDescription(oldPos.x - 8, oldPos.y - 6, oldPos.z+3, 18, 14, -3, skip, player)

            if skip >= 0:
                self.uint8(skip)
                self.uint8(0xFF)
                
        elif oldPos.z+1 > 8:
            skip = self.floorDescription(oldPos.x - 8, oldPos.y - 6, oldPos.z+3, 18, 14, -3, -1, player)
            
            if skip >= 0:
                self.uint8(skip)
                self.uint8(0xFF)            
        
        self.uint8(0x66) # East
        self.mapDescription(Position(oldPos.x + 9, oldPos.y - 7, oldPos.z+1), 1, 14, player)
        self.uint8(0x67) # South
        self.mapDescription(Position(oldPos.x - 8, oldPos.y + 7, oldPos.z+1), 18, 1, player)

    def updateTileItem(self, pos, stackpos, item):
        if stackpos > 9: return
        self.uint8(0x6B)
        self.position(pos)
        self.uint8(stackpos)
        self.item(item)
        
    def removeTileItem(self, pos, stackpos):
        if stackpos > 9: return
        self.uint8(0x6C)
        self.position(pos)
        self.uint8(stackpos)
    def status(self, player):
        self.uint8(0xA0)
        self.uint16(player.data["health"])
        self.uint16(player.data["healthmax"])
        self.uint32(player.freeCapacity())
        self.uint32(player.data["capacity"] * 100)
        self.uint64(player.data["experience"])
        if player.data["level"] > 0xFFFF:
            self.uint16(0xFFFF)
        else:
            self.uint16(player.data["level"])
        
        if not player.data["experience"]:
            self.uint8(int(math.ceil(float(config.levelFormula(player.data["level"]+1)) / player.data["experience"]))) # % to next level, TODO
        else:
            self.uint8(0)
            
        self.uint16(player.data["mana"]) # mana
        self.uint16(player.data["manamax"]) # mana max
        if player.data["maglevel"] > 255:
            self.uint8(255)
            self.uint8(255)
        else:
            self.uint8(player.data["maglevel"])
            self.uint8(player.data["maglevel"]) # TODO: Virtual cap? ManaBase
        self.uint8(int(player.data["manaspent"] / int(config.magicLevelFormula(player.data["maglevel"], player.getVocation().mlevel)))) # % to next level, TODO
        self.uint8(player.data["soul"]) # TODO: Virtual cap? Soul
        self.uint16(min(42 * 60, int(player.data["stamina"] / 60))) # Stamina minutes
        self.uint16(int(player.speed)) # Speed
        if player.client.version > 961:
            self.uint16(0x00) # Regeneration time
        self.uint16(0x00) # Offline training time

    def skills(self, player):
        self.uint8(0xA1) # Skill type
        for x in xrange(game.enum.SKILL_FIRST, game.enum.SKILL_LAST+1):
            self.uint8(player.skills[x]) # Value / Level
            self.uint8(player.data["skills"][x]) # Base
            currHits = player.data["skill_tries"][x]
            goalHits = player.skillGoals[x]
            if currHits < 1:
                self.uint8(0)
            else:
                self.uint8(int(round((currHits / goalHits) * 100))) # %

    def cooldownIcon(self, icon, cooldown):
        self.uint8(0xA4)
        self.uint8(icon)
        self.uint32(cooldown * 1000)
        
    def cooldownGroup(self, group, cooldown):
        self.uint8(0xA5)
        self.uint8(group)
        self.uint32(cooldown * 1000)

    def violation(self, flag):
        pass # Not on 9.1

    def icons(self, icons):
        self.uint8(0xA2)
        self.uint16(icons)

    def message(self, player, message, msgType=game.enum.MSG_STATUS_DEFAULT, color=0, value=0, pos=None):
        self.uint8(0xB4)
        self.uint8(self.enum(msgType))
        if msgType in (MSG_DAMAGE_DEALT, MSG_DAMAGE_RECEIVED, MSG_DAMAGE_OTHERS):
            if pos:
                self.position(pos)
            else:
                self.position(player.position)
            self.uint32(value)
            self.uint8(color)
            self.uint32(0)
            self.uint8(0)
        elif msgType in (MSG_EXPERIENCE, MSG_EXPERIENCE_OTHERS, MSG_HEALED, MSG_HEALED_OTHERS):
            if pos:
                self.position(pos)
            else:
                self.position(player.position)
            self.uint32(value)
            self.uint8(color)
            
        self.string(message)

    def vipLogin(self, playerId):
        self.uint8(0xD3)
        self.uint32(playerId)
        
    def vipLogout(self, playerId):
        self.uint8(0xD4)
        self.uint32(playerId)
        
    def vip(self, playerId, playerName, online=False):
        self.uint8(0xD2)
        self.uint32(playerId)
        self.string(playerName)
        self.uint8(online)
        
    def openChannels(self, channels):
        self.uint8(0xAB)
        self.uint8(len(channels))
        for channelId in channels:
            self.uint16(channelId)
            self.string(channels[channelId].name)

    def openChannel(self, channel):
        self.uint8(0xAC)
        self.uint16(channel.id)
        self.string(channel.name)

        # TODO: Send members for certain channels
        self.uint32(0)

    def say(self, player, message, msgType=game.enum.MSG_STATUS_DEFAULT, color=0, value=0, pos=None):
        self.uint8(0xAA)
        self.uint8(self.enum(msgType))
        if msgType in (MSG_DAMAGE_DEALT, MSG_DAMAGE_RECEIVED, MSG_DAMAGE_OTHERS):
            if pos:
                self.position(pos)
            else:
                self.position(player.position)
            self.uint32(value)
            self.uint8(color)
            self.uint32(0)
            self.uint8(0)
        elif msgType in (MSG_EXPERIENCE, MSG_EXPERIENCE_OTHERS, MSG_HEALED, MSG_HEALED_OTHERS):
            if pos:
                self.position(pos)
            else:
                self.position(player.position)
            self.uint32(value)
            self.uint8(color)
            
        self.string(message)
        
    def playerInfo(self, player):
        # 9.5+
        if player.client.version >= 950:
            self.uint8(0x9F)
            self.uint8(player.sendPremium)
            self.uint8(player.getVocationId())
            
            # Spell counting.
            spells = player.getSpells()
            
            self.uint16(len(spells))
            randomNr = 0
            for spell in spells:
                # TODO: Implant spell ids, unfortunatly we can't do witout them.
                self.uint8(randomNr)
                randomNr += 1
                
    def dialog(self, player, dialogId, title, message, buttons=["Ok", "Exit"], defaultEnter=0, defaultExit=1):
        # 9.6+
        if player.client.version >= 960:
            self.uint8(0xFA)
            self.uint32(dialogId)
            self.string(title)
            self.string(message)
            self.uint8(len(buttons))
            for button in xrange(len(buttons)):
                self.string(buttons[button])
                self.uint8(button)
                
            self.uint8(defaultEnter)
            self.uint8(defaultExit)
        else:
            pass # TODO send as a text dialog.
            
    def delayWalk(self, delay):
        self.uint8(0xb6)
        self.uint16(delay * 1000)
        
    def skull(self, creatureId, skull):
        self.uint8(0x90)
        self.uint32(creatureId)
        self.uint8(skull)
        
    def shield(self, creatureId, shield):
        self.uint8(0x91)
        self.uint32(creatureId)
        self.uint8(shield)

###########################################
############## BASE PROTOCOL ##############
###########################################

OPHANDLERS = {}
def packet(opcode):
    global OPHANDLERS
    def _(f):
        OPHANDLERS[opcode] = f
        return f

    return _
        
class BaseProtocol(object):
    Packet = BasePacket    
    def handle(self, player, packet):
        packetType = packet.uint8()

        if packetType in OPHANDLERS:
            try:
                 OPHANDLERS[packetType](self, player, packet)
            except:
                if IS_IN_TEST:
                    raise
                else:
                    print "\n\n[UNHANDLED CORE EXCEPTION!]"
                    traceback.print_exc()
                    print "==============================\n"
        else:
            log.msg("Unhandled packet (type = {0}, length: {1}, content = {2})".format(hex(packetType), len(packet.data), ' '.join( map(str, map(hex, map(ord, packet.getData())))) ))
            #self.transport.loseConnection()

 
    def enum(self, key):
        return getattr(game.enum, key)

    @packet(0x14)
    def handleLogout(self, player, packet):
        try:
            if player.prepareLogout():
                player.client.transport.loseConnection()
        except:
            pass # Sometimes the connection is already dead
    
    @packet(0x1E)
    def handleKeepAlive(self, player, packet):
        player.pong()
    
    @packet(0x96)
    def handleSay(self, player, packet):
        channelType = packet.uint8()
        channelId = 0
        reciever = ""

        if channelType in (self.enum(MSG_CHANNEL_MANAGEMENT), self.enum(MSG_CHANNEL), self.enum(MSG_CHANNEL_HIGHLIGHT)):
            channelId = packet.uint16()
        elif channelType in (self.enum(MSG_PRIVATE_TO), self.enum(MSG_GAMEMASTER_PRIVATE_TO)):
            reciever = packet.string()

        text = packet.string()
        
        player.handleSay(channelType, channelId, reciever, text)

    @packet(0x97)
    def handleRequestChannels(self, player, packet):
        player.openChannels()

    @packet(0x98)
    def handleOpenChannel(self, player, packet):
        player.openChannel(packet.uint16())

    @packet(0x99)
    def handleCloseChannel(self, player, packet):
        player.closeChannel(packet.uint16())

    @packet(0x9A)
    def handleOpenPrivateChannel(self, player, packeet):
        player.openPrivateChannel(game.engine.getPlayer(packet.string()))

    @packet(0x64)
    def handleAutoWalk(self, player, packet):
        if player.target:
            player.target = None
            player.targetMode = 0
            player.cancelTarget()

        player.stopAction()  
        player.walkPattern = deque()
        
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
        
        player.walkPattern = walkPattern
        game.engine.autoWalkCreature(player)

    @packet(0x65)
    def handleWalkNorth(self, player, packet):
        self.handleWalk(player, NORTH)

    @packet(0x67)
    def handleWalkSouth(self, player, packet):
        self.handleWalk(player, SOUTH)

    @packet(0x66)
    def handleWalkEast(self, player, packet):
        self.handleWalk(player, EAST)

    @packet(0x68)
    def handleWalkWest(self, player, packet):
        self.handleWalk(player, WEST)
    
    @packet(0x69)
    def handleStopAutoWalk(self, player, packet):
        player.stopAutoWalk()

    @packet(0x6A)
    def handleWalkNorthEast(self, player, packet):
        self.handleWalk(player, 7)

    @packet(0x6B)
    def handleWalkSouthEast(self, player, packet):
        self.handleWalk(player, 5)

    @packet(0x6C)
    def handleWalkNorthWest(self, player, packet):
        self.handleWalk(player, 4)

    @packet(0x6D)
    def handleWalkSouthWest(self, player, packet):
        self.handleWalk(player, 6)

    @packet(0x6F)
    def handleTurn0(self, player, packet):
        player.turn(0)

    @packet(0x70)
    def handleTurn1(self, player, packet):
        player.turn(1)

    @packet(0x71)
    def handleTurn2(self, player, packet):
        player.turn(2)

    @packet(0x72)
    def handleTurn3(self, player, packet):
        player.turn(3)

    def handleWalk(self, player, direction):
        if player.target and player.modes[1] == game.enum.CHASE and player.targetMode > 0:
            player.cancelTarget()
            player.target = None
            player.targetMode = 0

        player.lastClientMove = direction        
        player.walkPattern = deque((direction,))
        game.engine.autoWalkCreature(player)

    @packet(0x78)
    @inlineCallbacks
    def handleMoveItem(self, player, packet):
        from game.item import items
        fromPosition = packet.position(player.position.instanceId)
        fromMap = False
        toMap = False

        if fromPosition.x != 0xFFFF:
            # From map
            fromMap = True
        
        clientId = packet.uint16()
        fromStackPos = packet.uint8()
        toPosition = packet.position(player.position.instanceId)
        if toPosition.x != 0xFFFF:
            toMap = True
        
        count = packet.uint8()
        oldItem = None
        renew = False
        stack = True
        fromPosition = fromPosition.setStackpos(fromStackPos)
        thing = player.findItem(fromPosition)

        if not thing:
            player.notPossible()
            return

        if not thing.position:
            thing.position = fromPosition
        isCreature = False
        if clientId < 100:
            isCreature = True
        if not isCreature:
            # Remove item:
            oldItem = player.findItemWithPlacement(fromPosition)
            if not thing.position:
                thing.position = fromPosition
                
            if toPosition.x == 0xFFFF:
                currItem = player.findItemWithPlacement(toPosition)
            else:
                currItem = None

            if fromMap:
                # This means we need to walk to the item
                if not player.inRange(fromPosition, 1, 1):

                    walkPattern = game.engine.calculateWalkPattern(player, player.position, fromPosition, -1)

                    # No walk pattern means impossible move.
                    if not walkPattern:
                        player.notPossible()
                        return

                    # Some half sync yield -> sleep walking
                    def sleep(seconds):
                        d = Deferred()
                        reactor.callLater(seconds, d.callback, seconds)
                        return d
                    
                    walking = [True]
                    scount = 0
                    player.walkPattern = deque(walkPattern)
                    game.engine.autoWalkCreature(player, lambda: walking.pop())
                    while walking and scount < 100:
                        yield sleep(0.1)
                        scount += 1

                    # Vertify, we might have been stopped on the run
                    if not player.inRange(fromPosition, 1, 1):
                        player.notPossible()
                        return
  
                    if toPosition.x == 0xFFFF and toPosition.y >= 64 and not player.getContainer(toPosition.y-64):
                        player.notPossible()
                        return
            if player.canSee(fromPosition) and player.canSee(toPosition):
                moveItem(player, fromPosition, toPosition, count)
            
        else:
            if not player.canSee(toPosition):
                return
            
            if toPosition.getTile().topCreature():
                player.notEnoughRoom()
                return
                
            creature = game.map.getTile(fromPosition).getThing(fromStackPos)
            if not creature or not isinstance(creature, Creature):
                return
            if not creature.isPushable(player):
                player.message("Creature can't be pushed")
                return
                
            toTile = game.map.getTile(toPosition)
            for i in toTile.getItems():
                if i.solid:
                    player.notPossible()
                    return
            if abs(creature.position.x-player.position.x) > 1 or abs(creature.position.y-player.position.y) > 1:
                walkPattern = game.engine.calculateWalkPattern(player, creature.position, toPosition)
                if len(walkPattern) > 1:
                    player.outOfRange()
                else:
                    game.engine.autoWalkCreatureTo(player, creature.position, -1, True, lambda: game.engine.autoWalkCreatureTo(creature, toPosition))
            else:
                game.engine.autoWalkCreatureTo(creature, toPosition)
        
    @packet(0x8C)    
    def handleLookAt(self, player, packet):
        from game.item import items
        position = packet.position(player.position.instanceId)
        
        clientId = packet.uint16()
        stackpos = packet.uint8()
        
        stackPosition = position.setStackpos(stackpos)
        
        if not player.canSee(position):
            return
        
        if position.x == 0xFFFF:
            thing = player.findItem(stackPosition)
        elif stackpos == 0 and clientId == 99:
            thing = None
            try:
                thing = game.map.getTile(position).topCreature()
            except:
                pass

            if not thing:
                player.notPossible()
                return
        else:
            thing = player.findItem(stackPosition)
            if not thing or thing.cid != clientId:
                for thing2 in game.map.getTile(position).things:
                    if thing2.cid == clientId:
                        thing = thing2
                        break       
        if thing:
            if isinstance(thing, Item):
                def afterScript():
                    extra = ""
                    # TODO propper description handling
                    if config.debugItems:
                        extra = "(ItemId: %d, Cid: %d)" % (thing.itemId, clientId)

                    player.message(thing.description(player) + extra)
            elif isinstance(thing, Creature):
                def afterScript():
                    if player == thing:
                        player.message(thing.description(True))
                    else:
                        player.message(thing.description())
            game.scriptsystem.get('lookAt').runSync(thing, player, afterScript, position=stackPosition)
        else:
            player.notPossible()

    @packet(0x8D)
    def handleLookAtBattleList(self, player, packet):
        creatureId = packet.uint32()

        try:
            creature = game.creature.allCreatures[creatureId]
        except:
            return

        if not player.canSee(creature):
            return

        def afterScript():
            if player == creature:
                player.message(creature.description(True))
            else:
                player.message(creature.description())

        game.scriptsystem.get('lookAt').runSync(creature, player, afterScript, position=creature.position)

    @packet(0x79) # This is in stores. 
    def handleLookAtTrade(self, player, packet):
        clientId = packet.uint16()
        count = packet.uint8()
        
        item = Item(clientId, count)
        player.message(item.description(player))
        del item
        
    @packet(0x85)
    def handleRotateItem(self, player, packet):
        position = packet.position(player.position.instanceId) # Yes, we don't support backpack rotations
        clientId = packet.uint16()
        stackpos = packet.uint8()
        
        if player.inRange(position, 1, 1):
            item = game.map.getTile(position).getThing(stackpos)
            def end():
                game.engine.transformItem(item, item.rotateTo, position, stackpos)
            game.scriptsystem.get('rotate').runSync(item, player, end, position=position.setStackpos(stackpos))
            
    @packet(0xD2)
    def handleRequestOutfit(self, player, packet):
        player.outfitWindow()

    @packet(0xD3)
    def handleSetOutfit(self, player, packet):
        if config.playerCanChangeColor:
            player.outfit = [packet.uint16(), packet.uint8(), packet.uint8(), packet.uint8(), packet.uint8()]
        else:
            player.outfit[0] = packet.uint16()
            
        player.addon = packet.uint8()
        if config.allowMounts and player.client.version >= 870:
            player.mount = packet.uint16()
        player.refreshOutfit()
    
    @packet(0xD4)
    def handleSetMounted(self, player, packet):
        if config.allowMounts:
            if player.mount:
                mount = packet.uint8() != 0
                player.changeMountStatus(mount)
            else:
                player.outfitWindow()
    
    @packet(0x82)        
    @inlineCallbacks        
    def handleUse(self, player, packet):
        position = packet.position(player.position.instanceId)

        clientId = packet.uint16() # Junk I tell you :p
        stackpos = packet.uint8()
        index = packet.uint8()
        stackPosition = position.setStackpos(stackpos)
        thing = player.findItem(stackPosition)
        end = None
        
        thing.position = stackPosition
            
        if config.useDelay and player.lastUsedObject + config.useDelay > time.time():
            player.cantUseObjectThatFast()
            return
        
        if thing and (position.x == 0xFFFF or (position.z == player.position.z and player.canSee(position))):
            if not position.x == 0xFFFF and not player.inRange(position, 1, 1):
                walkPattern = game.engine.calculateWalkPattern(player, player.position, position, -1)

                # No walk pattern means impossible move.
                if not walkPattern:
                    player.notPossible()
                    return

                # Some half sync yield -> sleep walking
                def sleep(seconds):
                    d = Deferred()
                    reactor.callLater(seconds, d.callback, seconds)
                    return d
                    
                scount = 0
                player.walkPattern = deque(walkPattern)
                game.engine.autoWalkCreature(player)
                while player.walkPattern and scount < 100:
                    yield sleep(0.1)
                    scount += 1
                # Add a short delay here. Kinda fix overuse of useDelay.
                yield sleep(0.2)
    
            if position.x == 0xFFFF or player.inRange(position, 1, 1):
                game.scriptsystem.get('use').runSync(thing, player, None, position=stackPosition, index=index)
                if config.useDelay:
                    player.lastUsedObject = time.time()

    @packet(0x83)
    @inlineCallbacks
    def handleUseWith(self, player, packet):
        position = packet.position(player.position.instanceId)
        clientId = packet.uint16() # Junk I tell you :p
        stackpos = packet.uint8()
        
        onPosition = packet.position(player.position.instanceId)
        onClientId = packet.uint16()
        onStack = packet.uint8()
        
        stackPosition1 = position.setStackpos(stackpos)
        stackPosition2 = onPosition.setStackpos(onStack)
        
        if clientId != 99:
            thing = player.findItem(stackPosition1)
        else:
            thing = position.getTile().topCreature()
            
        if not thing:
            return
        if not thing.position:
            thing.position = stackPosition1
            
        if onClientId != 99:
            onThing = player.findItem(stackPosition2)
        else:
            onThing = game.map.getTile(onPosition).topCreature()
        
        if not onThing:
            return

        if not onThing.position:
            onThing.position = stackPosition2
            
        if config.useDelay and player.lastUsedObject + config.useDelay > time.time():
            player.cantUseObjectThatFast()
            return
        
        if thing and onThing and ((position.z == player.position.z and player.canSee(position)) or position.x == 0xFFFF) and ((onPosition.z == player.position.z and player.canSee(onPosition)) or onPosition.x == 0xFFFF):
            if not onPosition.x == 0xFFFF and not player.inRange(onPosition, 1, 1):
                walkPattern = game.engine.calculateWalkPattern(player, player.position, onPosition, -1)

                # No walk pattern means impossible move.
                if not walkPattern:
                    player.notPossible()
                    return

                # Some half sync yield -> sleep walking
                def sleep(seconds):
                    d = Deferred()
                    reactor.callLater(seconds, d.callback, seconds)
                    return d
                    
                walking = [True]
                scount = 0
                player.walkPattern = deque(walkPattern)
                game.engine.autoWalkCreature(player, lambda: walking.pop())
                while walking and scount < 100:
                    yield sleep(0.1)
                    scount += 1

            if (position.x == 0xFFFF or player.inRange(position, 1, 1)) and (onPosition.x == 0xFFFF or player.canSee(onPosition)):
                end = lambda: game.scriptsystem.get('useWith').runDeferNoReturn(onThing, player, None, position=stackPosition2, onPosition=stackPosition1, onThing=thing)
                game.scriptsystem.get('useWith').runDeferNoReturn(thing, player, end, position=stackPosition1, onPosition=stackPosition2, onThing=onThing)
                if config.useDelay:
                    player.lastUsedObject = time.time()
            else:
                player.notPossible()
            
    @packet(0xA0)
    def handleSetModes(self, player, packet):
        player.setModes(packet.uint8(), packet.uint8(), packet.uint8())

    @packet(0xA1)
    def handleAttack(self, player, packet):
        # HACK?
        # If we're in protected zone
        if player.position.getTile().getFlags() & TILEFLAGS_PROTECTIONZONE:
            player.notPossible()
            player.cancelTarget()
        else:
            cid = packet.uint32()
            
            player.setAttackTarget(cid)
            
    @packet(0xA2)
    def handleFollow(self, player, packet):
        cid = packet.uint32()
        player.setFollowTarget(cid)
        
    @packet(0xBE)
    def handleStop(self, player, packet):
        player.stopAction()
        if player.target:
            player.cancelTarget()
            player.target = None
            player.targetMode = 0

    @packet(0xC9)
    def handleUpdateTile(self, player, packet):
        pos = packet.position(player.position.instanceId)
        tile = getTile(pos)
        stream = player.packet(0x69)
        stream.position(pos)
        stream.tileDescription(tile, player)
        stream.uint8(0x00)
        stream.uint8(0xFF)
        stream.send(player.client)
        
    @packet(0xCA)
    def handleUpdateContainer(self, player, packet):
        openId = packet.uint8()
        
        parent = False
        try:
            parent = bool(container.parent)
        except:
            pass
        player.openContainer(player.openContainers[openId], parent=parent, update=True)
        
    @packet(0x7A)
    def handlePlayerBuy(self, player, packet):
        if not player.openTrade:
            return
            
        clientId = packet.uint16()
        count = packet.uint8()
        amount = packet.uint8()
        ignoreCapacity = packet.uint8()
        withBackpack = packet.uint8()
        
        player.openTrade.buy(player, clientId, count, amount, ignoreCapacity, withBackpack)
        
    @packet(0x7B)
    def handlePlayerSale(self, player, packet):
        if not player.openTrade:
            return
            
        clientId = packet.uint16()
        count = packet.uint8()
        amount = packet.uint8()
        ignoreEquipped = packet.uint8() 
        
        player.openTrade.sell(player, clientId, count, amount, ignoreEquipped)

    @packet(0x87)
    def handleCloseContainer(self, player, packet):
        player.closeContainerId(packet.uint8())

    @packet(0x88)
    def handleArrowUpContainer(self, player, packet):
        player.arrowUpContainer(packet.uint8())

    @packet(0x89)
    def handleWriteBack(self, player, packet):
        windowId = packet.uint32()
        text = packet.string()
        
        try:
            player.windowHandlers[windowId](text)
            del player.windowHandlers[windowId] # Cleanup
        except:
            pass
        
    @packet(0x8A)
    def handleWriteBackForHouses(self, player, packet):
        packet.pos += 1 # Skip doorId, no need in PyOT :)
        windowId = packet.uint32()
        text = packet.string()
        
        try: # Try blocks are better than x in y checks :)
            player.windowHandlers[windowId](text)
            del player.windowHandlers[windowId] # Cleanup
        except:
            pass
        
    @packet(0xF9)
    def handleDialog(self, player, packet):
        windowId = packet.uint32()
        button = packet.uint8()
        
        try:
            player.windowHandlers[windowId](button)
            del player.windowHandlers[windowId] # Cleanup
        except:
            pass
        
    @packet(0xF0)
    def handleOpenQuestLog(self, player, packet):
        player.questLog()

    @packet(0xF1)
    def handleQuestLine(self, player, packet):
        questId = packet.uint16()-1
        player.questLine(game.resource.getQuest(questId).name)
        
    @packet(0xDC)
    def handleAddVip(self, player, packet):
        player.addVipByName(packet.string())
        
    @packet(0xDD)
    def handleRemoveVip(self, player, packet):
        player.removeVip(packet.uint32())
        
    @packet(0x7D)
    def handleRequestTrade(self, player, packet):
        position = packet.position(player.position.instanceId)
        itemId = sid(packet.uint16())
        stackpos = packet.uint8()
        player2 = game.engine.getCreatureByCreatureId(packet.uint32())
        
        if not player.inRange(player2.position, 2, 2):
            player.message("You need to move closer.")
            return
            
        if position.x == 0xFFFF:
            thing = player.findItem(position, stackpos)
            if thing in player.tradeItems:
                player.message("Your already trading this item.")
                return
        else:
            return
        
        
        if player2.isTradingWith and player2.isTradingWith != player:
            player.message("This player is already trading.")
            return
        
        thing.inTrade = True
        
        # Modifing the current trade    
        if player.isTradingWith == player2:
            player.tradeItems.append(thing)
            # Close trade since we're refreshing it
            player2.closeTrade()
            player.closeTrade()
            
            if player.startedTrade:
                starter = player
                trader = player2
            else:
                starter = player2
                trader = player
                
            player2.tradeItemRequest(starter, starter.tradeItems, True)
            if player2.tradeItems:
                player2.tradeItemRequest(trader, trader.tradeItems, False)
                player.tradeItemRequest(trader, trader.tradeItems, True)
                player.tradeItemRequest(starter, starter.tradeItems, False)
            else:
                player.tradeItemRequest(starter, starter.tradeItems, True)

        else:
            player2.message("%s wish to trade with you." % player.name())
            
            player.tradeItems = [thing]
            
            player.tradeItemRequest(player, player.tradeItems, True)
            player2.tradeItemRequest(player, player.tradeItems, True)
            
            player.isTradingWith = player2
            player2.isTradingWith = player
            player.startedTrade = True
            player2.startedTrade = False
            
    @packet(0x80)
    def handleCloseTrade(self, player, packet, c=False):
        player.closeTrade()
        if player.isTradingWith:
            if not c:
                player.isTradingWith.message("Trade cancelled.")
                for item in player.isTradingWith.tradeItems:
                    del item.inTrade
                
            player.isTradingWith.tradeItems = []
            player.isTradingWith.isTradingWith = None
            player.isTradingWith.closeTrade()
            player.isTradingWith.tradeAccepted = False
            
            if not c:
                player.message("Trade cancelled.")
                for item in player.tradeItems:
                    del item.inTrade
                    
            player.tradeItems = []
            
            player.isTradingWith = None
            player.tradeAccepted = False
            
    @packet(0x7C)
    def handleCloseTradeNPC(self, player, packet):
        if player.openTrade:
            player.openTrade.farewell(player)
            player.closeTrade()

        
    @packet(0x7E)    
    def handleLookAtInTrade(self, player, packet):
        counter = packet.uint8()
        stackpos = packet.uint8()
        thing = None
        if counter:
            try:
                thing = player.isTradingWith.tradeItems[stackpos]
            except:
                pass
        else:
            try:
                thing = player.tradeItems[stackpos]
            except:
                pass
            
        if thing:
            def afterScript():
                extra = ""
                # TODO propper description handling
                if config.debugItems:
                    extra = "(ItemId: %d, Cid: %d)" % (thing.itemId, thing.cid)
                player.message(thing.description(player) + extra)
            game.scriptsystem.get('lookAtTrade').runSync(thing, player, afterScript, position=game.map.StackPosition(0xFFFE, counter, 0, stackpos))
        
    @packet(0x7F)    
    def handleAcceptTrade(self, player, packet):
        if player.isTradingWith.tradeAccepted:
            for item in player.isTradingWith.tradeItems:
                del item.inTrade
                if item.decayCreature and not item.inContainer:
                   item.decayCreature.inventory[item.decayCreature.inventory.index(item)] = None
                if item.decayCreature:
                    player.isTradingWith.removeCache(item)
                if item.inContainer:
                    item.inContainer.removeItem(item)
                    
                
            for item in player.tradeItems:
                del item.inTrade
                if item.decayCreature and not item.inContainer:
                    item.decayCreature.inventory[item.decayCreature.inventory.index(item)] = None
                if item.decayCreature:
                    player.isTradingWith.removeCache(item)
                if item.inContainer:
                    item.inContainer.removeItem(item)
                    
            for item in player.tradeItems:
                player.isTradingWith.addItem(item)
                
            for item in player.isTradingWith.tradeItems:
                player.addItem(item)
                
            player.message("Trade completed.")
            player.updateAllContainers()
            player.isTradingWith.message("Trade completed.")
            player.isTradingWith.updateAllContainers()
            self.handleCloseTrade(player, None, True)
            
        else:
            player.tradeAccepted = True
            player.isTradingWith.message("Offer accepted. Whats your take on this?")
        
    @packet(0x84)    
    @inlineCallbacks        
    def handleUseBattleWindow(self, player, packet):
        position = packet.position(player.position.instanceId)
        clientItemId = packet.uint16()
        stackpos = packet.uint8()
        creature = game.engine.getCreatureByCreatureId(packet.uint32())
        hotkey = position.x == 0xFFFF and not position.y
        stackPosition = position.setStackpos(stackpos)
        # Is hotkeys allowed?
        if not config.enableHotkey:
            player.cancelMessage("Hotkeys are disabled.")
            return
            
        # Are we in distance to object?
        if player != creature and not player.inRange(creature.position, 7, 5):
            player.cancelMessage("Target is too far away.")
            return 
        serverId = sid(clientItemId)
        if not hotkey:
            thing = player.findItem(stackPosition)
        else:
            thing = player.findItemById(serverId)
            
            if not thing:
                player.cancelMessage("You don't have any left of this item.")
                
                return
                
            # Also tell hotkey message
            count = player.inventoryCache[serverId][0]
            
            if not thing.showCount:
                player.message("Using one of %s..." % thing.rawName())
            elif count == 1:
                player.message("Using the last %s..." % thing.rawName())
            else:
                player.message("Using one of %d %s..." % (count, thing.rawName()))
        
        if not thing: return

        if not thing.position:
            thing.position = stackPosition

        if thing and (position.x == 0xFFFF or (position.z == player.position.z and player.canSee(position))):
            if not position.x == 0xFFFF and not player.inRange(position, 1, 1):
                walkPattern = game.engine.calculateWalkPattern(player, player.position, position, -1)

                # No walk pattern means impossible move.
                if not walkPattern:
                    player.notPossible()
                    return

                # Some half sync yield -> sleep walking
                def sleep(seconds):
                    d = Deferred()
                    reactor.callLater(seconds, d.callback, seconds)
                    return d
                    
                walking = [True]
                scount = 0
                player.walkPattern = deque(walkPattern)
                game.engine.autoWalkCreature(player, lambda: walking.pop())
                while walking and scount < 100:
                    yield sleep(0.1)
                    scount += 1
            
            if position.x == 0xFFFF or player.inRange(position, 1, 1):
                game.scriptsystem.get('useWith').runSync(thing, player, None, position=stackPosition, onThing=creature, onPosition=creature.position)

        
    @packet(0xA3)
    def handleInviteToParty(self, player, packet):
        creature = game.engine.getCreatureByCreatureId(packet.uint32())
        
        if creature.party():
            player.message("%s is already in a party." % creature.name())
            return
            
        # Grab the party
        party = player.party()
        if not party:
            # Make a party
            party = player.newParty()
        elif party.leader != player:
            return player.message("Your not the party leader!")
        
        party.addInvite(creature)
        
    @packet(0xA4)
    def handleJoinParty(self, player, packet):
        creature = game.engine.getCreatureByCreatureId(packet.uint32())

        # Grab the party
        party = creature.party()
        if not party or party.leader != creature:
            return
        
        party.addMember(player)
        
    @packet(0xA5)
    def handleRevokePartyInvite(self, player, packet):
        creature = game.engine.getCreatureByCreatureId(packet.uint32())
        myParty = player.party()
        
        if not myParty:
            player.message("You don't have a party!")
            return
        elif player is not myParty.leader:
            player.message("You are not the party leader!")
            return
        elif creature.party() != myParty:
            player.message("%s is not a member/invite of the party." % creature.name())
            return

        
        myParty.removeInvite(creature)        
        
    @packet(0xA6)
    def handlePassPartyLeadership(self, player, packet):
        creature = game.engine.getCreatureByCreatureId(packet.uint32())
        
        if creature.party() != player.party():
            player.message("%s is not in your party." % creature.name())
            return
            
        # Grab the party
        party = player.party()
        if not party or party.leader != player:
            return
        
        party.changeLeader(creature)
        
    @packet(0xA7)
    def handleLeaveParty(self, player, packet):
        player.leaveParty()

    @packet(0xA8)
    def handleShareExperience(self, player, packet):
        # Grab the party
        party = player.party()
        if not party or party.leader != player:
            return
        
        party.toggleShareExperience()
        
    @packet(0xE7)
    @inlineCallbacks
    def handleThanks(self, player, packet):
        messageId = packet.uint32()
        message = game.chat.getMessage(messageId)
        
        yield game.scriptsystem.get("thankYou").runDefer(player, messageId = messageId, author = message[0], channelType = message[3], channel = message[1], text = message[2])

    @packet(0xE8)
    def handleDebugAssert(self, player, packet):
        logger.writeEntry("debugs", '\n'.join([packet.string(), packet.string(), packet.string(), packet.string()]), player.name(), "IP:%s" % player.getIP() )
        
        
    @packet(0x1D)
    def handlePing(self, player, packet):
        with player.packet(0x1E) as stream:
            pass
    
    @packet(0xF4)
    def handleCloseMarket(self, player, packet):
        player.closeMarket()

    @packet(0xF5)
    def handleBrowseMarket(self, player, packet):
        if not player.market or not player.marketOpen: return

        id = packet.uint16()

        if id == 0xFFFE:
            print "Req own offers"
            player.marketOwnOffers()

        elif id == 0xFFFF:
            print "Req own history"
            player.marketHistory()

        else:
            player.marketOffers(id)

    @packet(0xF6)
    def handleCreateMarketOffer(self, player, packet):
        if not player.market or not player.marketOpen: return

        type = packet.uint8()
        id = packet.uint16()
        amount = packet.uint16()
        price = packet.uint32()
        anonymous = packet.uint8()

        if not id:
            return

        player.createMarketOffer(type, id, amount, price, anonymous)

    @packet(0xF7)
    def handleCancelOffer(self, player, packet):
        if not player.market or not player.marketOpen: return

        expire = packet.uint32()
        counter = packet.uint16()

        print expire, counter
        
        offer = player.market.findOffer(expire, counter)
        if offer:
            type = offer.type
            player.market.removeOffer(offer)
        player.marketOwnOffers()
        
    @packet(0xF8)
    def handleAcceptOffer(self, player, packet):
        if not player.market or not player.marketOpen: return

        expire = packet.uint32()
        counter = packet.uint16()
        amount = packet.uint16()

        offer = player.market.findOffer(expire, counter)
        if not offer:
            print "Offer not found"
            print expire, expire-config.marketOfferExpire, counter
            return
        if offer.amount < amount:
            print "Too much, reducing offer"
            player.marketOffers(offer.itemId)
            amount = offer.amount

        if not offer.type:
            player.marketOffers(offer.itemId)
            return

        if offer.type == MARKET_OFFER_BUY:
            offer.handleBuy(player, amount)

        else:
            offer.handleSell(player, amount)

        player.marketOffers(offer.itemId)
