import protocolbase
import game.protocol

from twisted.internet.defer import inlineCallbacks
from twisted.python import log
import config
import hashlib
import otcrypto
import game.scriptsystem
from packet import TibiaPacket
import sql
import game.player
from game.map import getTile,removeCreature
class GameProtocol(protocolbase.TibiaProtocol):
    __slots__ = 'player', 'protocol'
    
    def onInit(self):
        self.player = None
        self.protocol = None
    def onConnect(self):
        pkg = TibiaPacket()
        pkg.uint8(0x1F)
        pkg.uint16(random.randint(0, 0xFFFF))
        pkg.uint16(0x00)
        pkg.uint8(random.randint(0, 0xFF))
        pkg.send(self)

    def exitWithError(self, message, error = 0x14):
        packet = TibiaPacket()
        packet.uint8(error) # Error code
        packet.string(message) # Error message
        packet.send(self)
        self.loseConnection()
        
    @inlineCallbacks
    def onFirstPacket(self, packet):
        packet.pos += 3 # Packet Type, we don't really care about it in the first packet
        #packet.uint16() # OS 0x00 and 0x01
        version = packet.uint16() # Version int
        self.protocol = game.protocol.getProtocol(version)
        print "Client protocol version %d" % version
        
        if not self.protocol:
            log.msg("Trying to load a invalid protocol")
            self.transport.loseConnection()
            return
            
        if (len(packet.data) - packet.pos) == 128: # RSA 1024 is always 128
            packet.data = otcrypto.decryptRSA(packet.getData()) # NOTICE: Should we do it in a seperate thread?
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
        account = yield sql.conn.runQuery("SELECT `id` FROM `accounts` WHERE `name` = %s AND `password` = %s", (username, hashlib.sha1(password).hexdigest()))

        if not account:
            self.exitWithError("Invalid username or password")
            return

        character = yield sql.conn.runQuery("SELECT `id`,`name`,`world_id`,`group_id`,`account_id`,`vocation`,`health`,`mana`,`soul`,`manaspent`,`experience`,`posx`,`posy`,`posz`,`direction`,`sex`,`looktype`,`lookhead`,`lookbody`,`looklegs`,`lookfeet`,`lookaddons`,`lookmount`,`town_id`,`skull`,`stamina`, `storage`, `skills`, `inventory`, `depot` FROM `players` WHERE account_id = %s", (account[0]['id']))

        if not character:
            self.exitWithError("Character can't be loaded")
            return

        if gamemaster and character["group"] < 3:
            self.exitWithError("You are not gamemaster! Turn off gamemaster mode in your IP changer.")
            return
        
        if character[0]['name'] in game.player.allPlayers:
            self.player = game.player.allPlayers[character[0]['name']]
            if self.player.data["health"] < 1:
                self.player.onSpawn()
            self.player.client = self
            print self.player
            getTile(self.player.position).placeCreature(self.player)
        else:
            game.player.allPlayers[character[0]['name']] = game.player.Player(self, character[0])
            self.player = game.player.allPlayers[character[0]['name']]
            if self.player.data["health"]:
                try:
                    getTile(self.player.position).placeCreature(self.player)
                except AttributeError:
                    import data.map.info
                    self.player.position = data.map.info.towns[1][1]
                    getTile(self.player.position).placeCreature(self.player)
                
        self.player.sendFirstPacket()
                
        # Call the login script
        game.scriptsystem.get("login").run(self.player)
        
        
    def onPacket(self, packet):
        packet.data = otcrypto.decryptXTEA(packet.getData(), self.xtea)
        packet.pos = 0
        packet.data = packet.data[2:2+packet.uint16()]
        packet.pos = 0
        
        self.protocol.handle(self.player, packet)


    def onConnectionLost(self):
        if self.player:
            self.player.client = None
            self.player.knownCreatures = set()
            for x in game.player.allPlayersObject:
                if x.client and self.player.data["id"] in x.getVips():
                    stream = x.packet()
                    stream.vipLogout(self.player.data["id"])
                    stream.send(x.client)
            removeCreature(self.player, self.player.position)
            game.scriptsystem.get("logout").run(self.player)
        
    def packet(self, *args):
        return self.protocol.Packet(*args)
        
class GameFactory(protocolbase.TibiaFactory):
    __slots__ = ()
    protocol = GameProtocol
