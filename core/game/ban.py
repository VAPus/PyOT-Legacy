import datetime

banAccounts = {}
banPlayers = {}
banIps = {}

class BanEntry(object):
    __slots__ = 'id', 'time', 'reason'
    
    def __init__(self, id, time, reason):
        self.id = id
        self.time = time
        self.reason = reason
    
    def message(self):
        return "Reason: %s. It will expire: %s" % (self.reason, datetime.datetime.fromtimestamp(self.time).strftime(config.banTimeFormat))
@inlineCallbacks    
def refresh():
    global banAccounts, banPlayers, banIps
    _banAccounts = {}
    _banPlayers = {}
    _banIps = {}
    
    _time = time.time()
    
    for entry in (yield sql.runQuery("SELECT ban_id, ban_type, ban_data, ban_reason, ban_expire FROM bans WHERE ban_expire > %s", (_time))):
        banEntry = BanEntry(entry[0], entry[4], entry[3])
        
        if entry[1] == BAN_ACCOUNT:
            accountId = int(entry[2])
            _banAccounts[accountId] = banEntry
            
            # Check if any player use this account.
            for player in game.player.allPlayerObjects:
                if player.data["account_id"] == accountId:
                    player.exit("Your account have been banned! \n%s" % banEntry.message())
        elif entry[1] == BAN_PLAYER:
            playerId = int(entry[2])
            _banPlayers[playerId] = banEntry
            
            # Check if player is online.
            for player in game.player.allPlayerObjects:
                if player.data["id"] == playerId:
                    player.exit("Your player have been banned! \n%s" % banEntry.message())
                    break
                    
        elif entry[1] == BAN_IP:
            _banIps[entry[2]] = banEntry
            
            # Check if player is online.
            for player in game.player.allPlayerObjects:
                if player.getIP() == entry[2]:
                    player.exit("Your ip have been banned! \n%s" % banEntry.message())
                    break
    

    if config.refreshBans:
        callLater(config.refreshBans, refresh)
        
    banAccounts = _banAccounts
    banPlayers = _banPlayers
    banIps = _banIps
    
def ipIsBanned(ip):
    if isinstance(ip, Player):
        ip = ip.getIP()
        
    try:
        entry = banIps[ip]
        if entry.time > time.time():
            return True
        return False
    except:
        return False

def playerIsBanned(player):
    if isinstance(player, Player):
        player = player.data["id"]
    return player in banPlayers

    try:
        entry = banPlayers[player]
        if entry.time > time.time():
            return True
        return False
    except:
        return False

def accountIsBanned(account):
    if isinstance(account, Player):
        account = account.data["account_id"]

    try:
        entry = banAccounts[account]
        if entry.time > time.time():
            return True
        return False
    except:
        return False

@inlineCallbacks
def addBan(type, data, reason, expire):
    global banAccounts, banPlayers, banIps
    expire = time.time() + expire
    banEntry = BanEntry(0, expire, reason)
    if type == BAN_ACCOUNT:
        banAccounts[data] = banEntry
        
        for player in game.player.allPlayerObjects:
            if player.data["account_id"] == data:
                player.exit("Your account have been banned! \n%s" % banEntry.message())
    elif type == BAN_PLAYER:
        banPlayers[data] = banEntry
        
        for player in game.player.allPlayerObjects:
            if player.data["id"] == data:
                player.exit("Your player have been banned! \n%s" % banEntry.message())
                
    elif type == BAN_IP:
        banIps[data] = banEntry
        for player in game.player.allPlayerObjects:
            if player.getIP() == data:
                player.exit("Your ip have been banned! \n%s" % banEntry.message())
                
    banEntry.id = yield sql.runOperationLastId("INSERT INTO bans (ban_type, ban_data, ban_reason, ban_expire) VALUES(%s, %s, %s, %s)", (type, data, reason, expire))
        