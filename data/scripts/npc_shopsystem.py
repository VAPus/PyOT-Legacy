import game.scriptsystem as scriptsystem

greetings = ('hi ', 'hey ', 'hello ', 'hail ')
farwells = ('bye', 'farewell', 'cya')

def saidTo(creature, creature2, said, channelType, channelId):
    if not channelId:
        ok = False
        for greeting in greetings:
            if greeting+creature2.data["name"] == said:
                ok = True
                break
        if ok:
            creature.openNPCChannel(creature2)
    elif channelType == 5 and channelId == creature2.name():
        print "This npc heard: %s" % said
scriptsystem.reg("playerSayTo", 'shop', saidTo)