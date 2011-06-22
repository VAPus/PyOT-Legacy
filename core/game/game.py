# This act as the core event system
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import deferLater
from twisted.internet import reactor
from collections import deque

# First order of buisness, the autoWalker
def autoWalkCreature(creature, walkPatterns):
    reactor.callLater(creature.stepDuration(), handleAutoWalking, creature, walkPatterns)

def handleAutoWalking(creature, walkPatterns):
    if not creature.inAutoWalk:
        return
    direction = walkPatterns.popleft()
    ret = creature.move(direction)
    if ret and creature.inAutoWalk and len(walkPatterns):
        reactor.callLater(creature.stepDuration(), handleAutoWalking, creature, walkPatterns)
    else:
        creature.inAutoWalk = False