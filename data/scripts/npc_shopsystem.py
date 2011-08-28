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
    _sayParams = {"playerName":creature.name()}
    
    if channelType == 1 and not creature in creature2.focus:
        ok = False
        for greeting in greetings:
            if (greeting+creature2.data["name"]).lower() == said:
                ok = True
                break
        if ok:
            creature2.focus.add(creature)
            creature2.sayTo(creature, creature2.base.shopGreet % _sayParams)
            creature2.turnAgainst(creature.position)
            
    elif channelType == 11 and not creature in creature2.focus:
        creature2.sayTo(creature, "Do I know you?")
    elif channelType == 11:
        # Check for goodbyes
        if said in farwells:
            creature2.sendClose(creature)
            creature2.sayTo(creature, creature2.base.shopFarewell % _sayParams)
            creature2.focus.remove(creature)
            
        elif said in offers:
            creature2.sayTo(creature, creature2.base.shopTrade % _sayParams)
            creature2.sendTradeOffers(creature)
        else:
            creature2.sayTo(creature, "i HEAR: '%s'" % said)

scriptsystem.reg("playerSayTo", 'shop', saidTo)


# The offers action
class Shop(ClassAction):
    def action(self):
        self.on.offers = []
        self.on.shopGreet = "Welcome, %(playerName)s! I have been expecting you."
        self.on.shopFarewell = "Good bye, %(playerName)s!"
        self.on.shopBuy = "Do you want to buy %(itemCount)d %(itemName)s for %(totalcost)d gold coins?"
        self.on.shopOnBuy = "It was a pleasure doing business with you."
        self.on.shopDecline = "Not good enough, is it... ?"
        self.on.shopClose = "Thank you, come back when you want something more."
        self.on.shopWalkAway = "How rude!"
        self.on.shopEmpty = "Sorry, I'm not offering anything."
        self.on.shopTrade = "Here's my offer, %(playerName)s. Don't you like it?"
        
    def offer(self, name, buyPrice=0, sellPrice=0):
        if type(name) == str:
            name = game.item.itemNames[name]
            
        self.on.offers.append( (name, buyPrice, sellPrice) )
        
    def decline(self, text):
        self.on.shopDecline = text
        
    def greet(self, text):
        self.on.shopGreet = text
        
regClassAction('shop', Shop)