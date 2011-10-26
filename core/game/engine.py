"""A collection of functions that almost every other component requires"""

from twisted.internet import reactor, threads, defer
from twisted.internet.defer import inlineCallbacks, returnValue, Deferred
from collections import deque
from twisted.python import log
import time
import game.map
import config
import math
import game.pathfinder
import bindconstant
import sql
import otjson
import game.enum
import sys
import random
import game.vocation
import game.resource
import game.scriptsystem
import glob
import game.protocol
import __builtin__
import re

try:
    import cPickle as pickle
except:
    import pickle
    
serverStart = time.time() - config.tibiaTimeOffset
globalStorage = {'storage':{}, 'objectStorage':{}}
saveGlobalStorage = False
jsonFields = 'storage',
pickleFields = 'objectStorage',
savedItems = {}
houseData = {}
groups = {}
globalize = ["magicEffect", "summonCreature", "relocate", "transformItem", "placeItem", "autoWalkCreature", "autoWalkCreatureTo", "getCreatures", "getPlayers", "placeInDepot", "townNameToId", "getTibiaTime", "getLightLevel", "getPlayerIDByName", "positionInDirection", "updateTile", "saveAll", "teleportItem", "getPlayer", "townPosition", "broadcast", "getHouseById", "loadPlayer", "loadPlayerById", "getHouseByPos"]

class House(object):
    def __init__(self, id, owner, guild, paid, name, town, size, rent, data):
        self.id = id
        self.owner = owner
        self.guild = guild
        self.paid = paid
        self.name = name
        self.town = town
        self.rent = rent
        self.size = size
        if data:
            self.data = pickle.loads(data)
        else:
            self.data = {"items":[], "subowners": [], "guests": [], "doors":{}}
        try:
            for pos in self.data["items"]:
                savedItems[pos] = self.data["items"][pos]
        except:
            pass
        self.save = False

    # Doors
    def getDoorAccess(self, doorId):
        try:
            return self.data["doors"][doorId]
        except:
            self.data["doors"][doorId] = []
            return self.data["doors"][doorId]
            
    def addDoorAccess(self, doorId, name):
        self.save = True
        
        try:
            self.data["doors"][doorId].append(name)
        except:
            self.data["doors"][doorId] = [name]
            
    def removeDoorAccess(self, doorId, name):
        self.save = True
        try:
            self.data["doors"][doorId].remove(name)
        except:
            pass
    def haveDoorAccess(self, doorId, nameOrPlayer):
        # TODO: guild!
        import game.player
        
        try:
            if isinstance(nameOrPlayer, game.player.Player):
                check = nameOrPlayer.name()
                 
            else:
                check = nameOrPlayer
            
            for e in self.data["doors"][doorId]:
                try:
                    isnot = False
                    if e[0] == "!":
                        isnot = True
                    if "@" in e:
                        # No guild support yet
                        continue
                    if "#" in e:
                        continue # Comment
                        
                    if re.match(e, nameOrPlayer, re.I):
                        if isnot: continue
                        else: return True
                    else:
                        if isnot: return True
                        else: continue
                except:
                    continue
        except:
            pass
        return False
            
    # Guests
    def addGuest(self, name):
        self.save = True
        try:
            self.data["guests"].append(name)
        except:
            self.data["guests"] = [name]
    def removeGuest(self, name):
        self.save = True
        try:
            self.data["guests"].remove(name)
        except:
            pass
    def isGuest(self, nameOrPlayer):
        # TODO: guild!
        import game.player
        
        try:
            if isinstance(nameOrPlayer, game.player.Player):
                check = nameOrPlayer.name()
                 
            else:
                check = nameOrPlayer
            
            for e in self.data["guests"]:
                try:
                    isnot = False
                    if e[0] == "!":
                        isnot = True
                    if "@" in e:
                        # No guild support yet
                        continue
                    if "#" in e:
                        continue # Comment
                        
                    if re.match(e, nameOrPlayer, re.I):
                        if isnot: continue
                        else: return True
                    else:
                        if isnot: return True
                        else: continue
                except: # Malformed regex, such as name**
                    continue
        except:
            pass
        return False
            
    # Subowners
    def addSubOwner(self, name):
        self.save = True
        try:
            self.data["subowners"].append(name)
        except:
            self.data["subowners"] = [name]
    def removeSubOwner(self, name):
        self.save = True
        try:
            self.data["subowners"].remove(name)
        except:
            pass
    def isSubOwner(self, nameOrPlayer):
        # TODO: guild!
        import game.player
        
        try:
            if isinstance(nameOrPlayer, game.player.Player):
                check = nameOrPlayer.name()
                 
            else:
                check = nameOrPlayer
            
            for e in self.data["subowners"]:
                try:
                    isnot = False
                    if e[0] == "!":
                        isnot = True
                    if "@" in e:
                        # No guild support yet
                        continue
                    if "#" in e:
                        continue # Comment
                        
                    if re.match(e, nameOrPlayer, re.I):
                        if isnot: continue
                        else: return True
                    else:
                        if isnot: return True
                        else: continue
                except:
                    continue
        except:
            pass
        
        return False

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name != "save":
            object.__setattr__(self, "save", True)
        
# The loader rutines, async loading :)
def loader(timer):
    log.msg("Begin loading...")
    import game.item

    # Begin loading items in the background
    d = game.item.loadItems()

    @inlineCallbacks
    def _sql_():
        for x in (yield sql.conn.runQuery("SELECT `key`, `data`, `type` FROM `globals`")):
            if x['type'] == 'json':
                globalStorage[x['key']] = otjson.loads(x['data'])
            elif x['type'] == 'pickle':
                globalStorage[x['key']] = pickle.loads(x['data'])
            else:
                globalStorage[x['key']] = x['data']

        for x in (yield sql.conn.runQuery("SELECT `id`,`owner`,`guild`,`paid`,`name`,`town`,`size`,`rent`,`data` FROM `houses`")):
            houseData[x["id"]] = House(x["id"], x["owner"],x["guild"],x["paid"],x["name"],x["town"],x["size"],x["rent"],x["data"])
            
        for x in (yield sql.conn.runQuery("SELECT `group_id`, `group_name`, `group_flags` FROM `groups`")):
            groups[x["group_id"]] = (x["group_name"], otjson.loads(x["group_flags"]))
    _sql_()            
    def sync(d, timer):
        # Load map (if configurated to do so)
        if config.loadEntierMap:
            begin = time.time()
            files = glob.glob('data/map/*.sec')
            for fileSec in files:
                x, y, junk = fileSec.split('/')[-1].split('.')
                game.map.load(int(x),int(y))
            log.msg("Loaded entier map in %f" % (time.time() - begin))
            
        # Load scripts
        game.scriptsystem.importer()
        game.scriptsystem.get("startup").run()
        
        # Charge rent?
        def _charge(house):
            callLater(config.chargeRentEvery, looper, lambda: game.scriptsystem.get("chargeRent").run(house))
            
        for house in houseData.values():
            if not house.rent or not house.owner: continue
            
            if house.paid < (timer - config.chargeRentEvery):
                game.scriptsystem.get("chargeRent").run(house)
                _charge(house)
            else:
                callLater((timer - house.paid) % config.chargeRentEvery, _charge, house)
                
        log.msg("Loading complete in %fs, everything is ready to roll" % (time.time() - timer))
        
        
         
    # Globalize certain things
    import game.player, game.creature, game.npc, game.monster, game.spell
    __builtin__.enum = game.enum
    for i in dir(game.enum):
        if not "__" in i:
            setattr(__builtin__, i, getattr(game.enum, i))
    for i in globalize:
        setattr(__builtin__, i, getattr(sys.modules["game.engine"], i))
        
    __builtin__.sql = sql.conn
    __builtin__.config = config
    __builtin__.reg = game.scriptsystem.reg
    __builtin__.regFirst = game.scriptsystem.regFirst
    __builtin__.defer = defer
    __builtin__.reactor = reactor
    __builtin__.engine = sys.modules["game.engine"]
    __builtin__.sys = sys
    __builtin__.math = math
    __builtin__.inlineCallbacks = inlineCallbacks
    __builtin__.returnValue = returnValue
    __builtin__.Deferred = Deferred
    __builtin__.deque = deque
    __builtin__.random = random
    __builtin__.time = time
    __builtin__.re = re
    __builtin__.spell = game.spell # Simplefy spell making
    __builtin__.callLater = safeCallLater
    __builtin__.Item = game.item.Item
    __builtin__.getTile = game.map.getTile
    __builtin__.Condition = game.creature.Condition
    __builtin__.itemAttribute = game.item.attribute
    __builtin__.getHouseId = game.map.getHouseId
    
    class Globalizer(object):
        __slots__ = ('monster', 'npc', 'creature', 'player', 'map', 'item', 'scriptsystem', 'spell', 'resource', 'vocation', 'enum')
        monster = game.monster
        npc = game.npc
        creature = game.creature
        player = game.player
        map = game.map
        item = game.item
        scriptsystem = game.scriptsystem
        spell = game.spell
        resource = game.resource
        vocation = game.vocation
        enum = game.enum
            
    __builtin__.game = Globalizer
    
    d.addCallback(sync, timer)
    
    # Load protocols
    for version in config.supportProtocols:
        game.protocol.loadProtocol(version)

    # Do we issue saves?
    if config.doSaveAll:
        reactor.callLater(config.saveEvery, looper, saveAll, config.saveEvery)
    
    # Do we save on shutdowns?
    if config.saveOnShutdown:
        game.scriptsystem.reg("shutdown", lambda **k: saveAll(True), False)
        
    # Light stuff
    lightchecks = config.tibiaDayLength / float(config.tibiaFullDayLight - config.tibiaNightLight)
    reactor.callLater(lightchecks, looper, checkLightLevel, lightchecks)
    
# Useful for windows
def safeTime():
    """Gives the time rounded so it can be divided by 60. This gives the same time on both unix systems and Windows.
    
    :rtype: float time.
    :returns: Time rounded so it can be divided by 60.
    
    """
    return math.ceil(time.time() * 60) / 60

def safeCallLater(sec, *argc, **kwargs):
    """This is a thread safe and time safe call for reactor.callLater. Passes args to callLater.
    
    :param sec: The number of seconds to delay the calls.
    :type sec: float.
    
    """
    reactor.callFromThread(reactor.callLater, math.ceil(sec * 60) / 60, *argc, **kwargs) # Closest step to the accurecy of windows clock

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
                creature.action.cancel()
                f(creature, *args, **argw)
            elif not forced and creature.action and creature.action.active():
                safeCallLater(0.05, new_f, creature, *args, **argw)
            elif delay and creature.action:
                safeCallLater(delay, f, creature, *args, **argw)
            else:
                f(creature, *args, **argw)

        return new_f
    return decor

def loopInThread(time):
    """Loop function in a thread decorator.
    
    :param time: Run the function every ``time`` seconds.
    :type time: float (seconds).

    """
    
    def decor(f):
        def new_f(*args, **kwargs):
            ret = f(*args, **kwargs)
            if ret != False:
                safeCallLater(time, reactor.callInThread, new_f, *args, **kwargs)
        
        def first(*args, **kwargs):
            safeCallLater(0, reactor.callInThread, new_f, *args, **kwargs)
            
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
        creature.action = safeCallLater(creature.stepDuration(game.map.getTile(creature.positionInDirection(creature.walkPattern[0])).getThing(0)), handleAutoWalking, creature, callback)
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
    if creature.position[2] != to[2]:
        creature.message("Change floor")
        return
        
    pattern = calculateWalkPattern(creature.position, to, skipFields, diagonal)
    
    if pattern:
        creature.walkPattern = deque(pattern)
        autoWalkCreature(creature, callback)
    elif callback:
        callback(None)
        
@action()
def handleAutoWalking(creature, callback=None, level=0):
    if not creature.walkPattern:
        return
        
    direction = creature.walkPattern.popleft()
    currPos = creature.position[:]
    mcallback=callback
    if creature.walkPattern:
        def mcallback(ret):
            creature2, oldPos, newPos = ret
            if oldPos == currPos:
                creature.action = safeCallLater(creature2.stepDuration(game.map.getTile(positionInDirection(newPos, creature2.walkPattern[0])).getThing(0)), handleAutoWalking, creature2, callback)
    
    d = Deferred()
    if mcallback:
        d.addCallback(mcallback)
    creature._move(d, direction, level=level, stopIfLock=True)
    
    

# Calculate walk patterns
def calculateWalkPattern(fromPos, to, skipFields=None, diagonal=True):
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
    if abs(fromPos[0] - to[0]) == 1 and abs(fromPos[1] - to[1]) == 1:
        if fromPos[1] > to[1]:
            base = 6
        else:
            base = 4
            
        if fromPos[0] < to[0]:
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
        pattern = game.pathfinder.findPath(fromPos[2], fromPos[0], fromPos[1], to[0], to[1])
                
    # Fix for diagonal things like items
    if len(pattern) > 2 and diagonal == True:
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
            pattern.append(last)
    if pattern and skipFields != 0:
        pattern = pattern[:skipFields]
        
    return pattern

# Spectator list
def getSpectators(pos, radius=(8,6), ignore=tuple()):
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
    try:       
        for player in game.player.allPlayersObject:
            if player.canSee(pos, radius) and player.client and player not in ignore:
                players.add(player.client)
    except:
        pass # No players
        
    return players
        
getSpectators = bindconstant._make_constants(getSpectators)

    
def getCreatures(pos, radius=(8,6), ignore=tuple()):
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
        
getCreatures = bindconstant._make_constants(getCreatures)

def getPlayers(pos, radius=(8,6), ignore=tuple()):
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
    
    try:            
        for player in game.player.allPlayersObject:
            if player.canSee(pos, radius) and player not in ignore:
                players.add(player)
    except:
        pass # No players
    
    return players
        
getPlayers = bindconstant._make_constants(getPlayers)

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
    
    position = list(nposition[:]) # Important not to remove the : here, we don't want a reference!
    if direction == 0:
        position[1] = nposition[1] - amount
    elif direction == 1:
        position[0] = nposition[0] + amount
    elif direction == 2:
        position[1] = nposition[1] + amount
    elif direction == 3:
        position[0] = nposition[0] - amount
    elif direction == 4:
        position[1] = nposition[1] + amount
        position[0] = nposition[0] - amount
    elif direction == 5:
        position[1] = nposition[1] + amount
        position[0] = nposition[0] + amount
    elif direction == 6:
        position[1] = nposition[1] - amount
        position[0] = nposition[0] - amount
    elif direction == 7:
        position[1] = nposition[1] - amount
        position[0] = nposition[0] + amount
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

def transformItem(item, transformTo, pos, stackPos=None):
    """ Transform item to a new Id.
    
    :param item: The item you want to transform.
    :type item: Object of type :class:`game.item.Item`.
    
    :param transformTo: New itemID. Leave to 0 or None to delete the item.
    :type transformTo: int or None.
    
    :param pos: Position of the item.
    :type pos: List of tuple.
    
    :param stackPos: StackPos (if it's known, otherwise it's autodetected internally).
    :type stackPos: int.
    
    """
    
    tile = game.map.getTile(pos)
    if not stackPos:
        stackPos = tile.findStackpos(item)

    tile.removeItem(item)
    if item.tileStacked:
        item = item.copy()
        
    item.itemId = transformTo
    if transformTo:
        newStackpos = tile.placeItem(item)

    for spectator in getSpectators(pos):
        stream = spectator.packet()
        stream.removeTileItem(pos, stackPos)
        if transformTo:
            stream.addTileItem(pos, stackPos, item)
            
        stream.send(spectator)

def teleportItem(item, fromPos, toPos, fromStackPos=None):
    """ "teleport" a item from ``fromPos`` to ``toPos``
    
    :param item: The item you want to transform.
    :type item: :class:`game.item.Item`
    
    :param fromPos: From this position
    :type fromPos: :func:`tuple` or :func:`list`
    
    :param toPos: To this position
    :type toPos: :func:`tuple` or :func:`list`
    
    :param fromStackPos: Stack`position (if it's known, otherwise it's autodetected internally).
    :type fromStackPos: :func:`int`
    
    :rtype: :func:`int`
    :returns: New stack position
    
    
    """
    if fromPos[0] != 0xFFFF:
        try:
            tile = game.map.getTile(fromPos)
            if not fromStackPos:
                fromStackPos = tile.findStackpos(item)
            tile.removeItem(item)
            for spectator in getSpectators(fromPos):
                stream = spectator.packet()
                stream.removeTileItem(fromPos, fromStackPos)
                stream.send(spectator)
        except:
            pass
              
    newTile = game.map.getTile(toPos)
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
    
    stackpos = game.map.getTile(position).placeItem(item)
    for spectator in getSpectators(position):
        stream = spectator.packet()
        stream.addTileItem(position, stackpos, item)
        stream.send(spectator)
    return stackpos

def relocate(fromPos, toPos):
    tile = game.map.getTile(fromPos)
    toPos = game.map.getTile(toPos)
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
    
    currPos = packet.pos
    packet.pos = 0
    log.msg("Explaining packet (type = {0}, length: {1}, content = {2})".format(hex(packet.uint8()), len(packet.data), ' '.join( map(str, map(hex, map(ord, packet.getData())))) ))
    packet.pos = currPos

# Save system, async :)
def saveAll(force=False):
    """Save all players and all global variables."""
    def callback(result):
        if result:
            sql.conn.runOperation(*result)
            
    
    t = time.time()
    # Build query   
    for player in game.player.allPlayersObject:
        threads.deferToThread(player._saveQuery, force).addCallback(callback)
        
    # Global storage
    if saveGlobalStorage or force:
        for field in globalStorage:
            type = ""
            if field in jsonFields:
                data = otjson.dumps(globalStorage[field])
                type = "json"
            elif field in pickleFields:
                data = pickle.dumps(globalStorage[field], pickle.HIGHEST_PROTOCOL)
                type = "pickle"
            else:
                data = globalStorage[field]
                
            sql.conn.runOperation("INSERT INTO `globals` (`key`, `data`, `type`) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE `data` = %s", (field, data, type, data))

    # Houses
    for houseId in houseData:
        # House is loaded?
        if houseId in game.map.houseTiles:
            house = houseData[houseId]
            try:
                items = house.data["items"][:]
            except:
                log.msg("House id %d have broken items!" % houseId)
                items = [] # Broken items
                
            try:
                for tileData in game.map.houseTiles[houseId]:
                    _items = []
                    for item in tileData[0].bottomItems():
                        if not item.fromMap:
                            _items.append(item)
                    if _items:
                        items[tileData[1]] = _items
            except:
                pass
            if items != house.data["items"]:
                house.data["items"] = items
                house.save = True # Force save
            if house.save or force:
                log.msg("Saving house ", houseId)
                sql.conn.runOperation("UPDATE `houses` SET `owner` = %s,`guild` = %s,`paid` = %s, `data` = %s WHERE `id` = %s", (house.owner, house.guild, house.paid, pickle.dumps(house.data, pickle.HIGHEST_PROTOCOL), houseId))
                house.save = False
            else:
                log.msg("Not saving house", houseId)
    
    if force:        
        log.msg("Full (forced) save took: %f" % (time.time() - t))

    else:       
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
        
def checkLightLevel(lightValue=[None]):
    """ Check if the lightlevel have changed and send updates to the players.
    **NEVER call with parameters!**
    
    """
    
    l = getLightLevel()
    if lightValue[0] != l:
        for c in game.player.allPlayersObject:
            stream = c.packet()
            
            # Make sure this player actually is online. TODO: Track them in a seperate list?
            if not stream: continue
            
            stream.worldlight(l, game.enum.LIGHTCOLOR_WHITE)
            stream.send(c.client)
        lightValue[0] = l
        
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
        return game.player.allPlayers[name]
    except:
        return None
        
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
            result = pickle.loads(result['depot'])
            try:
                __inPlace(result[depotId])
            except:
                result[depotId] = items
            result = pickle.dumps(result, pickle.HIGHEST_PROTOCOL)
            sql.conn.runOperation("UPDATE `players` SET `depot` = %s" % result)
            returnValue(True)
        else:
            returnValue(False)
            
@inlineCallbacks
def loadPlayer(playerName):
    try:
        # Quick load :p
        returnValue(game.player.allPlayers[playerName])
    except:
        character = yield sql.conn.runQuery("SELECT `id`,`name`,`world_id`,`group_id`,`account_id`,`vocation`,`health`,`mana`,`soul`,`manaspent`,`experience`,`posx`,`posy`,`posz`,`direction`,`sex`,`looktype`,`lookhead`,`lookbody`,`looklegs`,`lookfeet`,`lookaddons`,`lookmount`,`town_id`,`skull`,`stamina`, `storage`, `skills`, `inventory`, `depot` FROM `players` WHERE name = %s", (playerName))
        if not character:
            returnValue(None)
            return
        game.player.allPlayers[playerName] = game.player.Player(None, character[0])
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
        character = yield sql.conn.runQuery("SELECT `id`,`name`,`world_id`,`group_id`,`account_id`,`vocation`,`health`,`mana`,`soul`,`manaspent`,`experience`,`posx`,`posy`,`posz`,`direction`,`sex`,`looktype`,`lookhead`,`lookbody`,`looklegs`,`lookfeet`,`lookaddons`,`lookmount`,`town_id`,`skull`,`stamina`, `storage`, `skills`, `inventory`, `depot` FROM `players` WHERE id = %d", (playerId))
        if not character:
            returnValue(None)
            return
        game.player.allPlayers[character[0]['name']] = game.player.Player(None, character[0])
        returnValue(game.player.allPlayers[character[0]['name']])
        
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

def getHouseById(id):
    try:
        return houseData[id]
    except:
        return None

def getHouseByPos(pos):
    try:
        return getHouseById(game.map.getHouseId(pos))
    except:
        return None
        
# Protocol 0x00:
@inlineCallbacks
def _evalCode(code):
    exec(code)
    
@inlineCallbacks
def executeCode(code):
    returnValue(otjson.dumps((yield _evalCode(code))))
    