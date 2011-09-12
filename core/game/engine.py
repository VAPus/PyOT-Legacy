"""A collection of functions that almost every other component requires"""

from twisted.internet import reactor, threads
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
import game.protocol

try:
    import cPickle as pickle
except:
    import pickle
    
serverStart = time.time() - config.tibiaTimeOffset
globalStorage = {'storage':{}, 'objectStorage':{}}
jsonFields = ['storage']
pickleFields = ['objectStorage']

# The loader rutines, async loading :)
def loader(timer):
    log.msg("Begin loading...")
    from game.item import loadItems
    # Begin loading items in the background
    d = loadItems()

    @inlineCallbacks
    def _sql_():
        for x in (yield sql.conn.runQuery("SELECT `key`, `data`, `type` FROM `globals`")):
            if x['type'] == 'json':
                globalStorage[x['key']] = otjson.loads(x['data'])
            elif x['type'] == 'pickle':
                globalStorage[x['key']] = pickle.loads(x['data'])
            else:
                globalStorage[x['key']] = x['data']
    _sql_()
                    
    def sync(d, timer):
        # Load protocols
        for version in config.supportProtocols:
            game.protocol.loadProtocol(version)
            
        # Load scripts
        from game.scriptsystem import importer
        importer()
        
        # Load map (if configurated to do so)
        if config.loadEntierMap:
            from game.map import load
            import glob
            begin = time.time()
            files = glob.glob('data/map/*.sec')
            for fileSec in files:
                def __(fileSec):
                    fileSec = fileSec.split('/')[-1]
                    x, y, junk = fileSec.split('.')
                    load(int(x),int(y))
                
                ret = threads.deferToThread(__, fileSec)
            ret.addCallback(lambda x: log.msg("Loaded entier map in %f" % (time.time() - begin)))
        
        # Just a inner funny call
        def looper(f, t):
            f()
            reactor.callLater(t, looper, f, t)
        
        # Do we issue saves?
        if config.doSaveAll:
            reactor.callLater(config.saveEvery, looper, saveAll, config.saveEvery)
            
        # Light stuff
        lightchecks = config.tibiaDayLength / float(config.tibiaFullDayLight - config.tibiaNightLight)
        reactor.callLater(lightchecks, looper, checkLightLevel, lightchecks)
        
        game.scriptsystem.get("startup").runSync(None)
        
        log.msg("Loading complete in %fs, everything is ready to roll" % (time.time() - timer))
        
        
    d.addCallback(sync, timer)


# Useful for windows
def safeTime():
    """Gives the time rounded so it can be divided by 60. This gives the same time on both unix systems and Windows.
    
    :rtype: float time.
    :returns: Time rounded so it can be divided by 60.
    
    """
    return math.ceil(time.time() * 60) / 60

def safeCallLater(sec, *args):
    """This is a thread safe and time safe call for reactor.callLater. Passes args to callLater.
    
    :param sec: The number of seconds to delay the calls.
    :type sec: float.
    
    """
    reactor.callFromThread(reactor.callLater, math.ceil(sec * 60) / 60, *args) # Closest step to the accurecy of windows clock


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
            safeCallLater(time/2, reactor.callInThread, new_f, *args, **kwargs)
            
        return first
    return decor
# First order of buisness, the autoWalker
@action(True)
def autoWalkCreature(creature, walkPatterns, callback=None):
    """Autowalk the creature using the walk patterns. This binds the action slot.
    
    :param creature: The creature to autowalk of type :class:`core.game.creature.Creature` or any subclass of it.
    :type creature: :class:`core.game.creature.Creature`.
    :param walkPatterns: List of steps to take.
    :type walkPatterns: :class:`collections.deque`.
    :param callback: Call this function when the creature reach it's destination.
    :type callback: function.
    
    """
    
    try:
        creature.action = safeCallLater(creature.stepDuration(game.map.getTile(creature.positionInDirection(walkPatterns[0])).getThing(0)), handleAutoWalking, creature, walkPatterns, callback)
    except:
        # Just have to assume he goes down?
        pos = positionInDirection(creature.position, walkPatterns[0], 2)
        pos[2] += 1
        creature.teleport(pos)
        
# This one calculate the tiles on the way
def autoWalkCreatureTo(creature, to, skipFields=0, diagonal=True, callback=None):
    """Autowalk the creature using the walk patterns. This binds the action slot.
    
    :param creature: The creature to autowalk of type :class:`core.game.creature.Creature` or any subclass of it.
    :type creature: :class:`core.game.creature.Creature`.
    
    :param to: Destination position.
    :type to: list or tuple.
    
    :param skipFields: Don't walk the last steps to the destination. Useful if you intend to walk close to a target.
    :type skipFields: int.
    
    :param diagonal: Allow diagonal walking?
    :type diagonal: bool.
    
    :param callback: Call this function when the creature reach it's destination.
    :type callback: function.
    
    """
    
    pattern = calculateWalkPattern(creature.position, to, skipFields, diagonal)
    print pattern
    if pattern:
        autoWalkCreature(creature, deque(pattern), callback)
    elif callback:
        callback(None)
        
@action()
def handleAutoWalking(creature, walkPatterns, callback=None, level=0):
    if not walkPatterns:
        return
        
    direction = walkPatterns.popleft()
    currPos = creature.position[:]
    mcallback=callback
    if walkPatterns:
        def mcallback(ret):
            creature2, oldPos, newPos = ret
            if oldPos == currPos:
                creature.action = safeCallLater(creature2.stepDuration(game.map.getTile(positionInDirection(newPos, walkPatterns[0])).getThing(0)), handleAutoWalking, creature2, walkPatterns, callback)
            else:
                pass #creature2.cancelWalk(walkPatterns[0])
    
    d = Deferred()
    if mcallback:
        d.addCallback(mcallback)
    creature._move(d, direction, level=level)
    
    

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
    
    :rtype: set of :class:`core.game.creature.Creature` compatible objects
    
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
    
    :rtype: set of :class:`core.game.player.Player` compatible objects
    
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
    
    position = nposition[:] # Important not to remove the : here, we don't want a reference!
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
    *Note that this function does NOT replace the known tile in :mod:`core.game.map`'s knownMap array.*
    
    :param pos: Position of tile.
    :type pos: list or tuple.
    :param tile: The tile that replace the currently known tile at the position.
    :type tile: Tile of type :class:`core.game.map.Tile`.
    
    """
    
    for spectator in getSpectators(pos):
        stream = spectator.packet(0x69)
        stream.position(pos)
        stream.tileDescription(tile)
        stream.uint8(0x00)
        stream.uint8(0xFF)
        stream.send(spectator)

def transformItem(item, transformTo, pos, stackPos=None):
    """ Transform item to a new Id.
    
    :param item: The item you want to transform.
    :type item: Object of type :class:`core.game.item.Item`.
    
    :param transformTo: New itemID. Leave to 0 or None to delete the item.
    :type transformTo: int or None.
    
    :param pos: Position of the item.
    :type pos: List of tuple.
    
    :param stackPos: StackPos (if it's known, otherwise it's autodetected internally).
    :type stackPos: int.
    
    """
    item.itemId = transformTo
    if not stackPos:
        stackPos = game.map.getTile(pos).findStackpos(item)
    game.map.getTile(pos).removeItem(item)
    
    for spectator in getSpectators(pos):
        stream = spectator.packet()

        if transformTo:
            stream.updateTileItem(pos, stackPos, item)
        else:
            stream.removeTileItem(pos, stackPos)
            
        stream.send(spectator)

def teleportItem(item, fromPos, toPos, fromStackPos=None):
    """ "teleport" a item from ``fromPos`` to ``toPos``
    
    :param item: The item you want to transform.
    :type item: :class:`core.game.item.Item`
    
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
    toStackPos = newTile.placeItem(item)
        
    for spectator in getSpectators(toPos):
        stream = spectator.packet()
        stream.addTileItem(toPos, toStackPos, item)
        stream.send(spectator)
        
    return toStackPos
        
def placeItem(item, position):
    """ Place a item to a position
    
    :param item: The item to place.
    :type item: Object of type :class:`core.game.item.Item`.
    
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
        stackpos = toPos.placeItem(item)
        items.append((item, tile.getSlot(item), stackpos))
        
    for item in items:    
        tile.removeItem(item)
        
    for spectator in getSpectators(fromPos):
        stream = spectator.packet()
        for pair in items:
            stream.removeTileItem(fromPos, pair[1])
        stream.send(self.client)

    for spectator in getSpectators(toPos):
        stream = spectator.packet()
        for pair in items:
            stream.addTileItem(toPos, pair[2], pair[0])
        stream.send(self.client)
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

# The auto type caster
def autoCastValue(data): # We get a string, then find the simplest possible value for it
    if not data:
        return None

    try:
        data = int(data)
        if data == 1:
            return True
        elif data == 0:
            return False
        else:
            return data

    except:
        return data
        
# Call that ignores failours
def ignore(result):
    pass

# Save system, async :)
def saveAll():
    """Save all players and all global variables."""
    
    # Build query
    try:
        def callback(result):
            sql.conn.runOperation(*result)
            
        for player in game.player.allPlayersObject:
            d = threads.deferToThread(player._saveQuery)
            d.addCallback(callback)
    except:
        pass # No players
        
    # Global storage
    for field in globalStorage:
        type = ""
        if field in jsonFields:
            data = otjson.dumps(globalStorage[field])
            type = "json"
        elif field in pickleFields:
            data = pickle.dumps(globalStorage[field])
            type = "pickle"
        else:
            data = globalStorage[field]
            
        sql.conn.runOperation("INSERT INTO `globals` (`key`, `data`, `type`) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE `data` = %s", (field, data, type, data))
        
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
        for c in getSpectators((0x7FFF,0x7FFF,7), (100000, 100000)):
            stream = c.packet()
            stream.worldlight(l, game.enum.LIGHTCOLOR_WHITE)
            stream.send(c)
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
            defer.returnValue(d['id'])
        else:
            defer.returnValue(None)

def townNameToId(name):
    """ Return the townID based on town name.
    
    :rtype: int or None.
    
    """
    
    import data.map.info as i
    for id in i.towns:
        if i.towns[id][0] == name:
            return id

@inlineCallbacks
def placeInDepot(name, depotId, items):
    """ Place items into the depotId of player with a name. This can be used even if the player is offline.
    
    :param name: Player name.
    :type name: str.
    
    :param depotId: DepotID to place items into.
    :type depotId: int or str.
    
    :param items: Either one Item or a list of items to place into the depot.
    :type items: Either one object of type :class:`core.game.item.Item`, or a list of objects.
    
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
        