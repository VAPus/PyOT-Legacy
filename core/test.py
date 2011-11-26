from twisted.trial import unittest
import time
import sys
sys.path.insert(0, '.')
sys.path.insert(1, 'core')

import config

import game.engine
from twisted.internet import reactor, threads, defer

startTime = time.time()

# Turn off looper call.
game.engine.looper = lambda x,y: x()

game.engine.loader(startTime)

# Clear reactor
for i in reactor.getDelayedCalls():
    i.cancel()

#### The tests ####

### Packet ###
class Packet(unittest.TestCase):
    def test_uint8(self):
        import packet
        p = packet.TibiaPacket()
        p.uint8(255)
        p.uint8(0)

        self.assertEqual(ord(p.bytes[0]), 255)
        self.assertEqual(ord(p.bytes[1]), 0)

### Engine ###
class GameEngine(unittest.TestCase):
    def test_getSpectators(self):
        # Without players
        self.assertEqual(game.engine.getSpectators([100,100,7]), set())

        # TODO: With players

    def test_getPlayers(self):
        # Without players
        self.assertEqual(game.engine.getPlayers([100,100,7]), set())

        # TODO: With players

    def test_getCreatures(self):
        # Without players
        self.assertEqual(game.engine.getCreatures([100,100,7]), set())

        # TODO: With map sectors / creatures loaded
        
    def test_getSpectators_tuple(self):
        # Without players
        self.assertEqual(game.engine.getSpectators((100,100,7)), set())

        # TODO: With players

    def test_getPlayers_tuple(self):
        # Without players
        self.assertEqual(game.engine.getPlayers((100,100,7)), set())

        # TODO: With players

    def test_getCreatures_tuple(self):
        # Without players
        self.assertEqual(game.engine.getCreatures((100,100,7)), set())

        # TODO: With map sectors / creatures loaded