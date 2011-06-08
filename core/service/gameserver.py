import core.protocolbase

from twisted.internet.defer import inlineCallbacks, deferredGenerator, waitForDeferred
from twisted.python import log
from core.packet import TibiaPacket
import core.sql
import core.otcrypto
import config
import hashlib
from core.game.player import TibiaPlayer
from core.game.map import placeCreature

class GameProtocol(core.protocolbase.TibiaProtocol):

    def onInit(self):
        self.player = None

    def onConnect(self):
        pkg = TibiaPacket()
        pkg.uint8(0x1F)
        pkg.uint16(0xFFFF)
        pkg.uint16(0x00)
        pkg.uint8(0xFF)
        pkg.send(self)

    @deferredGenerator
    def onFirstPacket(self, packet):
        packet.pos += 1 # Packet Type, we don't really care about it in the first packet
        packet.uint16() # OS 0x00 and 0x01
        version = packet.uint16() # Version int
         
        if (packet.length - packet.pos) is 128: # RSA 1024 is always 128
            packet.data = core.otcrypto.decryptRSA(packet.getData()) # NOTICE: Should we do it in a seperate thread?
            packet.pos = 0 # Reset position

        else:
            log.msg("RSA, length != 128 (it's %d)" % (packet.length - packet.pos))
            self.transport.loseConnection()
            return

        if not packet.data or packet.uint8(): # RSA needs to decrypt just fine, so we get the data, and the first byte should be 0
            log.msg("RSA, first char != 0")
            self.transport.loseConnection()
            return

        # Set the XTEA key
        self.xtea = (packet.uint32(), packet.uint32(), packet.uint32(), packet.uint32())

        # "Gamemaster" mode?
        gamemaster = packet.uint8()

        # Check if version is correct
        if version > config.versionMax or version < config.versionMin:
            self.exitWithError(config.versionError)
            return

        # Check if there is a username (and a password)
        username = packet.string()
        characterName = packet.string()
        password = packet.string()

        if not username or not characterName:
            self.exitWithError("Could not get your account name, or character name")
            return

        packet.pos += 6 # I don't know what this is

        # Initialize the packet to send
        pkg = TibiaPacket()

        # Our funny way of doing async SQL
        d = waitForDeferred(core.sql.conn.runQuery("SELECT `id` FROM `accounts` WHERE `name` = %s AND `password` = %s", (username, hashlib.sha1(password).hexdigest())))

        yield d # Tell the core to come back to use once the query above is finished

        account = d.getResult()

        if not account:
            self.exitWithError("Invalid username or password")
            return

        d = waitForDeferred(core.sql.conn.runQuery("SELECT * FROM `players` WHERE account_id = %s", (account[0]['id'])))

        yield d # Tell the core to come back to use once the query above is finished

        character = d.getResult()

        if not character:
            self.exitWithError("Character can't be loaded")
            return

        if gamemaster and character["group"] < 3:
            self.exitWithError("You are not gamemaster! Turn off gamemaster mode in your IP changer.")
            return
        
        self.player = TibiaPlayer(self, character[0])
        placeCreature(self.player, self.position)

        self.player.sendFirstPacket()
        
    def onPacket(self, packet):
        log.msg("Unhandled packet (type = {0}, length: {1})".format(hex(packet.uint8()), len(packet.data)))
        #self.transport.loseConnection()
        
class GameFactory(core.protocolbase.TibiaFactory):
    protocol = GameProtocol

class GameService(core.protocolbase.TibiaService):
    pass
