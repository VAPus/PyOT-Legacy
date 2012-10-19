"""A collection of functions that almost every other component requires"""
import __builtin__
from twisted.internet import reactor, threads, defer
from twisted.internet.defer import inlineCallbacks, returnValue, Deferred
__builtin__.inlineCallbacks = inlineCallbacks
from collections import deque
from twisted.python import log
import time
import game.map
import config
import math
import sql
import otjson
import game.enum
import sys
import random
import game.vocation
import game.resource
import game.scriptsystem
import game.errors
import glob
import game.protocol
import core.logger
import game.chat
import re
import subprocess
import platform
import os
import game.deathlist
import game.ban

try:
    import cPickle as pickle
except:
    import pickle

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

# Some half important constants
IS_ONLINE = False
IS_RUNNING = True
globalStorage = {'storage':{}, 'objectStorage':{}}
saveGlobalStorage = False
jsonFields = 'storage',
pickleFields = 'objectStorage',
groups = {}
serverStart = time.time() - config.tibiaTimeOffset
globalize = ["magicEffect", "summonCreature", "relocate", "transformItem", "placeItem", "autoWalkCreature", "autoWalkCreatureTo", "getCreatures", "getPlayers", "getSpectators", "placeInDepot", "townNameToId", "getTibiaTime", "getLightLevel", "getPlayerIDByName", "positionInDirection", "updateTile", "saveAll", "teleportItem", "getPlayer", "townPosition", "broadcast", "loadPlayer", "loadPlayerById", "getHouseByPos", "moveItem"]

# Just a inner funny call
def looper(function, time):
    """Looper decorator"""
    
    function()
    reactor.callLater(time, looper, function, time)
    
# The action decorator :)
def action(forced=False, delay=0):
    """Action decorator.
    
    :param forced: Supress any other action.
    :type forced: bool.
    :param delay: Delay the start this action.
    :type delay: float (seconds).
    
    """
    
    def decor(f):
        def new_f(creature, *args, **argw):
            if creature.action and forced:
                try:
                    creature.action.cancel()
                except:
                    pass
                f(creature, *args, **argw)
            elif not forced and creature.action and creature.action.active():
                reactor.callLater(0.05, new_f, creature, *args, **argw)
            elif delay and creature.action:
                reactor.callLater(delay, f, creature, *args, **argw)
            else:
                f(creature, *args, **argw)

        return new_f
    return decor

def loopDecorator(time):
    """Loop function decorator.
    
    :param time: Run the function every ``time`` seconds.
    :type time: float (seconds).

    """
    
    def decor(f):
        def new_f(*args, **kwargs):
            if f(*args, **kwargs) != False:
                reactor.callLater(time, new_f, *args, **kwargs)
        
        def first(*args, **kwargs):
            reactor.callLater(0, new_f, *args, **kwargs)
            
        return first
    return decor
    
# First order of buisness, the autoWalker
@action(True)
def autoWalkCreature(creature, callback=None):
    """Autowalk the creature using the walk patterns. This binds the action slot.
    
    :param creature: The creature to autowalk of type :class:`game.creature.Creature` or any subclass of it.
    :type creature: :class:`game.creature.Creature`.
    :param walkPatterns: List of steps to take.
    :type walkPatterns: :class:`collections.deque`.
    :param callback: Call this function when the creature reach it's destination.
    :type callback: function.
    
    """
    
    try:
        creature.action = reactor.callLater(max(creature.lastAction - time.time(), 0), handleAutoWalking, creature, callback)
    except:
        # Just have to assume he goes down?
        """pos = positionInDirection(creature.position, creature.walkPattern[0], 2)
        pos[2] += 1
        creature.teleport(pos)"""
        pass
        
# This one calculate the tiles on the way
def autoWalkCreatureTo(creature, to, skipFields=0, diagonal=True, callback=None):
    """Autowalk the creature using the walk patterns. This binds the action slot.
    
    :param creature: The creature to autowalk of type :class:`game.creature.Creature` or any subclass of it.
    :type creature: :class:`game.creature.Creature`.
    
    :param to: Destination position.
    :type to: list or tuple.
    
    :param skipFields: Don't walk the last steps to the destination. Useful if you intend to walk close to a target.
    :type skipFields: int.
    
    :param diagonal: Allow diagonal walking?
    :type diagonal: bool.
    
    :param callback: Call this function when the creature reach it's destination.
    :type callback: function.
    
    """
    if creature.position.z != to.z:
        creature.message("Change floor")
        return
        
    pattern = calculateWalkPattern(creature, creature.position, to, skipFields, diagonal)
    
    if pattern:
        creature.walkPattern = deque(pattern)
        autoWalkCreature(creature, callback)
    elif callback:
        callback(None)

    
#@action()
def handleAutoWalking(creature, callback=None, level=0):
    if not creature.walkPattern:
        return
        
    direction = creature.walkPattern.popleft()

    mcallback=callback
    if creature.walkPattern:
        def mcallback():
            try:
                creature.action = reactor.callLater(max(creature.lastAction - time.time(), 0), handleAutoWalking, creature, callback)
            except IndexError:
                return

    creature.move(direction, level=level, stopIfLock=True, callback=mcallback)
    

# Calculate walk patterns
def calculateWalkPattern(creature, fromPos, to, skipFields=None, diagonal=True):
    """Calculate the route from ``fromPos`` to ``to``.
    
    :param fromPos: Start position.
    :type fromPos: list or tuple.
    
    :param to: Destination position.
    :type to: list or tuple.
    
    :param skipFields: Don't walk the last steps to the destination. Useful if you intend to walk close to a target.
    :type skipFields: int or None.
    
    :param diagonal: Allow diagonal walking?
    :type diagonal: bool.
    
    """
    pattern = []
    currPos = fromPos
    # First diagonal if possible
    if abs(fromPos.x - to.x) == 1 and abs(fromPos.y - to.y) == 1:
        if fromPos.y > to.y:
            base = 6
        else:
            base = 4
            
        if fromPos.x < to.x:
            base += 1
        newPos = positionInDirection(currPos, base)
        
        isOk = True
        for item in game.map.getTile(newPos).getItems():
            if item.solid:
                isOk = False
                break
                
        if isOk:
            currPos = newPos
            pattern.append(base)
        
    if not pattern:
        # Try a straight line
        pattern = pathfinder.findPath(creature, fromPos.z, fromPos.x, fromPos.y, to.x, to.y)
        if not pattern:
            return None
                
    # Fix for diagonal things like items
    """if len(pattern) > 2 and diagonal == True:
        last, last2 = pattern[len(pattern)-2:len(pattern)]
        if abs(last-last2) == 1:
            del pattern[len(pattern)-2:len(pattern)]
            if last == 0: # last = north, last2 must be east/west
                last = 6 + (0 if last2 == 3 else 1)
            elif last == 2: # last = south, last2 must be east/west
                last = 4 + (0 if last2 == 3 else 1)
                
            elif last == 1: # last = east, last2 must be 
                last = 1 + (6 if last2 == 0 else 4)
            elif last == 3: # last = west, last2 must be 
                last = 0 + (6 if last2 == 0 else 4)
            pattern.append(last)"""
    if skipFields != 0:
        pattern = pattern[:skipFields]
    return pattern

# Spectator list
def getSpectators(pos, radius=(8,6), ignore=()):
    """Gives you the spectators (:class:`service.gameserver.GameProtocol`) in the area.
    
    :param pos: Position of the center point.
    :type pos: list or tuple.
    :param radius: Radius from center point to check for players.
    :type radius: list or tuple.
    :param ignore: known spectators to ignore in the set.
    :type ignore: list, tuple or set.
    
    :rtype: set of :class:`service.gameserver.GameProtocol`
    
    """
    
    players = set()   
    for player in game.player.allPlayersObject:
        if player.canSee(pos, radius) and player.client and player.client.ready and player not in ignore:
            players.add(player.client)
        
    return players

def hasSpectators(pos, radius=(8,6), ignore=()):
    for player in game.player.allPlayersObject:
        if player.canSee(pos, radius) and player not in ignore: return True
        
    return False
    
def getCreatures(pos, radius=(8,6), ignore=()):
    """Gives you the creatures in the area.
    
    :param pos: Position of the center point.
    :type pos: list or tuple.
    :param radius: Radius from center point to check for creatures.
    :type radius: list or tuple.
    :param ignore: known creatures to ignore in the set.
    :type ignore: list, tuple or set.
    
    :rtype: set of :class:`game.creature.Creature` compatible objects
    
    """
    
    creatures = set()
                
    for creature in game.creature.allCreaturesObject:
        if creature.canSee(pos, radius) and creature not in ignore:
            creatures.add(creature)
    return creatures
        

def getPlayers(pos, radius=(8,6), ignore=()):
    """Gives you the players in the area.
    
    :param pos: Position of the center point.
    :type pos: list or tuple.
    :param radius: Radius from center point to check for players.
    :type radius: list or tuple.
    :param ignore: known players to ignore in the set.
    :type ignore: list, tuple or set.
    
    :rtype: set of :class:`game.player.Player` compatible objects
    
    """
    
    players = set()
              
    for player in game.player.allPlayersObject:
        if player.canSee(pos, radius) and player not in ignore:
            players.add(player)
    
    return players
        

# Calculate new position by direction
def positionInDirection(nposition, direction, amount=1):
    """Gives the position in a direction
    
    :param nposition: Current position.
    :type nposition: list.
    
    :param direction: The direction.
    :type direction: int (range 0-7).
    
    :param amount: Amount of steps in that direction.
    :type amount: int.
    
    :rtype: list.
    :returns: New position.
    
    """
    
    position = nposition.copy() # Important not to remove the : here, we don't want a reference!
    if direction == 0:
        position.y = nposition.y - amount
    elif direction == 1:
        position.x = nposition.x + amount
    elif direction == 2:
        position.y = nposition.y + amount
    elif direction == 3:
        position.x = nposition.x - amount
    elif direction == 4:
        position.y = nposition.y + amount
        position.x = nposition.x - amount
    elif direction == 5:
        position.y = nposition.y + amount
        position.x = nposition.x + amount
    elif direction == 6:
        position.y = nposition.y - amount
        position.x = nposition.x - amount
    elif direction == 7:
        position.y = nposition.y - amount
        position.x = nposition.x + amount
    return position
    
def updateTile(pos, tile):
    """ Send the update to a tile to all who can see the position.
    *Note that this function does NOT replace the known tile in :mod:`game.map`'s knownMap array.*
    
    :param pos: Position of tile.
    :type pos: list or tuple.
    :param tile: The tile that replace the currently known tile at the position.
    :type tile: Tile of type :class:`game.map.Tile`.
    
    """
    
    for spectator in getSpectators(pos):
        stream = spectator.packet(0x69)
        stream.position(pos)
        stream.tileDescription(tile, spectator.player)
        stream.uint8(0x00)
        stream.uint8(0xFF)
        stream.send(spectator)

def transformItem(item, transformTo):
    """ Transform item to a new Id.
    
    :param item: The item you want to transform.
    :type item: Object of type :class:`game.item.Item`.
    
    :param transformTo: New itemID. Leave to 0 or None to delete the item.
    :type transformTo: int or None.
    
    :param pos: Position of the item.
    :type pos: List of tuple.
    
    
    """
    """pos = item.vertifyPosition()
    if not pos:
        raise Exception("BUG: Can't vertify position")
 
    tile = game.map.getTile(pos)
    if not isinstance(pos, StackPosition):
        pos = pos.setStackpos(tile.findStackpos(item))

    tile.removeItem(item)
    if item.tileStacked:
        item = item.copy()
        
    item.itemId = transformTo
    if transformTo:
        newStackpos = tile.placeItem(item)

    for spectator in getSpectators(pos):
        stream = spectator.packet()
        stream.removeTileItem(pos, pos.stackpos)
        if transformTo:
            stream.addTileItem(pos, newStackpos, item)
            
        stream.send(spectator)"""

    return item.transform(transformTo)

def teleportItem(item, fromPos, toPos):
    """ "teleport" a item from ``fromPos`` to ``toPos``
    
    :param item: The item you want to transform.
    :type item: :class:`game.item.Item`
    
    :param fromPos: From this position
    :type fromPos: :func:`tuple` or :func:`list`
    
    :param toPos: To this position
    :type toPos: :func:`tuple` or :func:`list`
    
    
    :rtype: :func:`int`
    :returns: New stack position
    
    
    """
    if fromPos.x != 0xFFFF:
        try:
            tile = fromPos.getTile()
            if not isinstance(fromPos, StackPosition):
                fromPos = fromPos.setStackpos(tile.findStackpos(item))
                
            tile.removeItem(item)
            for spectator in getSpectators(fromPos):
                stream = spectator.packet()
                stream.removeTileItem(fromPos, fromPos.stackpos)
                stream.send(spectator)
        except:
            pass
              
    newTile = toPos.getTile()
    if item.decayPosition:
            item.decayPosition = toPos
    toStackPos = newTile.placeItem(item)
        
    for spectator in getSpectators(toPos):
        stream = spectator.packet()
        stream.addTileItem(toPos, toStackPos, item)
        stream.send(spectator)
        
    return toStackPos
        
def placeItem(item, position):
    """ Place a item to a position
    
    :param item: The item to place.
    :type item: Object of type :class:`game.item.Item`.
    
    :param position: The position to place the item on.
    :type position: list or tuple.
    
    :rtype: int.
    :returns: Stack position of item.
    
    """
    
    stackpos = position.getTile().placeItem(item)
    for spectator in getSpectators(position):
        stream = spectator.packet()
        stream.addTileItem(position, stackpos, item)
        stream.send(spectator)
    return stackpos

def relocate(fromPos, toPos):
    tile = fromPos.getTile()
    toPos = toPos.getTile()
    items = []
    for item in tile.getItems():
        if not item.movable: continue
        
        if item.decayPosition:
            item.decayPosition = toPos
            
        stackpos = toPos.placeItem(item)
        items.append((item, tile.getSlot(item), stackpos))
        
    for item in items:    
        tile.removeItem(item)
        
    for spectator in getSpectators(fromPos):
        stream = spectator.packet()
        for pair in items:
            stream.removeTileItem(fromPos, pair[1])
        stream.send(spectator)

    for spectator in getSpectators(toPos):
        stream = spectator.packet()
        for pair in items:
            stream.addTileItem(toPos, pair[2], pair[0])
        stream.send(spectator)
# The development debug system
def explainPacket(packet):
    """ Explains the packet structure in hex
    
    :param packet: Packet to explain.
    :type packet: subclass of :class:`core.packet.TibiaPacket`.
    
    """
    
    #currPos = packet.pos
    #packet.pos = 0
    log.msg("Explaining packet (type = {0}, length: {1}, content = {2})".format(hex(ord(packet.data[0])), len(packet.data), ' '.join( map(str, map(hex, map(ord, packet.data)))) ))
    #packet.pos = currPos

# Save system, async :)
def saveAll(force=False):
    commited = False
    
    t = time.time()
    for player in game.player.allPlayers.values():
        result = player._saveQuery(force)
        if result:
            sql.runOperation(*result)
            commited = True

    # Global storage
    if saveGlobalStorage or force:
        for field in globalStorage:
            type = ""
            if field in jsonFields:
                data = otjson.dumps(globalStorage[field])
                type = "json"
            elif field in pickleFields:
                data = fastPickler(globalStorage[field])
                type = "pickle"
            else:
                data = globalStorage[field]
                
            sql.runOperation("INSERT INTO `globals` (`key`, `data`, `type`) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE `data` = %s", (field, data, type, data))
            commited = True
            
    # Houses
    if game.map.houseTiles:
        for houseId, house in game.house.houseData.items():
            # House is loaded?
            if houseId in game.map.houseTiles:
                try:
                    items = house.data["items"].copy()
                except:
                    log.msg("House id %d have broken items!" % houseId)
                    items = {} # Broken items
                    
                for tile in game.map.houseTiles[houseId]:
                    _items = []
                    for item in tile.bottomItems():
                        ic = item.count
                        if not item.fromMap and (ic == None or ic > 0):
                            _items.append(item)
                    items[tile.position] = _items

                if items != house.data["items"]  or force:
                    house.data["items"] = items
                    house.save = True # Force save
                if house.save:
                    log.msg("Saving house ", houseId)
                    sql.runOperation("UPDATE `houses` SET `owner` = %s,`guild` = %s,`paid` = %s, `data` = %s WHERE `id` = %s", (house.owner, house.guild, house.paid, fastPickler(house.data), houseId))
                    house.save = False
                    commited = True
                else:
                    log.msg("Not saving house", houseId)
        
    if force:        
        log.msg("Full (forced) save took: %f" % (time.time() - t))

    elif commited:       
        log.msg("Full save took: %f" % (time.time() - t))
        
# Time stuff
def getTibiaTime():
    """ Return the Time inside the game.
    
    :rtype: tuple (hours, minutes, seconds).
    """
    
    seconds = ((time.time() - serverStart) % config.tibiaDayLength) * ((24*60*60) / config.tibiaDayLength)
    hours = int(float(seconds / 3600))
    seconds = seconds - (hours * 3600)
    minutes = int(seconds / 60)
    seconds = seconds % 60
    
    return (hours, minutes, seconds)
    
def getLightLevel():
    """ Get the light level relevant to the time of the day.
    
    :rtype: int.
    """
    
    tibiaTime = getTibiaTime()
    light = 0
    if tibiaTime[0] >= config.tibiaDayFullLightStart and tibiaTime[0] < config.tibiaDayFullLightEnds:
        return config.tibiaFullDayLight
    else:
        dayHours = 24 - (config.tibiaDayFullLightEnds - config.tibiaDayFullLightStart)
        hoursleft = (abs(24 - tibiaTime[0]) + config.tibiaDayFullLightStart) % 24

        if hoursleft >= 12:
            lightChange = ((config.tibiaFullDayLight - config.tibiaNightLight) / dayHours) * (hoursleft-12)
            return config.tibiaNightLight + lightChange            
        else:
            lightChange = ((config.tibiaFullDayLight - config.tibiaNightLight) / dayHours) * (hoursleft)
            return config.tibiaFullDayLight - lightChange
        
LIGHT_LEVEL = getLightLevel()

def checkLightLevel():
    """ Check if the lightlevel have changed and send updates to the players.
    
    """
    global LIGHT_LEVEL
    light = getLightLevel()
    if LIGHT_LEVEL != light:
        for c in game.player.allPlayersObject:
            if not c.client: continue
            with c.packet() as stream:
                stream.worldlight(light, LIGHTCOLOR_DEFAULT)

        LIGHT_LEVEL = light
        
# Player lookup and mail
# Usually blocking calls, but we're only called from scripts so i suppose it's ok
@inlineCallbacks
def getPlayerIDByName(name):
    """ Returns the playerID based on the name.
    
    :rtype: int or None.
    
    """
    
    try:
        returnValue(game.player.allPlayers[name].data["id"])
    except:
        d = yield sql.conn.runQuery("SELECT `id` FROM `players` WHERE `name` = %s", (name))
        if d:
            returnValue(d[0]['id'])
        else:
            returnValue(None)

def getPlayer(playerName):
    try:
        return game.player.allPlayers[playerName]
    except:
        return None

def getCreatureByCreatureId(cid):
    for creature in game.creature.allCreaturesObject:
        if creature.cid == cid:
            return creature
            
def townNameToId(name):
    """ Return the townID based on town name.
    
    :rtype: int or None.
    
    """
    
    import data.map.info as i
    for id in i.towns:
        if i.towns[id][0] == name:
            return id

def townPosition(id):
    """ Returns the position of a town passed by id
    
    :rtype: list
    
    """
    import data.map.info as i
    return i.towns[id][1]

def broadcast(message, type='MSG_GAMEMASTER_BROADCAST', sendfrom="SYSTEM", level=0):
    """ Broadcasts a message to every player
    
    """
    for player in game.player.allPlayersObject:
        stream = player.packet(0xAA)
        
        # Make sure this player actually is online. TODO: Track them in a seperate list?
        if not stream: continue
        
        stream.uint32(0)
        stream.string(senfrom)
        stream.uint16(level)
        stream.uint8(stream.enum(messageType))
        stream.string(message)
        stream.send(player.client)
        
@inlineCallbacks
def placeInDepot(name, depotId, items):
    """ Place items into the depotId of player with a name. This can be used even if the player is offline.
    
    :param name: Player name.
    :type name: str.
    
    :param depotId: DepotID to place items into.
    :type depotId: int or str.
    
    :param items: Either one Item or a list of items to place into the depot.
    :type items: Either one object of type :class:`game.item.Item`, or a list of objects.
    
    :rtype: bool.
    :returns: True on success, False otherwise.
    
    """
    if not type(items) == list:
        items = [items]
        
    def __inPlace(place):
        for i in items:
            place.append(i)
            
    if name in game.player.allPlayers:
        try:
            __inPlace(game.player.allPlayers[name].depot[depotId])
        except:
            game.player.allPlayers[name].depot[depotId] = items
        returnValue(True)
    else:
        result = yield sql.conn.runQuery("SELECT `depot` FROM `players` WHERE `name` = %s", (name))
        if result:
            result = pickle.loads(result[0]['depot'])
            try:
                __inPlace(result[depotId])
            except:
                result[depotId] = items
            result = fastPickler(result)
            sql.conn.runOperation("UPDATE `players` SET `depot` = %s", result)
            returnValue(True)
        else:
            returnValue(False)
            
@inlineCallbacks
def loadPlayer(playerName):
    try:
        # Quick load :p
        returnValue(game.player.allPlayers[playerName])
    except KeyError:
        character = yield sql.conn.runQuery("SELECT p.`id`,p.`name`,p.`world_id`,p.`group_id`,p.`account_id`,p.`vocation`,p.`health`,p.`mana`,p.`soul`,p.`manaspent`,p.`experience`,p.`posx`,p.`posy`,p.`posz`,p.`instanceId`,p.`sex`,p.`looktype`,p.`lookhead`,p.`lookbody`,p.`looklegs`,p.`lookfeet`,p.`lookaddons`,p.`lookmount`,p.`town_id`,p.`skull`,p.`stamina`, p.`storage`, p.`inventory`, p.`depot`, p.`conditions`, s.`fist`,s.`fist_tries`,s.`sword`,s.`sword_tries`,s.`club`,s.`club_tries`,s.`axe`,s.`axe_tries`,s.`distance`,s.`distance_tries`,s.`shield`,s.`shield_tries`,s.`fishing`, s.`fishing_tries`, (SELECT a.`language` FROM account AS `a` WHERE a.`id` = p.`account_id`) as `language`, g.`guild_id`, g.`guild_rank`, p.`balance` FROM `players` AS `p` LEFT JOIN player_skills AS `s` ON p.`id` = s.`player_id` LEFT JOIN player_guild AS `g` ON p.`id` = g.`player_id` WHERE p.`name` = %s AND p.`world_id` = %s", (playerName, config.worldId))
        if not character:
            returnValue(None)
            return
        cd = character[0]
        deathlist.loadDeathList(cd['id'])
        game.player.allPlayers[playerName] = game.player.Player(None, cd)
        returnValue(game.player.allPlayers[playerName])
        
@inlineCallbacks
def loadPlayerById(playerId):
    try:
        # Quick look
        for player in game.player.allPlayersObject:
            if player.data["id"] == playerId:
                returnValue(player)
                return
    except:
        character = yield sql.conn.runQuery("SELECT p.`id`,p.`name`,p.`world_id`,p.`group_id`,p.`account_id`,p.`vocation`,p.`health`,p.`mana`,p.`soul`,p.`manaspent`,p.`experience`,p.`posx`,p.`posy`,p.`posz`,p.`instanceId`,p.`sex`,p.`looktype`,p.`lookhead`,p.`lookbody`,p.`looklegs`,p.`lookfeet`,p.`lookaddons`,p.`lookmount`,p.`town_id`,p.`skull`,p.`stamina`, p.`storage`, p.`inventory`, p.`depot`, p.`conditions`, s.`fist`,s.`fist_tries`,s.`sword`,s.`sword_tries`,s.`club`,s.`club_tries`,s.`axe`,s.`axe_tries`,s.`distance`,s.`distance_tries`,s.`shield`,s.`shield_tries`,s.`fishing`, s.`fishing_tries`, (SELECT a.`language` FROM account AS `a` WHERE a.`id` = p.`account_id`) as `language`, g.`guild_id`, g.`guild_rank`, p.`balance` FROM `players` AS `p` LEFT JOIN player_skills AS `s` ON p.`id` = s.`player_id` LEFT JOIN player_guild AS `g` ON p.`id` = g.`player_id` WHERE p.`id` = %s, p.`world_id` = %s", (playerId, config.worldId))
        if not character:
            returnValue(None)
            return
        cd = character[0]
        deathlist.loadDeathList(cd['id'])
        game.player.allPlayers[cd['name']] = game.player.Player(None, cd)
        returnValue(game.player.allPlayers[cd['name']])

def moveItem(player, fromPosition, toPosition, count=0):
    if fromPosition == toPosition:
        return True
        
    # TODO, script events.
    
    # Analyse a little.
    fromMap = False
    toMap = False

    if fromPosition.x != 0xFFFF:
        # From map
        fromMap = True

    if toPosition.x != 0xFFFF:
        toMap = True
        
    oldItem = None
    renew = False
    stack = True
        
    thing = player.findItem(fromPosition)
    destItem = None
    if toPosition.x == 0xFFFF or isinstance(toPosition, StackPosition):
        destItem = player.findItem(toPosition)
    if not thing:
        return False
    
    # Some vertifications.
    if thing.stackable and count and count > thing.count:
        player.notPossible()
        return False
    
    elif not thing.movable or (toPosition.x == 0xFFFF and not thing.pickable):
        player.notPickable()
        return False
                    
    elif thing.openIndex != None and thing.openIndex == toPosition.y-64: # Moving into self
        player.notPossible()
        return False
    
    if destItem and destItem.inContainer: # Recursive check.
        container = destItem.inContainer
            
        while container:
            if container == thing:
                return player.notPossible()
            container = container.inContainer
            
    slots = thing.slots()
    
    # Can it be placed there?
    if toPosition.x == 0xFFFF and toPosition.y < 64 and (toPosition.y-1) not in (SLOT_PURSE, SLOT_BACKPACK):
        if (toPosition.y-1) not in slots:
            if not config.ammoSlotOnlyForAmmo and (toPosition.y-1) == SLOT_AMMO:
                pass
            else:
                player.notPossible()
                return False
        
    if player.freeCapasity() - ((thing.weight or 0) * (thing.count or 1)) < 0:
        player.tooHeavy()
        return False
    
    if fromPosition.x == 0xFFFF and fromPosition.y < 64 and game.scriptsystem.get("unequip").runSync(player, player.inventory[fromPosition.y-1], slot = (fromPosition.y-1)) == False:
        return False
    elif toPosition.x == 0xFFFF and toPosition.y < 64 and game.scriptsystem.get("equip").runSync(player, thing, slot = (toPosition.y-1)) == False:
        return False
    
    # Special case when both items are the same and stackable.
    if destItem and destItem.itemId == thing.itemId and destItem.stackable:
        _newItem = game.scriptsystem.get("stack", thing, position=fromPosition, onThing=destItem, onPosition=toPosition, count=count, end=False)
        if not newItem:
            newCount = min(100, destItem.count + count) - destItem.count
            player.modifyItem(destItem, newCount)
            player.modifyItem(thing, -count)
            return True
        else:
            newItem = _newItem
        
    # remove from fromPosition.
    elif count and thing.stackable:
        newItem = thing.copy()
        newItem.count = count
        
        player.modifyItem(thing, -count)
        
    else:
        newItem = thing # Easy enough.
        
    if destItem and destItem.containerSize:
        if game.scriptsystem.get('useWith').runSync(newItem, player, position=fromPosition, onPosition=toPosition, onThing=destItem) == False:
            return False
        if game.scriptsystem.get('useWith').runSync(destItem, player, position=toPosition, onPosition=fromPosition, onThing=newItem) == False:
            return False
        
        if not thing.stackable:
            player.removeItem(thing)
            
        player.itemToContainer(destItem, newItem)
    else:    
        if not thing.stackable:
            player.removeItem(thing)
    
    if toMap:
        # Place to ground.
        thisTile = toPosition.getTile()
        
        for item in thisTile.getItems():
            if game.scriptsystem.get('useWith').runSync(newItem, player, position=fromPosition, onPosition=toPosition, onThing=item) == False:
                return False
            if game.scriptsystem.get('useWith').runSync(item, player, position=toPosition, onPosition=fromPosition, onThing=newItem) == False:
                return False
            
        newItem.place(toPosition)
    else:
        if not destItem or not destItem.containerSize:
            if toPosition.y < 64:
                # Inventory.
                player.itemToInventory(newItem, toPosition.y-1)
                
            else:
                container = player.getContainer(toPosition.y-64)
                
                if game.scriptsystem.get('useWith').runSync(newItem, player, position=fromPosition, onPosition=toPosition, onThing=container) == False:
                    return False
                if game.scriptsystem.get('useWith').runSync(container, player, position=toPosition, onPosition=fromPosition, onThing=newItem) == False:
                    return False
                
                player.itemToContainer(container, newItem)
    
        else:
            # Move destItem.
            if thing.inContainer:
                player.itemToContainer(thing.inContainer, destItem)
            else:
                player.itemToContainer(player.inventory[SLOT_BACKPACK], destItem)
        
    # Update everything. Lazy.
    player.refreshInventory()
    player.updateAllContainers()
    player.refreshStatus()
    
    # Done.
    return True
    
# Helper calls
def summonCreature(name, position, master=None):
    import game.monster
    creature = game.monster.getMonster(name).spawn(position, spawnDelay=0)
    if master:
        creature.setMaster(master)
    else:
        creature.setRespawn(False)
    return creature
    
def magicEffect(pos, type):
    for spectator in getSpectators(pos):
        stream = spectator.packet()
        stream.magicEffect(pos, type)
        stream.send(spectator)

def getHouseByPos(pos):
    return game.house.getHouseById(game.map.getHouseId(pos))

# Speed pickler
def fastPickler(obj):
    return pickle.dumps(obj, 2)
    
# Protocol 0x00:
class ReturnValueExit(Exception):
    def __init__(self, value=""):
        self.value = value
        
def Return(ret):
    raise ReturnValueExit(ret)
     
@inlineCallbacks
def executeCode(code):
    try:
        if "yield " in code:
            newcode = []
            for p in code.split("\n"):
                newcode.append("    " + p)
                
                
            exec("""
@inlineCallbacks
def _N():
%s
""" % '\n'.join(newcode))
            returnValue(otjson.dumps((yield _N())))
        else:
            exec(code)
    except ReturnValueExit, e:
        e = e.value
    else:
        yield defer.maybeDeferred()
    returnValue(otjson.dumps(e))
