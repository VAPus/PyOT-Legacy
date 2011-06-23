# This act as the core event system
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import deferLater
from twisted.internet import reactor
from collections import deque

walkerEvents = {}

# First order of buisness, the autoWalker
def autoWalkCreature(creature, walkPatterns):
    if creature.clientId() in walkerEvents: # The walker locks
        walkerEvents[creature.clientId()].cancel()
        #creature.cancelMove(creature.direction)
        
    walkerEvents[creature.clientId()] = reactor.callLater(creature.stepDuration(), handleAutoWalking, creature, walkPatterns)
    
def handleAutoWalking(creature, walkPatterns):
    direction = walkPatterns.popleft()
    ret = creature.move(direction)
    if ret and len(walkPatterns):
        walkerEvents[creature.clientId()] = reactor.callLater(creature.stepDuration(), handleAutoWalking, creature, walkPatterns)
    else:
        del walkerEvents[creature.clientId()]
        
        

# Last order of buisness, the script system
import core.game.scriptsystem
from data.scripts import *