import protocolbase
from twisted.internet.defer import inlineCallbacks
from twisted.python import log
from packet import TibiaPacket
import os
import sql
import otcrypto
import config
import socket
import time
import cPickle

if os.path.exists('IP_CACHE') and os.path.getmtime('IP_CACHE') > time.time() - 2400:
    IPS = cPickle.load(open('IP_CACHE', 'rb'))
else:
    IPS = {}

class LoginProtocol(protocolbase.TibiaProtocol):
    @inlineCallbacks
    def onFirstPacket(self, packet):
        global IPS
        try:
            packet.uint8()
        except:
            return

        packet.pos += 2
        #packet.uint16() # OS 0x00 and 0x01
        version = packet.uint16() # Version int

        packet.pos += 12 # Checksum for files

        if (len(packet.data) - packet.pos) == 128: # RSA 1024 is always 128
            packet.data = otcrypto.decryptRSA(packet.getData()) # NOTICE: We don't have to yield this since we are already in a seperate thread?
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
        k = (packet.uint32(), packet.uint32(), packet.uint32(), packet.uint32())
        sum = 0
        a, b = [], []
        for x in xrange(32):
            a.append(sum + k[sum & 3] & 0xffffffff)
            sum = (sum + 0x9E3779B9) & 0xffffffff
            b.append(sum + k[sum>>11 & 3] & 0xffffffff)
                
        self.xtea = tuple(a + b)

        # Check if version is correct
        if version > config.versionMax or version < config.versionMin:
            self.exitWithError(config.versionError)
            return

        # Check if there is a username (and a password)
        username = packet.string()
        password = packet.string()

        if not username and not config.anyAccountWillDo:
            self.exitWithError("You must enter your account number")
            return

        # Initialize the packet to send
        pkg = TibiaPacket()

        if username:
            # Our funny way of doing async SQL
            account = yield sql.conn.runQuery("SELECT `id`, `premdays` FROM `accounts` WHERE `name` = %s AND `password` = SHA1(CONCAT(`salt`, %s))", (username, password))

            if account:
                characters = yield sql.conn.runQuery("SELECT `name`,`world_id` FROM `players` WHERE account_id = %s", (account[0]['id']))
     
        if not username or not account:
            if config.anyAccountWillDo:
                account = ((0,0),)
                characters = config.anyAccountPlayerMap
            else:
                self.exitWithError("Invalid username or password")
                return 
        
        if config.letGameServerRunTheLoginServer:
            import game.scriptsystem
            game.scriptsystem.get("preSendLogin").runSync(None, client=self, characters=characters, account=account, username=username, password=password)

        # Send motd
        pkg.uint8(0x14)
        pkg.string(config.motd)

        # Add character list
        pkg.uint8(0x64)
        pkg.uint8(len(characters))
        for character in characters:
            ip = config.servers[character['world_id']][0]
            port = config.gamePort
            if ':' in ip:
                ip, port = ip.split(':')
                port = int(port)
            if ip in IPS:
                ip = IPS[ip]
            if ip != 'auto':
                _ip = ip
                ip = socket.gethostbyname(ip)
                IPS[_ip] = ip
            else:
                if self.transport.getPeer().host == '127.0.0.1':
                    ip = '127.0.0.1'
                else:
                    import urllib2
                    try:
                        ip = urllib2.urlopen("http://automation.whatismyip.com/n09230945.asp").read()
                    except:
                        ip = urllib2.urlopen("http://vapus.net/ip.php").read()

                    IPS['auto'] = ip
                    # Save IPS here.
                    cPickle.dump(IPS, open('IP_CACHE', 'wb'), 2)

            pkg.string(character['name'])
            pkg.string(config.servers[character['world_id']][1])
            pkg.raw(socket.inet_aton(ip))
            pkg.uint16(port)

        # Add premium days
        pkg.uint16(account[0]['premdays'])
        pkg.send(self) # Send

    def exitWithError(self, message, error = 0x0A):
        packet = TibiaPacket()
        packet.uint8(error) # Error code
        packet.string(message) # Error message
        packet.send(self)
        self.loseConnection()

class LoginFactory(protocolbase.TibiaFactory):
    __slots__ = ()
    protocol = LoginProtocol

    def __repr__(self):
        return "<Login Server Factory>"
