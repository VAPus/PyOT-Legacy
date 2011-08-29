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
            creature2.sayTo(creature, creature2.base.shopFarewell % _sayParams)
            creature2.focus.remove(creature)
            creature.closeTrade()
            
        elif said in offers:
            
            if creature2.base.offers:
                creature2.sayTo(creature, creature2.base.shopTrade % _sayParams)
                creature2.sendTradeOffers(creature)
                creature.setTrade(creature2)
            else:
                creature2.sayTo(creature, creature2.base.shopEmpty % _sayParams)
        else:
            creature2.sayTo(creature, "i HEAR: '%s'" % said)


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
        
    def offer(self, name, sellPrice=0, buyPrice=0, count=1):
        if type(name) == str:
            name = game.item.itemNames[name]
            
        self.on.offers.append( (name, buyPrice, sellPrice, count) )

    def offerContainer(self, name, contains, count, buyPrice=0):
        pass # TODO
        
    def decline(self, text):
        self.on.shopDecline = text
        
    def greet(self, text):
        self.on.shopGreet = text
        
regClassAction('shop', Shop)

# Runes
class RuneShop(Shop):
    def action(self):
        Shop.action(self)
        # Include shop actions
        self.on.actions.append('shop')
        self.offer('intense healing rune', 95, 0, 1)
        self.offer('ultimate healing rune', 175, 0, 1)
        self.offer('magic wall rune', 2293, 0, 3)
        self.offer('destroy field rune', 45, 0, 3)
        self.offer('light magic missile rune', 40, 0, 10)
        self.offer('heavy magic missile rune', 120, 0, 10)
        self.offer('great fireball rune', 180, 0, 4)
        self.offer('explosion rune', 250, 0, 6)
        self.offer('sudden death rune', 350, 0, 3)
        #self.offer('death arrow rune', 300, 0, 3)
        self.offer('paralyze rune', 700, 0, 1)
        self.offer('animate dead rune', 375, 0, 1)
        self.offer('convince creature rune', 80, 0, 1)
        self.offer('chameleon rune', 210, 0, 1)
        self.offer('desintegrate rune', 80, 0, 3)

        self.offer('wand of vortex', 500, 250)
        self.offer('wand of dragonbreath', 1000, 500)
        self.offer('wand of decay', 5000, 2500)
        self.offer('wand of draconia', 7500, 3750)
        self.offer('wand of cosmic energy', 10000, 5000)
        self.offer('wand of inferno', 15000, 7500)
        self.offer('wand of starstorm', 18000, 9000)
        self.offer('wand of voodoo', 22000, 11000)

        self.offer('snakebite rod', 500, 250)
        self.offer('moonlight rod', 1000, 500)
        self.offer('necrotic rod', 5000, 2500)
        self.offer('northwind rod', 7500, 3750)
        self.offer('terra rod', 10000, 5000)
        self.offer('hailstorm rod', 15000, 7500)
        self.offer('springsprout rod', 18000, 9000)
        self.offer('underworld rod', 22000, 11000)

        self.offer('spellbook', 150)
        self.offer('magic lightwand', 400)

        self.offer('small health potion', 20, 0, 1)
        self.offer('health potion', 45, 0, 1)
        self.offer('mana potion', 50, 0, 1)
        self.offer('strong health potion', 100, 0, 1)
        self.offer('strong mana potion', 80, 0, 1)
        self.offer('great health potion', 190, 0, 1)
        self.offer('great mana potion', 120, 0, 1)
        self.offer('great spirit potion', 190, 0, 1)
        self.offer('ultimate health potion', 310, 0, 1)
        self.offer('antidote potion', 50, 0, 1)
        
regClassAction('runeshop', RuneShop)

# Have to apply on all prestores
scriptsystem.reg("playerSayTo", 'shop', saidTo)