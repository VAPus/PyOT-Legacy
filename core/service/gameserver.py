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
import core.game.scriptsystem
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
        placeCreature(self.player, self.player.position)
        
        self.player.sendFirstPacket()
        
        # Call the login script
        core.game.scriptsystem.get("login").run(self.player)
        
        
    def onPacket(self, packet):
        packet.data = core.otcrypto.decryptXTEA(packet.getData(), self.xtea)
        packet.pos = 0
        packet.data = packet.data[2:2+packet.uint16()]
        packet.pos = 0
        
        packetType = packet.uint8()
        
        if packetType is 0x14: # Logout
            self.transport.loseConnection()
            
        elif packetType is 0x1E: # Keep alive
            self.player.pong()
            
        elif packetType is 0xA0: # Set modes
            self.player.setModes(packet.uint8(), packet.uint8(), packet.uint8())
            
        elif packetType in (0x6F, 0x70, 0x71, 0x72): # Turn packages
            self.player.turn(packetType - 0x6F)
            
        elif packetType is 0x64: # movement with multiple steps
            self.player.handleAutoWalk(packet)
    
        elif packetType is 0x69: # Stop autowalking
            self.player.stopAutoWalk()
            
        elif packetType in (0x65, 0x66, 0x67, 0x68): # Movement
            self.player.move(packetType - 0x65)
        
        elif packetType is 0x96: # Say
            self.player.handleSay(packet)
            
        elif packetType is 0x78: # Throw/move item
            self.player.handleMoveItem(packet)
        
        elif packetType is 0x85: # Rotate item
            self.player.handleRotateItem(packet)
            
        elif packetType is 0x8C:
            self.player.handleLookAt(packet)
        else:
            log.msg("Unhandled packet (type = {0}, length: {1}, content = {2})".format(hex(packetType), len(packet.data), ' '.join( map(str, map(hex, map(ord, packet.getData())))) ))
            #self.transport.loseConnection()

    def onConnectionLost(self):
        core.game.scriptsystem.get("logout").run(self.player)
        
class GameFactory(core.protocolbase.TibiaFactory):
    protocol = GameProtocol

class GameService(core.protocolbase.TibiaService):
    pass
