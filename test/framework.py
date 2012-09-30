from twisted.internet import reactor, protocol
import pytest
import time
from twisted.application import internet, service
import sys
import os
sys.path.insert(0, '.')
sys.path.insert(1, 'core')
sys.path.insert(2, '../core')
import config
import packet

from twisted.trial import unittest
from twisted.test import proto_helpers
from service.gameserver import GameFactory

import game.engine
class Client(proto_helpers.StringTransport):
    def sendPacket(self, format, *argc):
        import packet
        import otcrypto
        from struct import pack
        from zlib import adler32
        
        packet = packet.TibiaPacket()
        i = 0
        for c in format:
            if c == "b":
                packet.uint8(argc[i])
            elif c == "h":
                packet.uint16(argc[i])
            elif c == "i":
                packet.uint32(argc[i])
            elif c == "q":
                packet.uin64(argc[i])
            elif c == "P":
                packet.uint16(argc[i].x)
                packet.uint16(argc[i].y)
                packet.uint8(argc[i].z)
            i += 1
            
        

        if self.client.xtea:
            data = otcrypto.encryptXTEA(data, self.client.xtea)
            data = pack("<H", len(packet.data))+packet.data
        else:
            data = packet.data
        self.client._packet = packet
        self.client._data = pack("<HI", len(data)+4, adler32(data) & 0xffffffff)+data
        self.client.dataReceived(self.client._data)
                

class FrameworkTest(unittest.TestCase):
    def setUp(self):
        self.initializeEngine()
        self.initializeClient()
        
    def initializeClient(self):
        self.tr = Client()
        self.client = self.server.buildProtocol(self.tr)
        self.tr.client = self.client
        self.client.makeConnection(self.tr)
        
    def initializeEngine(self):
        startTime = time.time()

        # Game Server
        self.server = GameFactory()
        gameServer = internet.TCPServer(config.gamePort, self.server, interface=config.gameInterface)
        # Load the core stuff!
        # Note, we use 0 here so we don't begin to load stuff before the reactor is free to do so, SQL require it, and anyway the logs will get fucked up a bit if we don't
        reactor.callLater(0, game.engine.loader, startTime)
