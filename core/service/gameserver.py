import sys
import protocolbase
import game.protocol
from collections import deque
from twisted.internet.defer import inlineCallbacks
from twisted.python import log
import config
import hashlib
if sys.subversion[0] != 'PyPy':
    try:
        import otcrypto
    except:
        import otcrypto_python as otcrypto
else:
    import otcrypto_python as otcrypto
import game.scriptsystem
from packet import TibiaPacket
import sql
import game.player
from game.map import getTile,removeCreature, Position
from game.engine import updateTile
import struct
import time

waitingListIps = deque()
lastChecks = {}
class GameProtocol(protocolbase.TibiaProtocol):
    connections = 0
    __slots__ = 'player', 'protocol', 'ready'

    def onInit(self):
        self.player = None
        self.protocol = None
        self.ready = False
        self.version = 0
        
    def onConnect(self):
        pkg = TibiaPacket()
        pkg.uint8(0x1F)
        pkg.uint16(0xFFFF) # Used for?
        pkg.uint16(0x00)
        pkg.uint8(0xFF) # Used for?
        pkg.send(self)

    def exitWithError(self, message):
        packet = TibiaPacket(0x14)
        packet.string(message) # Error message
        packet.send(self)
        self.loseConnection()

    def exitWaitingList(self, message, slot):
        packet = TibiaPacket(0x16)
        packet.string(message) # Error message
        packet.uint8(15 + (2 * slot))
        packet.send(self)
        self.loseConnection()
        
    @inlineCallbacks
    def onFirstPacket(self, packet):
        packetType = packet.uint8()

        if packetType and not self.ready:
            packet.pos += 2 # OS 0x00 and 0x01
            #packet.uint16() 
            version = packet.uint16() # Version int
            self.protocol = game.protocol.getProtocol(version)
            self.version = version
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

            ip = self.transport.getPeer().host
            if config.gameMaxConnections <= (self.connections + len(waitingListIps)):
                if ip in waitingListIps:
                    i = waitingListIps.index(ip) + 1
                    lastChecks[ip] = time.time()
                    # Note: Everyone below this threshhold might connect. So even if your #1 on the list and there is two free slots, you can be unlucky and don't get them.
                    if i + self.connections > config.gameMaxConnections:
                        self.exitWaitingList("Too many players online. You are at place %d on the waiting list." % i, i) 
                        return
                else:
                    waitingListIps.append(ip)
                    lastChecks[ip] = time.time()
                    self.exitWaitingList("Too many players online. You are at place %d on the waiting list." % len(waitingListIps), len(waitingListIps)) 
                    return
            self.connections += 1
            try:
                waitingListIps.remove(ip)
                del lastChecks[ip]
            except:
                pass
            
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

            if (not username and not config.anyAccountWillDo) or not characterName:
                self.exitWithError("Could not get your account name, or character name")
                return

            packet.pos += 6 # I don't know what this is

            # Our funny way of doing async SQL
            account = yield sql.conn.runQuery("SELECT `id` FROM `accounts` WHERE `name` = %s AND `password` = %s", (username, hashlib.sha1(password).hexdigest()))

            if not account:
                account = game.scriptsystem.get("loginAccountFailed").runSync(None, client=self, username=username, password=password)
                if not account or account == True:
                    self.exitWithError("Invalid username or password")

            character = yield sql.conn.runQuery("SELECT `id`,`name`,`world_id`,`group_id`,`account_id`,`vocation`,`health`,`mana`,`soul`,`manaspent`,`experience`,`posx`,`posy`,`posz`,`direction`,`sex`,`looktype`,`lookhead`,`lookbody`,`looklegs`,`lookfeet`,`lookaddons`,`lookmount`,`town_id`,`skull`,`stamina`, `storage`, `skills`, `inventory`, `depot`, `conditions` FROM `players` WHERE account_id = %s AND `name` = %s", (account[0][0], characterName))

            if not character:
                character = game.scriptsystem.get("loginCharacterFailed").runSync(None, client=self, account=account, name=characterName)
                if not character or character == True:
                    self.exitWithError("Character can't be loaded")
                    return
            if gamemaster and character[0][3] < 3:
                self.exitWithError("You are not gamemaster! Turn off gamemaster mode in your IP changer.")
                return

            # If we "made" a new character in a script, character = the player.
            player = None
            if isinstance(character, game.player.Player):
                player = character
                game.player.allPlayers[player.name()] = player
            elif character[0][1] in game.player.allPlayers:
                player = game.player.allPlayers[character[0][1]]
                if player.client:
                    self.exitWithError("This character is already logged in!")
                    return
                sql.runOperation("UPDATE `players` SET `lastlogin` = %s WHERE `id` = %s", (int(time.time()), character[0][0]))
            if player:    
                self.player = player
                if self.player.data["health"] < 1:
                    self.player.onSpawn()
                self.player.client = self
                tile = getTile(self.player.position)
                tile.placeCreature(self.player)
                # Send update tile to refresh all players. We use refresh because it fixes the order of things as well.
                updateTile(self.player.position, tile)
                
            else:
                # Bulld the dict since we disabled automaticly doing this. Here we cast Decimal objects to int aswell (no longer automaticly either)
                cd = character[0]
                cd = {"id": int(cd[0]), "name": cd[1], "world_id": int(cd[2]), "group_id": int(cd[3]), "account_id": int(cd[4]), "vocation": int(cd[5]), "health": int(cd[6]), "mana": int(cd[7]), "soul": int(cd[8]), "manaspent": int(cd[9]), "experience": int(cd[10]), "posx": cd[11], "posy": cd[12], "posz": cd[13], "direction": cd[14], "sex": cd[15], "looktype": cd[16], "lookhead": cd[17], "lookbody": cd[18], "looklegs": cd[19], "lookfeet": cd[20], "lookaddons": cd[21], "lookmount": cd[22], "town_id": cd[23], "skull": cd[24], "stamina": cd[25], "storage": cd[26], "skills": cd[27], "inventory": cd[28], "depot": cd[29], "conditions": cd[30]}

                game.player.allPlayers[cd['name']] = game.player.Player(self, cd)
                self.player = game.player.allPlayers[cd['name']]
                if self.player.data["health"]:
                    try:
                        tile = getTile(self.player.position)
                        tile.placeCreature(self.player)
                        # Send update tile to refresh all players. We use refresh because it fixes the order of things as well.
                        updateTile(self.player.position, tile)
                        
                    except AttributeError:
                        import data.map.info
                        self.player.position = Position(*data.map.info.towns[1][1])
                        tile = getTile(self.player.position)
                        tile.placeCreature(self.player)
                        # Send update tile to refresh all players. We use refresh because it fixes the order of things as well.
                        updateTile(self.player.position, tile)
                        
                    # Update last login
                    sql.runOperation("UPDATE `players` SET `lastlogin` = %s WHERE `id` = %s", (int(time.time()), character[0][0]))

            self.player.sendFirstPacket()
            self.ready = True # We can now accept other packages

            # Call the login script
            game.scriptsystem.get("login").runSync(self.player)
            
            # If we got a waiting list, now is a good time to vertify the list
            if lastChecks:
                checkTime = time.time()
                for entry in lastChecks:
                    if checkTime - lastChecks[entry] > 3600:
                        waitingListIps.remove(entry)
                        del lastChecks[entry]
                        
        elif packetType == 0x00 and self.transport.getPeer().host in config.executeProtocolIps:
            t = TibiaPacket()
            if not config.executeProtocolAuthKeys:
                self.ready = 2
                    
            try:
                while True:
                    op = packet.string()
                    print op
                    if op == "CALL" and self.ready:
                        result = yield game.engine.executeCode(packet.string())
                            
                        t.string(result)
                    elif op == "AUTH":
                        print "auth"
                        if packet.string() in config.executeProtocolAuthKeys:
                            t.string("True")
                            self.ready = 2
                        else:
                            t.string("False")
            except struct.error:
                pass # End of the line
            t.send(self)    

    def _executeProtocol(self, packet):
        t = TibiaPacket()
        if not config.executeProtocolAuthKeys:
            self.ready = 2
                
        try:
            while True:
                op = packet.string()
                print op
                if op == "CALL" and self.ready:
                    result = yield game.engine.executeCode(packet.string())
                        
                    t.string(result)
                elif op == "AUTH":
                    print "auth"
                    if packet.string() in config.executeProtocolAuthKeys:
                        t.string("True")
                        self.ready = 2
                    else:
                        t.string("False")
        except struct.error:
            pass # End of the line
        t.send(self)    
        
    def onPacket(self, packet):
        print "?", self.ready
        if self.ready == 2:
            a = packet.uint8()
            print "=", a
            t = TibiaPacket()
            if not config.executeProtocolAuthKeys:
                self.ready = 2
                    
            try:
                while True:
                    op = packet.string()
                    print op
                    if op == "CALL" and self.ready:
                        result = yield game.engine.executeCode(packet.string())
                            
                        t.string(result)
                    elif op == "AUTH":
                        print "auth"
                        if packet.string() in config.executeProtocolAuthKeys:
                            t.string("True")
                            self.ready = 2
                        else:
                            t.string("False")
            except struct.error:
                pass # End of the line
            t.send(self)  
        else:    
            packet.data = otcrypto.decryptXTEA(packet.getData(), self.xtea)
            packet.pos = 0
            packet.data = packet.data[2:2+packet.uint16()]
            packet.pos = 0

            self.protocol.handle(self.player, packet)


    def onConnectionLost(self):
        if self.player:
            print "Lost connection on, ", self.player.position
            self.player.client = None
            self.player.knownCreatures = set()
            self.player.knownBy = set()
            for x in game.player.allPlayers.values():
                if x.client and self.player.data["id"] in x.getVips():
                    stream = x.packet()
                    stream.vipLogout(self.player.data["id"])
                    stream.send(x.client)
            
            game.scriptsystem.get("logout").runSync(self.player)
            self.player.despawn()
            
    def packet(self, *args):
        return self.protocol.Packet(*args)

class GameFactory(protocolbase.TibiaFactory):
    __slots__ = ()
    protocol = GameProtocol
