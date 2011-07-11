# This act as the core event system
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import deferLater
from twisted.internet import reactor
from collections import deque
from twisted.python import log
import time
from packet import TibiaPacket
import game.map

walkerEvents = {}

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

# First order of buisness, the autoWalker
def autoWalkCreature(creature, walkPatterns):
    if creature.clientId() in walkerEvents: # The walker locks
        walkerEvents[creature.clientId()].cancel()
        #creature.cancelMove(creature.direction)
        
    walkerEvents[creature.clientId()] = reactor.callLater(0, handleAutoWalking, creature, walkPatterns)
    
# This one calculate the tiles on the way
def autoWalkCreatureTo(creature, to):
    pattern = deque()
    
    # First diagonal if possible
    if abs(creature.position[0] - to[0]) == 1 and abs(creature.position[1] - to[1]) == 1:
        if creature.position[1] > to[1]:
            base = 6
        else:
            base = 4
            
        if creature.position[0] < to[0]:
            base += 1
            
        pattern.append(base)
        
    else:
        # First x walk
        if creature.position[0] > to[0]:
            for x in xrange(0, creature.position[0]-to[0]):
                pattern.append(3)
        elif creature.position[0] < to[0]:
            for x in xrange(0, to[0]-creature.position[0]):
                pattern.append(1)
        
        # Then y walking
        if creature.position[1] > to[1]:
            for x in xrange(0, creature.position[1]-to[1]):
                pattern.append(0)
        elif creature.position[1] < to[1]:
            for x in xrange(0, to[1]-creature.position[1]):
                pattern.append(2)
    print pattern
    if pattern:
        autoWalkCreature(creature, pattern)
def handleAutoWalking(creature, walkPatterns):
    direction = walkPatterns.popleft()
    ret = creature.move(direction)
    if ret and len(walkPatterns):
        walkerEvents[creature.clientId()] = reactor.callLater(creature.stepDuration(game.map.getTile(creature.position).getThing(0)), handleAutoWalking, creature, walkPatterns)
    else:
        del walkerEvents[creature.clientId()]
        
        
# Spectator list
def getSpectators(pos):
    # At the moment, we only do one floor
    players = []
    for x in xrange(pos[0]-10, pos[0]+10):
        for y in xrange(pos[1]-8, pos[1]+8):
            try:
                for creature in game.map.knownMap[x][y][7].creatures():
                    # TODO: Check for player
                    if creature.creatureType == 0:
                        players.append(creature.client)
            except:
                pass # Tile isn't loaded

    return players
    
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
# Last order of buisness, the script system
import game.scriptsystem
from data.scripts import *