from twisted.internet import reactor,protocol
import pytest
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
import thread
from twisted.trial import unittest
from twisted.test import proto_helpers
from service.gameserver import GameFactory
from twisted.python import log
#log.startLogging(sys.stdout)
import game.engine
import __builtin__
__builtin__.IS_IN_TEST = True
SERVER = None
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