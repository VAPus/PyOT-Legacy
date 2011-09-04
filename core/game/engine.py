# This act as the core event system
from twisted.internet import reactor, threads, defer
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
    
    @defer.deferredGenerator
    def _sql_():
        d = defer.waitForDeferred(sql.conn.runQuery("SELECT `key`, `data`, `type` FROM `globals`"))
        yield d
        for x in d.getResult():
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
        
            
        log.msg("Loading complete in %fs, everything is ready to roll" % (time.time() - timer))
        
        
    d.addCallback(sync, timer)


# Useful for windows
def safeTime():
    return math.ceil(time.time() * 60) / 60

def safeCallLater(sec, *args):
    reactor.callFromThread(reactor.callLater, math.ceil(sec * 60) / 60, *args) # Closest step to the accurecy of windows clock


# The action decorator :)
def action(forced=False, delay=0):
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
    try:
        creature.action = safeCallLater(creature.stepDuration(game.map.getTile(creature.positionInDirection(walkPatterns[0])).getThing(0)), handleAutoWalking, creature, walkPatterns, callback)
    except:
        # Just have to assume he goes down?
        pos = positionInDirection(creature.position, walkPatterns[0], 2)
        pos[2] += 1
        creature.teleport(pos)
        
# This one calculate the tiles on the way
def autoWalkCreatureTo(creature, to, skipFields=0, diagonal=True, callback=None):

    pattern = calculateWalkPattern(creature.position, to, skipFields, diagonal)

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
                
    ret = creature.move(direction, level=level)
    if mcallback:
        ret.addCallback(mcallback)
    

# Calculate walk patterns
def calculateWalkPattern(fromPos, to, skipFields=None, diagonal=True):
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
    creatures = set()
                
    for creature in game.creature.allCreaturesObject:
        if creature.canSee(pos, radius) and creature not in ignore:
            creatures.add(creature)
    return creatures
        
getCreatures = bindconstant._make_constants(getCreatures)

def getPlayers(pos, radius=(8,6), ignore=tuple()):
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
    for spectator in getSpectators(pos):
        stream = spectator.packet(0x69)
        stream.position(pos)
        stream.tileDescription(tile)
        stream.uint8(0x00)
        stream.uint8(0xFF)
        stream.send(spectator)

def transformItem(item, transformTo, pos, stack=None):
    for spectator in getSpectators(pos):
        stream = spectator.packet()
        item.itemId = transformTo
        if not stack:
            stack = game.map.getTile(pos).findStackpos(item)
            
        if transformTo:
            stream.updateTileItem(pos, stack, item)
        else:
            stream.removeTileItem(pos, stack)
            game.map.getTile(pos).removeItem(item)
        stream.send(spectator)

def placeItem(item, position):
    stackpos = game.map.getTile(position).placeItem(item)
    for spectator in getSpectators(position):
        stream = spectator.packet()
        stream.addTileItem(position, stackpos, item)
        stream.send(spectator)
    return stackpos
    
# The development debug system
def explainPacket(packet):
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
    seconds = ((time.time() - serverStart) % config.tibiaDayLength) * ((24*60*60) / config.tibiaDayLength)
    hours = int(float(seconds / 3600))
    seconds = seconds - (hours * 3600)
    minutes = int(seconds / 60)
    seconds = seconds % 60
    
    return (hours, minutes, seconds)
    
def getLightLevel():
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
    l = getLightLevel()
    if lightValue[0] != l:
        for c in getSpectators((0x7FFF,0x7FFF,7), (100000, 100000)):
            stream = c.packet()
            stream.worldlight(l, game.enum.LIGHTCOLOR_WHITE)
            stream.send(c)
        lightValue[0] = l
        