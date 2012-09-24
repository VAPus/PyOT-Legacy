guilds = {}
guild_names = {}

def getGuildById(id):
    try:
        return guilds[id]
    except:
        return None
        
def getGuildByName(name):
    try:
        return guild_names[name]
    except:
        return None
        
def guildExists(id):
    if getGuildById(id) is not None:
        return True
    else:
        return False
        
class Guild(object):
    def __init__(self, id, name, motd, balance):
        self.id = id
        self.name = name
        self.ranks = {} # rankId -> GuildRank
        self.motd = motd
        self.balance = balance
        
    # Creature alike money interface.
    def setMoney(self, amount):
        self.balance = amount
        sql.runOperation("UPDATE guilds SET balance = %d WHERE guild_id = %d", (amount, self.id))
        
    def getMoney(self):
        return self.balance
    
    def removeMoney(self, amount):
        self.balance -= amount
        sql.runOperation("UPDATE guilds SET balance = %d WHERE guild_id = %d", (self.balance, self.id))
        
    def addMoney(self, amount):
        self.balance += amount
        sql.runOperation("UPDATE guilds SET balance = %d WHERE guild_id = %d", (self.balance, self.id))
        
    def setMotd(self, motd):
        self.motd = motd
        sql.runOperation("UPDATE guilds SET motd = %s WHERE guild_id = %d", (motd, self.id))
        
    def setName(self, motd):
        self.name = name
        sql.runOperation("UPDATE guilds SET name = %s WHERE guild_id = %d", (name, self.id))
        
    def rank(self, rankId):
        return self.ranks[rankId]
    
    
class GuildRank(object):
    def __init__(self, guild_id, rank_id, title, permissions):
        self.guild_id = guild_id
        self.rank_id = rank_id
        self.title = title
        self.permissions = permissions
        
    def isMember(self):
        return self.permissions & GUILD_MEMBER
    
    def isLeader(self):
        return self.permissions & GUILD_LEADER
    
    def isSubLeader(self):
        return self.permissions & GUILD_SUBLEADER
        
    def permission(self, permission):
        return self.permissions & permission
    
    def guild(self):
        return guilds[self.guild_id]
        
@inlineCallbacks
def load():
    # Guilds
    for entry in (yield sql.runQuery("SELECT guild_id, name, motd, balance FROM `guilds` WHERE world_id = %s", config.worldId)):
        guild = Guild(int(entry[0]), entry[1], entry[2], entry[3])
        guilds[int(entry[0])] = guild
        guild_names[entry[1]] = guild
        
    # Ranks
    if guilds:
        for entry in (yield sql.runQuery("SELECT guild_id, rank_id, title, permissions FROM `guild_ranks` WHERE guild_id IN %s" % repr(tuple(guilds.keys())))):
            guilds[int(entry[0])].ranks[entry[1]] = GuildRank(int(entry[0]), entry[1], entry[2], entry[3])