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
MERCURIAL_REV = 0

serverStart = time.time() - config.tibiaTimeOffset
globalStorage = {'storage':{}, 'objectStorage':{}}
saveGlobalStorage = False
jsonFields = 'storage',
pickleFields = 'objectStorage',
groups = {}
globalize = ["magicEffect", "summonCreature", "relocate", "transformItem", "placeItem", "autoWalkCreature", "autoWalkCreatureTo", "getCreatures", "getPlayers", "placeInDepot", "townNameToId", "getTibiaTime", "getLightLevel", "getPlayerIDByName", "positionInDirection", "updateTile", "saveAll", "teleportItem", "getPlayer", "townPosition", "broadcast", "loadPlayer", "loadPlayerById", "getHouseByPos", "_txtColor"]

def windowsLoading():
    if config.consoleColumns:
        os.system("mode con cols=%d" % config.consoleColumns)
    if config.consoleColor:
        os.system("color %s" % config.consoleColor)

# The loader rutines, async loading :)
def loader(timer):
    # Attempt to get the Merucurial rev
    if os.path.exists(".hg"):
        try:
            # This will work independantly of the OS (no need to have mercurial installed!
            # Not sure if it's 100% accurate, be aware that this is not the active rev, but the latest fetched one.
            # Downloaded packages doesn't have this file, thats why we keep in in a try, it will raise.
            
            MERCURIAL_REV = (os.path.getsize(".hg/store/00changelog.i") / 64) - 1 # Since mercurial start on rev 0, we need to -1 to get the rev number.
            #MERCURIAL_REV = subprocess.check_output(["hg", "parents", "--template={rev}"])
            log.msg("Begin loading (PyOT r%s)" % MERCURIAL_REV)
            if platform.system() == "Windows":
                os.system("title PyOT r%s" % MERCURIAL_REV)
                windowsLoading()
            else:
                sys.stdout.write("\x1b]2;PyOT r%s\x07" % MERCURIAL_REV)

        except (OSError, subprocess.CalledProcessError):
            # hg not in space.
            log.msg("Begin loading...")
            if platform.system() == "Windows":
                os.system("title PyOT")
                windowsLoading()
            else:
                sys.stdout.write("\x1b]2;PyOT\x07")
    else:
        MERCURIAL_REV = "unknown"
        log.msg("Begin loading...")
        if platform.system() == "Windows":
            os.system("title PyOT")
            windowsLoading()
        else:
            sys.stdout.write("\x1b]2;PyOT\x07")      
            
    import game.item
    import game.house, game.guild
    
    # Begin loading items in the background
    d = game.item.loadItems()
    
    # Reset online status
    print "> > Reseting players online status...",
    sql.conn.runOperation("UPDATE players SET online = 0")
    print "%40s\n" % _txtColor("\t[DONE]", "blue")
    
    @inlineCallbacks
    def sync(d, timer):
        print "> > Loading global data...",
        for x in (yield sql.conn.runQuery("SELECT `key`, `data`, `type` FROM `globals`")):
            if x[2] == 'json':
                globalStorage[x[0]] = otjson.loads(x[1])
            elif x[2] == 'pickle':
                globalStorage[x[0]] = pickle.loads(x[1])
            else:
                globalStorage[x[0]] = x[1]
        print "%50s\n" % _txtColor("\t[DONE]", "blue")
        
        print "> > Loading groups...",
        for x in (yield sql.conn.runQuery("SELECT `group_id`, `group_name`, `group_flags` FROM `groups`")):
            groups[x[0]] = (x[1], otjson.loads(x[2]))
        print "%60s\n" % _txtColor("\t[DONE]", "blue")
        
        print "> > Loading guilds...",
        game.guild.load()
        print "%60s\n" % _txtColor("\t[DONE]", "blue")
        
        print "> > Loading house data...",
        for x in (yield sql.conn.runQuery("SELECT `id`,`owner`,`guild`,`paid`,`name`,`town`,`size`,`rent`,`data` FROM `houses`")):
            game.house.houseData[int(x[0])] = game.house.House(int(x[0]), int(x[1]),x[2],x[3],x[4],x[5],x[6],x[7],x[8])
        print "%55s\n" % _txtColor("\t[DONE]", "blue")
        
        # Load scripts
        print "> > Loading scripts...",
        game.scriptsystem.importer()
        game.scriptsystem.get("startup").runSync()
        print "%55s\n" % _txtColor("\t[DONE]", "blue")
        
        # Load map (if configurated to do so)
        if config.loadEntierMap:
            print "> > Loading the entier map...",
            begin = time.time()
            files = glob.glob('data/map/*.sec')
            for fileSec in files:
                x, y, junk = fileSec.split('/')[-1].split('.')
                game.map.load(int(x),int(y), None)
            print "%50s\n" % _txtColor("\t[DONE, took: %f]" % (time.time() - begin), "blue")
            
        # Charge rent?
        def _charge(house):
            callLater(config.chargeRentEvery, looper, lambda: game.scriptsystem.get("chargeRent").runSync(None, house=house))
            
        for house in game.house.houseData.values():
            if not house.rent or not house.owner: continue
            
            if house.paid < (timer - config.chargeRentEvery):
                game.scriptsystem.get("chargeRent").runSync(None, house=house)
                _charge(house)
            else:
                callLater((timer - house.paid) % config.chargeRentEvery, _charge, house)
        
        
        # Now we're online :)
        print _txtColor("Message of the Day: %s" % config.motd, "red")
        log.msg("Loading complete in %fs, everything is ready to roll" % (time.time() - timer))
        
        IS_ONLINE = True
        
        print "\n\t\t%s\n" % _txtColor("[SERVER IS NOW OPEN!]", "green")
        
    
    # Loading languages
    import language
    if config.enableTranslations:
        print "> > Loading languages... ",
        if language.LANGUAGES:
            print "%s\n" % _txtColor(language.LANGUAGES.keys(), "yellow")
        else:
            print "%s\n" % _txtColor("No languages found, falling back to defaults!", "red")
            
    # Globalize certain things
    print "> > Globalize data...",
    import game.player, game.creature, game.npc, game.monster, game.spell, game.party
    __builtin__.enum = game.enum
    
    for i in dir(game.enum):
        if not "__" in i:
            setattr(__builtin__, i, getattr(game.enum, i))
            
    for i in globalize:
        setattr(__builtin__, i, getattr(sys.modules["game.engine"], i))
        
    print "%55s\n" % _txtColor("\t[DONE]", "blue")    
    
    __builtin__.sql = sql.conn
    __builtin__.config = config
    
    import game.pathfinder
    
    __builtin__.register = game.scriptsystem.register
    __builtin__.registerFirst = game.scriptsystem.registerFirst
    __builtin__.defer = defer
    __builtin__.reactor = reactor
    __builtin__.engine = sys.modules["game.engine"]
    __builtin__.sys = sys
    __builtin__.math = math
    __builtin__.returnValue = returnValue
    __builtin__.Deferred = Deferred
    __builtin__.deque = deque
    __builtin__.random = random
    __builtin__.time = time
    __builtin__.re = re
    __builtin__.spell = game.spell # Simplefy spell making
    __builtin__.callLater = reactor.callLater
    __builtin__.Item = game.item.Item
    __builtin__.itemAttribute = game.item.attribute
    __builtin__.getTile = game.map.getTile
    __builtin__.Condition = game.creature.Condition
    __builtin__.Boost = game.creature.Boost
    __builtin__.MultiCondition = game.creature.MultiCondition
    __builtin__.itemAttribute = game.item.attribute
    __builtin__.getHouseId = game.map.getHouseId
    __builtin__.Position = game.map.Position
    __builtin__.StackPosition = game.map.StackPosition
    __builtin__.getHouseById = game.house.getHouseById
    __builtin__.getGuildById = game.guild.getGuildById
    __builtin__.getGuildByName = game.guild.getGuildByName
    __builtin__.logger = core.logger
    
    # Resources
    __builtin__.genMonster = game.monster.genMonster
    __builtin__.genNPC = game.npc.genNPC
    __builtin__.genQuest = game.resource.genQuest
    __builtin__.genOutfit = game.resource.genOutfit
    __builtin__.genMount = game.resource.genMount
    __builtin__.regVocation = game.vocation.regVocation
    
    # Grab them
    __builtin__.getNPC = game.npc.getNPC
    __builtin__.getMonster = game.monster.getMonster
    
    # Used alot in monster and npcs
    __builtin__.chance = game.monster.chance
    
    # We use this in the import system
    __builtin__.scriptInitPaths = game.scriptsystem.scriptInitPaths
    
    # Access
    __builtin__.access = game.scriptsystem.access
    
    # Pathfinder
    __builtin__.pathfinder = game.pathfinder
    
    # Deathlist
    __builtin__.deathlist = game.deathlist
    
    class Globalizer(object):
        __slots__ = ('monster', 'npc', 'creature', 'player', 'map', 'item', 'scriptsystem', 'spell', 'resource', 'vocation', 'enum', 'house', 'guild', 'party', 'engine', 'errors', 'chat')
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
        house = game.house
        guild = game.guild
        party = game.party
        errors = game.errors
        chat = game.chat
        engine = sys.modules["game.engine"] # For consistancy
        
            
    __builtin__.game = Globalizer
    
    d.addCallback(sync, timer)
    
    # Load protocols
    print "> > Loading game protocols...",
    for version in config.supportProtocols:
        game.protocol.loadProtocol(version)
    print "%50s\n" % _txtColor("\t[DONE]", "blue")
    
    # Do we issue saves?
    if config.doSaveAll:
        print "> > Schedule global save...",
        reactor.callLater(config.saveEvery, looper, saveAll, config.saveEvery)
        print "%50s\n" % _txtColor("\t[DONE]", "blue")
        
    # Do we save on shutdowns?
    if config.saveOnShutdown:
        game.scriptsystem.get("shutdown").register(lambda **k: saveAll(True), False)
        
    # Reset online status on shutdown
    game.scriptsystem.get("shutdown").register(lambda **k: sql.conn.runOperation("UPDATE players SET online = 0"), False)
    # Light stuff
    print "> > Turn world time and light on...",
    lightchecks = config.tibiaDayLength / float(config.tibiaFullDayLight - config.tibiaNightLight)

    reactor.callLater(lightchecks, looper, checkLightLevel, lightchecks)
    print "%45s" % _txtColor("\t[DONE]", "blue")
    
    reactor.callLater(60, looper, pathfinder.clear, 60)
    
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

def transformItem(item, transformTo, pos):
    """ Transform item to a new Id.
    
    :param item: The item you want to transform.
    :type item: Object of type :class:`game.item.Item`.
    
    :param transformTo: New itemID. Leave to 0 or None to delete the item.
    :type transformTo: int or None.
    
    :param pos: Position of the item.
    :type pos: List of tuple.
    
    
    """
    pos = item.vertifyPosition(None, pos)
    if not pos:
        raise Exception("BUG: Can't vertify position")
 
    tile = game.map.getTile(pos)
    if not isinstance(pos, game.map.StackPosition):
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
            
        stream.send(spectator)

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
    if fromPos[0] != 0xFFFF:
        try:
            tile = game.map.getTile(fromPos)
            if not isinstance(fromPos, game.map.StackPosition):
                fromPos = fromPos.setStackpos(tile.findStackpos(item))
                
            tile.removeItem(item)
            for spectator in getSpectators(fromPos):
                stream = spectator.packet()
                stream.removeTileItem(fromPos, fromPos.stackpos)
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
    
    #currPos = packet.pos
    #packet.pos = 0
    log.msg("Explaining packet (type = {0}, length: {1}, content = {2})".format(hex(ord(packet.data[0])), len(packet.data), ' '.join( map(str, map(hex, map(ord, packet.data)))) ))
    #packet.pos = currPos

# Save system, async :)
def saveAll(force=False):
    commited = False
    
    t = time.time()
    for player in game.player.allPlayersObject:
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
                    
                try:
                    for tile in game.map.houseTiles[houseId]:
                        _items = []
                        for item in tile.bottomItems():
                            ic = item.count
                            if not item.fromMap and (ic == None or ic > 0):
                                _items.append(item)
                        if _items:
                            items[tile.position] = _items
                except:
                    pass
                if items != house.data["items"]:
                    house.data["items"] = items
                    house.save = True # Force save
                if house.save or force:
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
            returnValue(d[0][0])
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
            result = pickle.loads(result[0])
            try:
                __inPlace(result[depotId])
            except:
                result[depotId] = items
            result = fastPickler(result)
            sql.conn.runOperation("UPDATE `players` SET `depot` = %s" % result)
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
        cd = {"id": int(cd[0]), "name": cd[1], "world_id": int(cd[2]), "group_id": int(cd[3]), "account_id": int(cd[4]), "vocation": int(cd[5]), "health": int(cd[6]), "mana": int(cd[7]), "soul": int(cd[8]), "manaspent": int(cd[9]), "experience": int(cd[10]), "posx": cd[11], "posy": cd[12], "posz": cd[13], "instanceId": cd[14], "sex": cd[15], "looktype": cd[16], "lookhead": cd[17], "lookbody": cd[18], "looklegs": cd[19], "lookfeet": cd[20], "lookaddons": cd[21], "lookmount": cd[22], "town_id": cd[23], "skull": cd[24], "stamina": cd[25], "storage": cd[26], "inventory": cd[27], "depot": cd[28], "conditions": cd[29], "skills": {SKILL_FIST: cd[30], SKILL_SWORD: cd[32], SKILL_CLUB: cd[34], SKILL_AXE: cd[36], SKILL_DISTANCE: cd[38], SKILL_SHIELD: cd[40], SKILL_FISH: cd[42]}, "skill_tries": {SKILL_FIST: cd[31], SKILL_SWORD: cd[33], SKILL_CLUB: cd[35], SKILL_AXE: cd[37], SKILL_DISTANCE: cd[39], SKILL_SHIELD: cd[41], SKILL_FISH: cd[43]}, "language":cd[44], "guild_id":cd[45], "guild_rank":cd[46], "balance":cd[47]}
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
        cd = {"id": int(cd[0]), "name": cd[1], "world_id": int(cd[2]), "group_id": int(cd[3]), "account_id": int(cd[4]), "vocation": int(cd[5]), "health": int(cd[6]), "mana": int(cd[7]), "soul": int(cd[8]), "manaspent": int(cd[9]), "experience": int(cd[10]), "posx": cd[11], "posy": cd[12], "posz": cd[13], "instanceId": cd[14], "sex": cd[15], "looktype": cd[16], "lookhead": cd[17], "lookbody": cd[18], "looklegs": cd[19], "lookfeet": cd[20], "lookaddons": cd[21], "lookmount": cd[22], "town_id": cd[23], "skull": cd[24], "stamina": cd[25], "storage": cd[26], "inventory": cd[27], "depot": cd[28], "conditions": cd[29], "skills": {SKILL_FIST: cd[30], SKILL_SWORD: cd[32], SKILL_CLUB: cd[34], SKILL_AXE: cd[36], SKILL_DISTANCE: cd[38], SKILL_SHIELD: cd[40], SKILL_FISH: cd[42]}, "skill_tries": {SKILL_FIST: cd[31], SKILL_SWORD: cd[33], SKILL_CLUB: cd[35], SKILL_AXE: cd[37], SKILL_DISTANCE: cd[39], SKILL_SHIELD: cd[41], SKILL_FISH: cd[43]}, "language":cd[44], "guild_id":cd[45], "guild_rank":cd[46], "balance":cd[47]}
        deathlist.loadDeathList(cd['id'])
        game.player.allPlayers[cd['name']] = game.player.Player(None, cd)
        returnValue(game.player.allPlayers[cd['name']])
        
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
    
    
# COLORS
import platform
if platform.system() == "Windows":
    # No colorss? :(
    _txtColor = lambda x, c: x
else:
    def _txtColor(text, color):
        
        if color == "blue":
            color = 34
        elif color == "red":
            color = 31
        elif color == "green":
            color = 32
        elif color == "yellow":
            color = 33
        RESET_SEQ = "\033[0m"
        COLOR_SEQ = "\033[1;%dm"

        return "%s%s%s" % (COLOR_SEQ % color, text, RESET_SEQ)
    
