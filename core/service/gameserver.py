import protocolbase

from twisted.internet.defer import deferredGenerator, waitForDeferred
from twisted.python import log
import config
import hashlib
import otcrypto

class GameProtocol(protocolbase.TibiaProtocol):

    def onInit(self):
        self.player = None

    def onConnect(self):
        from packet import TibiaPacket
        pkg = TibiaPacket()
        pkg.uint8(0x1F)
        pkg.uint16(0xFFFF)
        pkg.uint16(0x00)
        pkg.uint8(0xFF)
        pkg.send(self)

    def exitWithError(self, message, error = 0x14):
        packet = TibiaPacket()
        packet.uint8(error) # Error code
        packet.string(message) # Error message
        packet.send(self)
        self.loseConnection()
        
    @deferredGenerator
    def onFirstPacket(self, packet):
        import sql
        import otcrypto
        
        from packet import TibiaPacket
        import game.player
        from game.map import getTile
        import game.scriptsystem
        
        packet.pos += 1 # Packet Type, we don't really care about it in the first packet
        packet.uint16() # OS 0x00 and 0x01
        version = packet.uint16() # Version int
         
        if (packet.length - packet.pos) == 128: # RSA 1024 is always 128
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
        d = waitForDeferred(sql.conn.runQuery("SELECT `id` FROM `accounts` WHERE `name` = %s AND `password` = %s", (username, hashlib.sha1(password).hexdigest())))

        yield d # Tell the core to come back to use once the query above is finished

        account = d.getResult()

        if not account:
            self.exitWithError("Invalid username or password")
            return

        d = waitForDeferred(sql.conn.runQuery("SELECT `id`,`name`,`world_id`,`group_id`,`account_id`,`vocation`,`health`,`mana`,`soul`,`manaspent`,`experience`,`posx`,`posy`,`posz`,`direction`,`sex`,`looktype`,`lookhead`,`lookbody`,`looklegs`,`lookfeet`,`lookaddons`,`lookmount`,`town_id`,`skull`,`stamina` FROM `players` WHERE account_id = %s", (account[0]['id'])))

        yield d # Tell the core to come back to use once the query above is finished

        character = d.getResult()

        if not character:
            self.exitWithError("Character can't be loaded")
            return

        if gamemaster and character["group"] < 3:
            self.exitWithError("You are not gamemaster! Turn off gamemaster mode in your IP changer.")
            return
        
        if character[0]['name'] in game.player.allPlayers:
            self.player = game.player.allPlayers[character[0]['name']]
            self.player.client = self
            if self.player.data["health"] < 1:
                self.player.onSpawn()
            
            
        else:
            game.player.allPlayers[character[0]['name']] = game.player.TibiaPlayer(self, character[0])
            self.player = game.player.allPlayers[character[0]['name']]
            self.player.client = self
            if self.player.data["health"]:
                try:
                    getTile(self.player.position).placeCreature(self.player)
                except:
                    print "%s is unspawnable, choosing a city" % str(self.player.position)
                    import data.map.info
                    import game.map
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
        
        packetType = packet.uint8()
        print hex(packetType)
        if packetType == 0x14 or self.player.data["health"] < 1: # Logout
            self.transport.loseConnection()
            
        elif packetType == 0x1E: # Keep alive
            self.player.pong()
            
        elif packetType == 0xA0: # Set modes
            self.player.setModes(packet.uint8(), packet.uint8(), packet.uint8())
            
        elif packetType in (0x6F, 0x70, 0x71, 0x72): # Turn packages
            self.player.turn(packetType - 0x6F)
            
        elif packetType == 0x64: # movement with multiple steps
            self.player.handleAutoWalk(packet)
    
        elif packetType == 0x69: # Stop autowalking
            self.player.stopAutoWalk()
            
        elif packetType in (0x65, 0x66, 0x67, 0x68): # Movement
            self.player.handleWalk(packetType - 0x65)
        
        elif packetType == 0x6A: # Northeast
            self.player.handleWalk(7)
            
        elif packetType == 0x6B: # Southeast
            self.player.handleWalk(5)

        elif packetType == 0x6C: # Northwest
            self.player.handleWalk(4)
            
        elif packetType == 0x6D: # Southwest
            self.player.handleWalk(6)
            
        elif packetType == 0x96: # Say
            self.player.handleSay(packet)
            
        elif packetType == 0x78: # Throw/move item
            self.player.handleMoveItem(packet)
        
        elif packetType == 0x82:
            self.player.handleUse(packet)

        elif packetType == 0x83:
            self.player.handleUseWith(packet)
            
        elif packetType == 0x85: # Rotate item
            self.player.handleRotateItem(packet)
            
        elif packetType == 0x87: # Close container
            self.player.closeContainerId(packet.uint8())
            
        elif packetType == 0x88: # Arrow up container
            self.player.arrowUpContainer(packet.uint8())
            
        elif packetType == 0x97: # Request channels
            self.player.openChannels()

        elif packetType == 0x98: # Open channel
            self.player.openChannel(packet.uint16())
            
        elif packetType == 0x99: # Close channel
            self.player.closeChannel(packet.uint16())
            
        elif packetType == 0x8C: # Look at
            self.player.handleLookAt(packet)
        
        elif packetType == 0xA1: # Attack
            self.player.handleAttack(packet)

        elif packetType == 0xA2: # Attack
            self.player.handleFollow(packet)
            
        elif packetType == 0xD2: # Request outfit
            self.player.outfitWindow()
            
        elif packetType == 0xD3: # Set outfit
            self.player.handleSetOutfit(packet)
        
        elif packetType == 0xD4: # Set mount status
            self.player.handleSetMounted(packet)
            
        elif packetType == 0xBE: # Stop action
            self.player.stopAction()
            
        else:
            log.msg("Unhandled packet (type = {0}, length: {1}, content = {2})".format(hex(packetType), len(packet.data), ' '.join( map(str, map(hex, map(ord, packet.getData())))) ))
            #self.transport.loseConnection()

    def onConnectionLost(self):
        if self.player:
            log.msg("Lost connection to player")
            import game.scriptsystem
            from game.map import removeCreature
            self.player.client = None
            removeCreature(self.player, self.player.position)
            game.scriptsystem.get("logout").run(self.player)
        
class GameFactory(protocolbase.TibiaFactory):
    protocol = GameProtocol

class GameService(protocolbase.TibiaService):
    pass
