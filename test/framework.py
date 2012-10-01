from twisted.internet import reactor,protocol,defer
import time
from twisted.application import internet, service
import sys
import os
sys.path.insert(0, '.')
sys.path.insert(0, '..')
sys.path.insert(1, 'core')
sys.path.insert(2, '../core')
import config
import packet
from twisted.trial import unittest
from twisted.test import proto_helpers
from service.gameserver import GameFactory
from twisted.python import log
import game.engine
import __builtin__
__builtin__.IS_IN_TEST = True

SERVER = None
TEST_PROTOCOL = 963

class Client(proto_helpers.StringTransport):
    def sendPacket(self, format, *argc, **kwargs):
        import packet as p
        import otcrypto
        from struct import pack
        from zlib import adler32
        
        packet = p.TibiaPacket()
        i = 0
        for c in format:
            if c == "b":
                packet.uint8(argc[i])
            elif c == "h":
                packet.uint16(argc[i])
            elif c == "i":
                packet.uint32(argc[i])
            elif c == "q":
                packet.uint64(argc[i])
            elif c == "P":
                packet.uint16(argc[i].x)
                packet.uint16(argc[i].y)
                packet.uint8(argc[i].z)
            elif c == "s":
                packet.string(argc[i])

            i += 1
            
        

        if self.client.xtea:
            data = otcrypto.encryptXTEA(data, self.client.xtea)
            data = pack("<H", len(packet.data))+packet.data
        else:
            data = packet.data
        self.client._packet = packet
        self.client._data = pack("<HI", len(data)+4, adler32(data) & 0xffffffff)+data
        if kwargs:
            return p.TibiaPacketReader(packet.data)
        else:
            self.client.dataReceived(self.client._data)
                
    def write(self, data):
        # From server. Never use directly on the test side!
        self._data = data
        self._packet = packet.TibiaPacketReader(data)
        self._packet.pos += 8
        
        proto_helpers.StringTransport.write(self, data)
        
class FrameworkTest(unittest.TestCase):
    def setUp(self):
        d = self.initializeEngine()
        self.initializeClient()
        self.addCleanup(self.clear)
        return d
        
    def initializeClient(self):
        self.tr = Client()
        self.client = self.server.buildProtocol(self.tr)
        self.tr.client = self.client
        self.client.makeConnection(self.tr)
    
    def clear(self):
        for call in reactor.getDelayedCalls():
            try:
                call.cancel()
            except:
                pass
            
    def initializeEngine(self):
        global SERVER
        if not SERVER:
            startTime = time.time()

            # Game Server
            SERVER = GameFactory()
            gameServer = internet.TCPServer(config.gamePort, SERVER, interface=config.gameInterface)
            # Load the core stuff!
            # Note, we use 0 here so we don't begin to load stuff before the reactor is free to do so, SQL require it, and anyway the logs will get fucked up a bit if we don't
            self.server = SERVER
            return game.engine.loader(startTime)
        self.server = SERVER

class FrameworkTestGame(FrameworkTest):
    def setUp(self):
        self.player = None
        d = defer.maybeDeferred(FrameworkTest.setUp, self) 
        d.addCallback(self.setupPlayer)
        d.addCallback(self.fixConnection)        

        return d

    def clear(self):
        # Despawn.
        self.player.despawn()
        # Force remove.
        del game.player.allPlayers[self.player.name()]
        del game.creature.allCreatures[self.player.cid]

        self.setupPlayer()

    def setupPlayer(self):
        # Data must be valid, just random.
        data = {"id": 0, "name": "__TEST__", "world_id": 0, "group_id": 6, "account_id": 0, "vocation": 6, "health": 100, "mana": 100, "soul": 100, "manaspent": 1000, "experience": 5000, "posx": 1000, "posy": 1000, "posz": 7, "instanceId": 0, "sex": 0, "looktype": 100, "lookhead": 100, "lookbody": 100, "looklegs": 100, "lookfeet": 100, "lookaddons": 0, "lookmount": 100, "town_id": 1, "skull": 0, "stamina": 0, "storage": "", "inventory": "", "depot": "", "conditions": "", "skills": {SKILL_FIST: 10, SKILL_SWORD: 10, SKILL_CLUB: 10, SKILL_AXE: 10, SKILL_DISTANCE: 10, SKILL_SHIELD: 10, SKILL_FISH: 10}, "skill_tries": {SKILL_FIST: 0, SKILL_SWORD: 0, SKILL_CLUB: 0, SKILL_AXE: 0, SKILL_DISTANCE: 0, SKILL_SHIELD: 0, SKILL_FISH: 0}, "language":"en_EN", "guild_id":0, "guild_rank":0, "balance":0}

        # Add player as if he was online.
        game.player.allPlayers[data['name']] = game.player.Player(self.client, data)
        self.player = game.player.allPlayer[data['name']]

        # Disable saving.
        self.player.doSave = False

        # Add him to the position.
        tile = getTile(self.player.position)
        tile.placeCreature(self.player)

        # Game server does this.
        self.client.packet = self.player.packet

        # Note, we do not send firstLoginPacket, or even packet for our spawning. Thats for a test to do.

    def fixConnection(self):
        # Imagine we already sent the login packet. And all is well.
        self.client.gotFirst = True
        self.client.player = self.player
        self.client.ready = True
        self.client.version = TEST_PROTOCOL
        self.client.protocol = game.protocol.getProtocol(TEST_PROTOCOL)
