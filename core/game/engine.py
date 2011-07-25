# This act as the core event system
from twisted.internet import reactor
from collections import deque
from twisted.python import log
import time
from packet import TibiaPacket
import game.map

# The loader rutines, async loading :)
def loader(timer):
    log.msg("Begin loading...")
    from game.item import loadItems
    # Begin loading items in the background
    d = loadItems()
    
    # This is called once we are done with all loading, we got to use deferred on all future rutines too
    def printer(d, timer):
        log.msg("Loading complete in %fs, everything is ready to roll" % (time.time() - timer))
        
    d.addCallback(printer, timer)

# The action decorator :)
def action(forced=False, delay=0):
    def decor(f):
        def new_f(creature, *args, **argw):
            creature.actionLock.acquire()
            if creature.action and forced: # + forced
                creature.action.cancel()
            elif creature.action:
                creature.action.addCallback(f, creature, *args, **argw)
            else:
                f(creature, *args, **argw)
                
            # (forced actions are released first when their done
            if not forced:
                creature.actionLock.release()
        return new_f
    return decor
    
# First order of buisness, the autoWalker
@action()
def autoWalkCreature(creature, walkPatterns, callback=None): 
    creature.action = reactor.callLater(0, handleAutoWalking, creature, walkPatterns, callback)
    
# This one calculate the tiles on the way
def autoWalkCreatureTo(creature, to, skipFields=0, diagonal=True, callback=None):

    pattern = calculateWalkPattern(creature.position, to, skipFields, diagonal)
    if pattern:
        autoWalkCreature(creature, deque(pattern), callback)
        
def handleAutoWalking(creature, walkPatterns, callback=None):
    direction = walkPatterns.popleft()
    ret = creature.move(direction)
    if ret and len(walkPatterns):
        creature.actionLock.acquire()
        creature.action = reactor.callLater(creature.stepDuration(game.map.getTile(creature.position).getThing(0)), handleAutoWalking, creature, walkPatterns, callback)
        creature.actionLock.release()
    else:
        creature.action = None
        
    if callback and ret and not len(walkPatterns):    
        reactor.callLater(creature.stepDuration(game.map.getTile(creature.position).getThing(0)), callback)

# Calculate walk patterns
def calculateWalkPattern(fromPos, to, skipFields=None, diagonal=True):
    pattern = []
    
    # First diagonal if possible
    if abs(fromPos[0] - to[0]) == 1 and abs(fromPos[1] - to[1]) == 1:
        if fromPos[1] > to[1]:
            base = 6
        else:
            base = 4
            
        if fromPos[0] < to[0]:
            base += 1
            
        pattern.append(base)
        
    else:
        # First x walk
        if fromPos[0] > to[0]:
            for x in xrange(0, fromPos[0]-to[0]):
                pattern.append(3)
        elif fromPos[0] < to[0]:
            for x in xrange(0, to[0]-fromPos[0]):
                pattern.append(1)
        
        # Then y walking
        if fromPos[1] > to[1]:
            for x in xrange(0, fromPos[1]-to[1]):
                pattern.append(0)
        elif fromPos[1] < to[1]:
            for x in xrange(0, to[1]-fromPos[1]):
                pattern.append(2)
                
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
def getSpectatorList(pos, radius=(9,7), extra=[]):
    # At the moment, we only do one floor
    players = []

    if extra:
        for creature in extra:
            if creature.creatureType == 0:
                players.append(creature.client)
            
    for x in xrange(pos[0]-radius[0], pos[0]+radius[1]+1):
        for y in xrange(pos[1]-radius[1], pos[1]+radius[1]+1):
            try:
                for creature in game.map.knownMap[x][y][7].creatures():
                    if creature.creatureType == 0:
                        players.append(creature.client)
            except:
                pass # Tile isn't loaded

    return players

# Spectator list using yield
def getSpectators(pos, radius=(9,7), extra=[]):
    # At the moment, we only do one floor
    
    if extra:
        for creature in extra:
            if creature.creatureType == 0:
                yield creature.client
            
    for x in xrange(pos[0]-radius[0], pos[0]+radius[0]+1):
        for y in xrange(pos[1]-radius[1], pos[1]+radius[1]+1):
            try:
                for creature in game.map.knownMap[x][y][7].creatures():
                    # TODO: Check for player
                    if creature.creatureType == 0:
                        yield creature.client
            except:
                raise StopIteration
    raise StopIteration

    
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
        
# Last order of buisness, the script system
import game.scriptsystem
from data.scripts import *
