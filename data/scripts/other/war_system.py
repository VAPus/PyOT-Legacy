# Is the war system enabled?
if config.enableWarSystem:
    # Guild war constants.
    GUILD_WAR_INVITE = 0
    GUILD_WAR_REJECT = 1
    GUILD_WAR_PENDING_PAYMENT = 2
    GUILD_WAR_CANCEL = 3
    GUILD_WAR_ACTIVE = 4
    GUILD_WAR_OVER = 5
    
    class WarEntry(object):
        def __init__(self, warId, guild1, guild2, started, duration, frags, stakes, status):
            self.warId = warId
            self.guild1 = guild1
            self.guild2 = guild2
            self.started = started
            self.duration = duration
            self.frags = frags
            self.stakes = stakes
            self.status = status
            
            # When to cancel war.
            callLater((started + duration) - time.time(), cancelWar, self)
            
            # TODO: fragchecks.
            
        def setStatus(self, status):
            global wars, warObjects, warInvites
            oldStatus = self.status
            
            self.status = status
            
            sql.runOperation("UPDATE guild_wars SET status = %s WHERE war_id = %s", (status, warId))
            
            if not self.guild1 in wars:
                wars[self.guild1] = [], [], []
                
            if not self.guild2 in wars:
                wars[self.guild2] = [], [], []
                
            if status == GUILD_WAR_ACTIVE:
                wars[self.guild1][0].append(self.guild2)
                wars[self.guild1][1].append(self)

                wars[self.guild2][0].append(self.guild1)
                wars[self.guild2][1].append(self)
                    
            elif status == GUILD_WAR_INVITE:
                wars[self.guild1][2].append(self)

                wars[self.guild2][2].append(self)
                    
            elif status == GUILD_WAR_PENDING_PAYMENT:
                
                pendingPayments.append(self)
                
            elif status == GUILD_WAR_OVER:
                pass # TODO
                
            if status in (GUILD_WAR_REJECT, GUILD_WAR_CANCEL) or (oldStatus == GUILD_WAR_INVITE and status == GUILD_WAR_PENDING_PAYMENT):
                try:
                    # Ow well.
                    wars[self.guild1][2].remove(self)
                except:
                    pass
                
                try:
                    # Ow well.
                    wars[self.guild2][2].remove(self)
                except:
                    pass
                
    wars = {} # GUILDID -> [guildIds at war], [warObjects at war], [warObjects on invite]
    pendingPayments = []
    
    _oldGetEmblem = game.player.Player.getEmblem
    # New emblem function.
    def getEmblem(self, creature):
        guildId = self.data["guild_id"]
        if guildId:
            if guildId == creature.data["guild_id"]:
                # Same guild.
                return EMBLEM_GREEN
            if guildId in wars:
                if creature.data["guild_id"] in wars[guildId][0]:
                    # We are at war with this guild.
                    return EMBLEM_RED
                    
                # We are at war, but not with him.
                return EMBLEM_BLUE
        
        # Call default function.
        return _oldGetEmblem(self, creature)
    
    # Cleanup callback.
    def cancelWar(warEntry):
        global wars, warObjects
        wars[warEntry.guild1][0].remove(warEntry.guild2)
        wars[warEntry.guild2][0].remove(warEntry.guild1)
        
        wars[warEntry.guild1][1].remove(warEntry)
        wars[warEntry.guild2][1].remove(warEntry)
        
        # TODO, deside winner.
        
    def checkPayments():
        global pendingPayments
        for entry in pendingPayments[:]:
            pass # TODO.
            
        callLater(3600, checkPayments) # Try once per hour to check for payments.
    
    def findInvite(creature, guild):
        try:
            for entry in wars[creature.data["guild_id"]][2]:
                if entry.guild2 == creature.data["guild_id"] and entry.guild1 == guild.id:
                    return entry
        except:
            pass
        
    def findIssuedInvite(creature, guild):
        try:
            for entry in wars[creature.data["guild_id"]][2]:
                if entry.guild1 == creature.data["guild_id"] and entry.guild2 == guild.id:
                    return entry
        except:
            pass
        
    # Loader.
    @inlineCallbacks
    def loadGuildWars():
        for entry in (yield sql.runQuery("SELECT w.war_id, w.guild_id, w.guild_id2, w.started, w.duration, w.frags, w.stakes, w.status FROM guild_wars w WHERE (SELECT 1 FROM guilds g WHERE g.world_id = %s AND g.guild_id = w.guild_id) AND w.status IN (0, 2, 4)", config.worldId)):
            warEntry = warEntry(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6])
            warEntry.setStatus(entry[6])
            
        checkPayments()
            
                    
    @register("startup")
    def init():
        # Replace the getEmblem for players.
        game.player.Player.getEmblem = getEmblem
        
        # Load using async sql.
        loadGuildWars()
        
    @register("talkactionRegex", "/war (?P<status>(accept|reject|cancel)) (?P<guildname>\w+)")
    def war_management(creature, status, guildname, **k):
        rank = creature.guildRank()
        if not rank or not rank.isLeader():
            creature.lmessage("You are not leader of a guild.")
            return False
            
        # Find invite entry.
        guild = getGuildByName(guildname)
        if not guild:
            creature.lmessage("Guild not found. Did you spell it right?")
            return False
            
        if status == "cancel":
            entry = findIssuedInvite(creature, guild)
        else:
            entry = findInvite(creature, guild)
                
        if not entry:
            creature.lmessage("Invite not found.")
            
        if status == "cancel":
            entry.setStatus(GUILD_WAR_CANCEL)
        elif status == "reject":
            entry.setStatus(GUILD_WAR_REJECT)
        else:
            entry.setStatus(GUILD_WAR_PENDING_PAYMENT)
            
        creature.message(_l(self, "War invitation with %(guildname)s have been %(status)s") % {"guildname":guildname, "status":status})
        return False
        
    @register("talkactionRegex", "/balance (?P<command>(pick|donate)) (?P<amount>\d+)")
    def balance_management(creature, command, amount, **k):
        # TODO: This is suppose to happen in the bank balance, not the inventory, but it's harder to debug it then, right?.
        guild = creature.guild()
        if not guild:
            creature.lmessage("You are not member of a guild.")
            return False
            
        if command == "donate":
            money = creature.getMoney()
            if money < amount:
                creature.lmessage("You don't have that much money.")
                return False
                
            creature.removeMoney(amount)
            guild.addMoney(amount)
            
            creature.message(_l(self, "You donated %(amount)d to your guild!") % {"amount": amount})
            
        else:
            if not creature.guildRank().isLeader():
                creature.lmessage("You are not guild leader.")
                return False
            
            money = guild.getMoney()
            if money < amount:
                creature.lmessage("Your guild don't have that much money.")
                return False
            
            guild.removeMoney(amount)
            creature.addMoney(amount)
            
            creature.message(_l(self, "You picked %(amount)d from your guild!") % {"amount": amount})
            
        return False