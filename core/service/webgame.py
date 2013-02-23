from twisted.internet.protocol import Protocol, Factory
import game.protocol
from core.packet import WGPacketReader, WGPacket
from twisted.internet.defer import inlineCallbacks

class ClientProtocol(Protocol):
    # Unlike Tibia, these are static.
    protocol = game.protocol.getProtocol("web")
    packet = game.protocol.getProtocol("web").Packet
    version = 1

    def __init__(self):
        self.player = None
        self.firstPacket = False
        self.ready = False
        
    def connectionMade(self):
        try:
            # Enable TCP_NO_DELAY
            self.transport.setTcpNoDelay(True)
        except:
            # May not always work.
            pass

    def exitWithError(self, message):
        pkg = self.protocol.Packet()
        pkg.exitWithError(message)
        pkg.send(self)
        self.transport.close()

    @inlineCallbacks
    def dataReceived(self, data):
        packet = WGPacketReader(data)
        pkg = self.protocol.Packet()
                
        if not self.firstPacket:
            # Then we got username and password.
            username = packet.string()
            print username
            password = packet.string()
            if not username and not config.anyAccountWillDo:
                self.exitWithError("Username cannot be blank.")
                return
                
            if username:
                # Our funny way of doing async SQL
                account = yield sql.runQuery("SELECT `id`, `premdays`, `language` FROM `accounts` WHERE `name` = %s AND `password` = SHA1(CONCAT(`salt`, %s))", (username, password))

                if account:
                    # Ban check.
                    if game.ban.accountIsBanned(account[0]['id']):
                        self.exitWithError("Your account is banned.\n %s" % game.ban.banAccounts[account[0]['id']].message())
                        return 
                    
                    if not account[0]['language']:
                        language = config.defaultLanguage
                    else:
                        language = account[0]['language']
                    characters = yield sql.runQuery("SELECT `name`,`world_id` FROM `players` WHERE account_id = %s", (account[0]['id']))
         
            if not username or not account:
                if config.anyAccountWillDo:
                    account = ((0,0),)
                    characters = config.anyAccountPlayerMap
                else:
                    self.exitWithError("Invalid username or password")
                    return 
            
            game.scriptsystem.get("preSendLogin").runSync(None, client=self, characters=characters, account=account, username=username, password=password)
            self.firstPacket = True
            self.account = account[0]
            self.language = language
            pkg.characters(characters)
            pkg.send(self)
        elif not self.player:
            characterName = packet.string()
            print characterName
            print Position(999, 998, 7).getTile().things,  Position(999, 998, 7).getTile().ground
            if not characterName:
                self.exitWithError("Need character name.")
                return
                
            character = yield sql.runQuery("SELECT p.`id`,p.`name`,p.`world_id`,p.`group_id`,p.`account_id`,p.`vocation`,p.`health`,p.`mana`,p.`soul`,p.`manaspent`,p.`experience`,p.`posx`,p.`posy`,p.`posz`,p.`instanceId`,p.`sex`,p.`looktype`,p.`lookhead`,p.`lookbody`,p.`looklegs`,p.`lookfeet`,p.`lookaddons`,p.`lookmount`,p.`town_id`,p.`skull`,p.`stamina`, p.`storage`, p.`inventory`, p.`depot`, p.`conditions`, s.`fist`,s.`fist_tries`,s.`sword`,s.`sword_tries`,s.`club`,s.`club_tries`,s.`axe`,s.`axe_tries`,s.`distance`,s.`distance_tries`,s.`shield`,s.`shield_tries`,s.`fishing`, s.`fishing_tries`, g.`guild_id`, g.`guild_rank`, p.`balance` FROM `players` AS `p` LEFT JOIN player_skills AS `s` ON p.`id` = s.`player_id` LEFT JOIN player_guild AS `g` ON p.`id` = g.`player_id` WHERE p.account_id = %s AND p.`name` = %s AND p.`world_id` = %s", (self.account['id'], characterName, config.worldId))

            if not character:
                character = game.scriptsystem.get("loginCharacterFailed").runSync(None, client=self, account=self.account, name=characterName)
                if not character or character == True:
                    self.exitWithError("Character can't be loaded")
                    return
                
            character = character[0]

            # Ban check.
            if isinstance(character, game.player.Player):
                if game.ban.playerIsBanned(character):
                    self.exitWithError("Your player is banned.\n %s" % game.ban.banAccounts[character.data["id"]].message())
                    return 
            elif game.ban.playerIsBanned(character['id']):
                self.exitWithError("Your player is banned.\n %s" % game.ban.banAccounts[character['id']].message())
                return 
            
            # If we "made" a new character in a script, character = the player.
            player = None
            if isinstance(character, game.player.Player):
                player = character
                game.player.allPlayers[player.name()] = player
            elif character['name'] in game.player.allPlayers:
                player = game.player.allPlayers[character['name']]
                if player.client:
                    self.exitWithError("This character is already logged in!")
                    return
                sql.runOperation("UPDATE `players` SET `lastlogin` = %s, `online` = 1 WHERE `id` = %s", (int(time.time()), character['id']))
            if player:    
                self.player = player
                if self.player.data["health"] <= 0:
                    self.player.onSpawn()
                self.player.client = self
                tile = getTile(self.player.position)
                tile.placeCreature(self.player)
                # Send update tile to refresh all players. We use refresh because it fixes the order of things as well.
                updateTile(self.player.position, tile)
                
            else:
                yield deathlist.loadDeathList(character['id'])
                character["language"] = self.language
                game.player.allPlayers[character['name']] = game.player.Player(self, character)
                self.player = game.player.allPlayers[character['name']]
                if self.player.data["health"] <= 0:
                    self.player.onSpawn()

                try:
                    tile = getTile(self.player.position)
                    tile.placeCreature(self.player)
                    # Send update tile to refresh all players. We use refresh because it fixes the order of things as well.
                    updateTile(self.player.position, tile)
                        
                except AttributeError:
                    self.player.position = Position(*game.map.mapInfo.towns[1][1])
                    tile = getTile(self.player.position)
                    tile.placeCreature(self.player)
                    # Send update tile to refresh all players. We use refresh because it fixes the order of things as well.
                    updateTile(self.player.position, tile)
                        
                # Update last login
                sql.runOperation("UPDATE `players` SET `lastlogin` = %s WHERE `id` = %s", (int(time.time()), character['id']))

            self.packet = self.player.packet
            self.player.sendFirstPacket()
            self.ready = True # We can now accept other packages

            # Call the login script
            game.scriptsystem.get("login").runSync(self.player)
            
        else:
            # Pass on to handler.
            self.protocol.handle(self.player, packet)

    def onConnectionLost(self):
        if self.player:
            print "Lost connection on, ", self.player.position
            self.player.client = None

            if self.player.alive and not self.player.prepareLogout():
                logoutBlock = self.player.getCondition(CONDITION_INFIGHT)
                callLater(logoutBlock.length, self.onConnectionLost)
                return

            self.player.knownCreatures = set()
            self.player.knownBy = set()
            for x in game.player.allPlayers.values():
                if x.client and self.player.data["id"] in x.getVips():
                    stream = x.packet()
                    stream.vipLogout(self.player.data["id"])
                    stream.send(x.client)

            game.scriptsystem.get("logout").runSync(self.player)
            self.player.despawn()
            
class ClientFactory(Factory):
    protocol = ClientProtocol


