wars = {} # GUILDID -> [guilds at war]

_oldGetEmblem = game.creature.Creature.getEmblem
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
    
@register("startup")
def init():
    _oldGetEmblem = game.creature.Creature.getEmblem
    game.creature.Creature.getEmblem = getEmblem
    
@register("talkactionRegex", "/war (?P<status>(accept|reject|cancel)) (?P<guildname>\w+)")
def war_management(creature, status, guildname, **k):
    pass # TODO
    
@register("talkactionRegex", "/balance (?P<command>(pick|donate) (?P<amount>\d+)")
def balance_management(creature, command, amount, **k):
    pass # TODO