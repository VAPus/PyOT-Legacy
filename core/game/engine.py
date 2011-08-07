# This act as the core event system
from twisted.internet import reactor, threads
from collections import deque
from twisted.python import log
import time
from packet import TibiaPacket
import game.map
import config
import math
import game.pathfinder

# The loader rutines, async loading :)
def loader(timer):
    log.msg("Begin loading...")
    from game.item import loadItems
    # Begin loading items in the background
    d = loadItems()
    
    
    def sync(d, timer):
        from game.scriptsystem import importer
        importer()
        if config.loadEntierMap:
            from game.map import load
            begin = time.time()
            x = 0
            y = 0
            retOld = False
            ret = False
            while True:
                try:
                    ret = load(x,y)
                    y += 1
                except IOError:
                    x += 1
                    y = 0                

                if not ret and not retOld:
                    break
                retOld = ret  
                    
            log.msg("Loaded entier map in %f" % (time.time() - begin))


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
            elif not forced and creature.action and creature.action.active():
                safeCallLater(0, new_f, *args, **argw)
            elif delay:
                safeCallLater(delay, f, *args, **argw)
            else:
                f(creature, *args, **argw)

        return new_f
    return decor

def loopInThread(time):
    def decor(f):
        def new_f(*args, **kwargs):
            f(*args, **kwargs)
            safeCallLater(time, reactor.callInThread, f, *args, **kwargs)
            
        return new_f
    return decor
# First order of buisness, the autoWalker
@action()
def autoWalkCreature(creature, walkPatterns, callback=None): 
    creature.action = safeCallLater(creature.stepDuration(game.map.getTile(creature.positionInDirection(walkPatterns[0])).getThing(0), 0.5), handleAutoWalking, creature, walkPatterns, callback)
    
# This one calculate the tiles on the way
def autoWalkCreatureTo(creature, to, skipFields=0, diagonal=True, callback=None):

    pattern = calculateWalkPattern(creature.position, to, skipFields, diagonal)
    if pattern:
        autoWalkCreature(creature, deque(pattern), callback)

@action()
def handleAutoWalking(creature, walkPatterns, callback=None):
    if not walkPatterns:
        return
        
    direction = walkPatterns.popleft()
    ret = creature.move(direction)
    if ret and len(walkPatterns):
        creature.action = safeCallLater(creature.stepDuration(game.map.getTile(creature.positionInDirection(walkPatterns[0])).getThing(0)), handleAutoWalking, creature, walkPatterns, callback)
    else:
        creature.action = None
        
    if callback and ret and not len(walkPatterns):    
        safeCallLater(0, callback)

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
        if not game.map.getTile(newPos).getThing(1) or not game.map.getTile(newPos).getThing(1).solid:
            currPos = newPos
            pattern.append(base)
        
    if not pattern:
        pattern = game.pathfinder.findPath(game.map.knownMap[fromPos[2]], fromPos[0], fromPos[1], to[0], to[1])
                
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
def getSpectatorList(pos, radius=(9,7), extra=[], ignore=[]):
    # At the moment, we only do one floor
    players = []

    if extra:
        for creature in extra:
            if creature.creatureType == 0:
                players.append(creature.client)

    for x in xrange(pos[0]-radius[0], pos[0]+radius[1]+1):
        for y in xrange(pos[1]-radius[1], pos[1]+radius[1]+1):
            try:
                for creature in game.map.knownMap[pos[2]][x][y].creatures():
                    if creature.creatureType == 0 and not creature in ignore:
                        players.append(creature.client)
            except:
                pass # Tile isn't loaded

    return players

# Spectator list using yield
def getSpectators(pos, radius=(9,7), extra=[], ignore=[]):
    # At the moment, we only do one floor
    
    if extra:
        for creature in extra:
            if creature.creatureType == 0:
                yield creature.client
            
    for x in xrange(pos[0]-radius[0], pos[0]+radius[0]+1):
        for y in xrange(pos[1]-radius[1], pos[1]+radius[1]+1):
            try:
                for creature in game.map.knownMap[pos[2]][x][y].creatures():
                    if creature.creatureType == 0 and not creature in ignore:
                        yield creature.client
            except:
                pass # Tile isn't loaded
                
    raise StopIteration

# Calculate new position by direction
def positionInDirection(nposition, direction):
    position = nposition[:] # Important not to remove the : here, we don't want a reference!
    if direction == 0:
        position[1] = nposition[1] - 1
    elif direction == 1:
        position[0] = nposition[0] + 1
    elif direction == 2:
        position[1] = nposition[1] + 1
    elif direction == 3:
        position[0] = nposition[0] - 1
    elif direction == 4:
        position[1] = nposition[1] + 1
        position[0] = nposition[0] - 1
    elif direction == 5:
        position[1] = nposition[1] + 1
        position[0] = nposition[0] + 1
    elif direction == 6:
        position[1] = nposition[1] - 1
        position[0] = nposition[0] - 1
    elif direction == 7:
        position[1] = nposition[1] - 1
        position[0] = nposition[0] + 1
    return position
def updateTile(pos, tile):
    stream = TibiaPacket(0x69)
    stream.position(pos)
    stream.tileDescription(tile)
    stream.uint8(0x00)
    stream.uint8(0xFF)
    stream.sendto(getSpectators(pos))

def transformItem(item, transformTo, pos, stack):
    from game.item import cid
    stream = TibiaPacket()
    stream.updateTileItem(pos, stack, cid(transformTo))
    item.itemId = transformTo
    stream.sendto(getSpectators(pos))
                
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
        