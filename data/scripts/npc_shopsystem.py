import game.scriptsystem as scriptsystem
from game.npc import ClassAction, regClassAction
import game.item

greetings = ('hi ', 'hey ', 'hello ', 'hail ')
farwells = ('bye', 'farewell', 'cya')
offers = ('offer', 'trade')

def saidTo(creature, creature2, said, channelType, channelId):
    print channelId
    if channelType == 1:
        ok = False
        for greeting in greetings:
            if greeting+creature2.data["name"] == said:
                ok = True
                break
        if ok:
            creature2.sayTo(creature, "Hello world!")
            
    elif channelType == 11:
        
        # Check for goodbyes
        if said in farwells:
            creature2.sendClose(creature)
            creature2.sayTo(creature, "Thank you, come again!")
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