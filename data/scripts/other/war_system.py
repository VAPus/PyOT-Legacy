# Is the war system enabled?
if config.enableWarSystem:
    
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
            self.status = status
            
            sql.runOperation("UPDATE guild_wars SET status = %s WHERE war_id = %s", (status, warId))
            
            if status == GUILD_WAR_ACTIVE:
                try:
                    wars[self.guild1].append(self.guild2)
                    warObjects[self.guild2].append(self)
                except:
                    wars[self.guild1] = [entry[12]]
                    warObjects[self.guild2] = [self]
                    
                try:
                    wars[self.guild2].append(self.guild1)
                    warObjects[self.guild2].append(self)
                except:
                    wars[self.guild2] = [self.guild1]
                    warObjects[self.guild2] = [self]
                    
            elif status == GUILD_WAR_INVITE:
                try:
                    warInvites[self.guild1].append(self)
                except:
                    warInvites[self.guild1] = [self]
                    
                try:
                    warInvites[self.guild2].append(self)
                except:
                    warInvites[self.guild2] = [self]
                    
            elif status == GUILD_WAR_PENDING_PAYMENT:
                pendingPayments.append(self)
                
            elif status == GUILD_WAR_OVER:
                pass # TODO
                
            elif status == GUILD_WAR_REJECT or status == GUILD_WAR_CANCEL:
                try:
                    # Ow well.
                    warInvites[self.guild1].remove(self)
                except:
                    pass
                
                try:
                    # Ow well.
                    warInvites[self.guild2].remove(self)
                except:
                    pass
                
    wars = {} # GUILDID -> [guilds at war]
    warInvites = {} # GUILDID -> [warobjects]
    warObjects = {} # GUILDID -> [warobjects]
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
                if creature.data["guild_id"] in wars[guildId]:
                    # We are at war with this guild.
                    return EMBLEM_RED
                    
                # We are at war, but not with him.
                return EMBLEM_BLUE
        
        # Call default function.
        return _oldGetEmblem(self, creature)
    
    # Cleanup callback.
    def cancelWar(warEntry):
        global wars, warObjects
        wars[warEntry.guild1].remove(warEntry.guild2)
        wars[warEntry.guild2].remove(warEntry.guild1)
        
        warObjects[warEntry.guild1].remove(warEntry)
        warObjects[warEntry.guild2].remove(warEntry)
        
        # TODO, deside winner.
        
    def checkPayments():
        global pendingPayments
        for entry in pendingPayments[:]:
            pass # TODO.
        
    # Loader.
    @inlineCallbacks
    def loadGuildWars():
        for entry in (yield sql.runQuery("SELECT w.war_id, w.guild_id, w.guild_id2, w.started, w.duration, w.frags, w.stakes, w.status FROM guild_wars w WHERE (SELECT 1 FROM guilds g WHERE g.world_id = %s AND g.guild_id = w.guild_id) AND w.status IN (0, 2, 4)", config.worldId)):
            warEntry = warEntry(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6])
            warEntry.setStatus(entry[6])
            
        checkPayments()
        callLater(3600, checkPayments) # Try once per hour to check for payments.
            
                    
    @register("startup")
    def init():
        # Replace the getEmblem for players.
        game.player.Player.getEmblem = getEmblem
        
        # Load using async sql.
        loadGuildWars()
        
    @register("talkactionRegex", "/war (?P<status>(accept|reject|cancel)) (?P<guildname>\w+)")
    def war_management(creature, status, guildname, **k):
        pass # TODO
        
    @register("talkactionRegex", "/balance (?P<command>(pick|donate)) (?P<amount>\d+)")
    def balance_management(creature, command, amount, **k):
        pass # TODO