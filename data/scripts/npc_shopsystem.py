import game.scriptsystem as scriptsystem
from game.npc import ClassAction, regClassAction
import game.item
import game.enum

greetings = ('hi ', 'hey ', 'hello ', 'hail ')
farwells = ('bye', 'farewell', 'cya')
offers = ('offer', 'trade')

def saidTo(creature, creature2, said, channelType, channelId):
    if not creature2.isNPC():
        return # We got nothing todo
        
    said = said.lower()
    if channelType == 1 and not creature in creature2.focus:
        ok = False
        for greeting in greetings:
            if (greeting+creature2.data["name"]).lower() == said:
                ok = True
                break
        if ok:
            creature2.focus.add(creature)
            creature2.sayTo(creature, "Hello world!")
            
    elif channelType == 11 and not creature in creature2.focus:
        creature2.sayTo(creature, "Do I know you?")
    elif channelType == 11:
        # Check for goodbyes
        if said in farwells:
            creature2.sendClose(creature)
            creature2.sayTo(creature, "Thank you, come again!")
            creature2.focus.remove(creature)
            
        elif said in offers:
            creature2.sendTradeOffers(creature)
        else:
            creature2.sayTo(creature, "i HEAR: '%s'" % said)

scriptsystem.reg("playerSayTo", 'shop', saidTo)


# The offers action
class Shop(ClassAction):
    def action(self):
        self.on.offers = []
        
    def offer(self, name, buyPrice=0, sellPrice=0):
        if type(name) == str:
            name = game.item.itemNames[name]
            
        self.on.offers.append( (name, buyPrice, sellPrice) )
        
regClassAction('shop', Shop)