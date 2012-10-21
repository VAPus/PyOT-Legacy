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
import random
import string
from twisted.trial import unittest
from twisted.test import proto_helpers
from service.gameserver import GameFactory
from twisted.python import log
import game.engine
import game.loading
import __builtin__
__builtin__.IS_IN_TEST = True

# Some config.
SERVER = None
TEST_PROTOCOL = 963
TEST_PLAYER_ID = random.randint(10, 0x7FFFFFFF)
TEST_PLAYER_NAME = "__TEST__"

__builtin__.PYOT_RUN_SQLOPERATIONS = False
# Async sleeper.
def asyncWait():
    d = defer.Deferred()
    reactor.callLater(0.01, d.callback, True) # a number >= 10ms will do. It's 5-6 sql queries.
    return d

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
        self.client._packets.append(packet)
        self.client._data = pack("<HI", len(data)+4, adler32(data) & 0xffffffff)+data
        if kwargs:
            return p.TibiaPacketReader(packet.data)
        else:
            self.client.dataReceived(self.client._data)
                
    def write(self, data):
        # From server. Never use directly on the test side!
        self._data = data
        self._packets.append(packet.TibiaPacketReader(data))
        self._packets[-1].pos += 8
        
        proto_helpers.StringTransport.write(self, data)
        
class FrameworkTest(unittest.TestCase):
    def setUp(self):
        self._overrideConfig = {}
        d = self.initializeEngine()
        self.initializeClient()
        self.addCleanup(self.clearDelayedCalls)
        self.addCleanup(self.clear)
        self.addCleanup(self.restoreConfig)
        
        self.init()
        
        return d
    
    def init(self):
        pass
    
    def initializeClient(self):
        self.tr = Client()
        self.tr._packets = []
        self.client = self.server.buildProtocol(self.tr)
        self.client._packets = []
        self.tr.client = self.client
        self.client.makeConnection(self.tr)
    
    def clear(self):
        # Clear all players.
        for player in game.player.allPlayers.values():
            self.destroyPlayer(player)
            
    def overrideConfig(self, name, value):
        self._overrideConfig[name] = getattr(config, name)
        
        setattr(config, name, value)
        
    def restoreConfig(self, key=None):
        if key:
            setattr(config, key, self._overrideConfig[key])
        else:
            for key in self._overrideConfig:
                setattr(config, key, self._overrideConfig[key])
            
    def clearDelayedCalls(self):
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
            d = game.loading.loader(startTime)
            
            # Kinda necessary if any scripts use load events from say SQL. 
            d.addCallback(lambda x: asyncWait())
            return d
        self.server = SERVER
        
    def destroyPlayer(self, player):
        # Despawn.
        player.despawn()
        # Force remove.
        del game.player.allPlayers[player.name()]
        del game.creature.allCreatures[player.cid]
        
        try:
            self._trackPlayers.remove(player)
        except:
            pass
        
class FrameworkTestGame(FrameworkTest):
    def setUp(self):
        self.player = None
        self._trackPlayers = []
        d = defer.maybeDeferred(FrameworkTest.setUp, self) 
        d.addCallback(lambda x: self.setupPlayer(TEST_PLAYER_ID, TEST_PLAYER_NAME, True))
        d.addCallback(lambda x: self.fixConnection)        

        return d

    def clear(self, recreate = False):
        if self.player: # Tests might clear us already. Etc to test clearing!
            self.destroyPlayer(self.player)

        for player in self._trackPlayers[:]:
            self.destroyPlayer(player)
        
        # Clear deathlists.
        deathlist.byKiller = {}
        deathlist.byVictim = {}
        deathlist.loadedDeathIds = set()
        
        if recreate:
            self.setupPlayer(TEST_PLAYER_ID, TEST_PLAYER_NAME, True)
            
        # Cleanup.
        tile = getTile(Position(1000, 1000, 7))
        for thing in tile.things[:]:
            if isinstance(thing, Item) and not thing.fromMap:
                tile.removeItem(thing)
                
        # Cleanup.
        tile = getTile(Position(1000, 1001, 7))
        for thing in tile.things[:]:
            if isinstance(thing, Item) and not thing.fromMap:
                tile.removeItem(thing)
                
        # Cleanup.
        tile = getTile(Position(1000, 999, 7))
        for thing in tile.things[:]:
            if isinstance(thing, Item) and not thing.fromMap:
                tile.removeItem(thing)
                
        # Clear instances.
        for instance in game.map.instances.copy():
            if instance != None:
                del game.map.instances[instance]
                # Might not be set if we never load anything.
                try:
                    del game.map.knownMap[instance]
                except:
                    pass

    def virtualPlayer(self, id, name):
        # Setup a virtual player.
        # No network abilities, or spawning or such.
        
        # Data must be valid, just random.
        data = {"id": id, "name": name, "world_id": 0, "group_id": 6, "account_id": 0, "vocation": 6, "health": 100, "mana": 100, "soul": 100, "manaspent": 10000, "experience": 5000, "posx": 1000, "posy": 1000, "posz": 7, "instanceId": None, "sex": 0, "looktype": 100, "lookhead": 100, "lookbody": 100, "looklegs": 100, "lookfeet": 100, "lookaddons": 0, "lookmount": 100, "town_id": 1, "skull": 0, "stamina": 100000, "storage": "", "inventory": "", "depot": "", "conditions": "", 'fist': 10, 'sword': 10, 'club': 10, 'axe': 10, 'distance': 10, 'shield': 10, 'fishing': 10, 'fist_tries': 0, 'sword_tries': 0, 'club_tries': 0, 'axe_tries': 0, 'distance_tries': 0, 'shield_tries': 0, 'fishing_tries': 0, "language":"en_EN", "guild_id":0, "guild_rank":0, "balance":0}

        # Add player as if he was online.
        player = game.player.Player(self.client, data)
        game.player.allPlayers[name] = player

        # Disable saving.
        player.doSave = False
        
        return player
        
    def setupPlayer(self, id=None, name=None, clientPlayer = False):
        if id is None:
            id = random.randint(1, 0x7FFFFFFF)
        if name is None:
            name = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(10))

        # A virtual player with network abilities and spawning.
        player = self.virtualPlayer(id, name)
        
        # Add him to the position.
        tile = getTile(player.position)
        tile.placeCreature(player)

        # Game server does this.
        if clientPlayer:
            self.player = player
            self.client.packet = player.packet

        # Track it.
        self._trackPlayers.append(player)
        
        # Note, we do not send firstLoginPacket, or even packet for our spawning. Thats for a test to do.
        
        return player
        
    def fixConnection(self):
        # Imagine we already sent the login packet. And all is well.
        self.client.gotFirst = True
        self.client.player = self.player
        self.client.ready = True
        self.client.version = TEST_PROTOCOL
        self.client.protocol = game.protocol.getProtocol(TEST_PROTOCOL)
