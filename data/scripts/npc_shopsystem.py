import game.scriptsystem as scriptsystem

greetings = ('hi ', 'hey ', 'hello ', 'hail ')
farwells = ('bye', 'farewell', 'cya')

def saidTo(creature, creature2, said, channel):
    if channel == 0:
        ok = False
        for greeting in greetings:
            if greeting+creature2.data["name"] == said:
                ok = True
                break
        if ok:
            creature.openPrivateChannel(creature2)

scriptsystem.reg("playerSayTo", 'shop', saidTo)