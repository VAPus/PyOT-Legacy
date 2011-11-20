from game.npc import ClassAction, regClassAction
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
            creature2.sayTo(creature, creature2.base.speakGreet % _sayParams)
            creature2.turnAgainst(creature.position)
            
    elif channelType == 11 and not creature in creature2.focus:
        creature2.sayTo(creature, "One moment...")
    elif channelType == 11:
        # Check for goodbyes
        if said in farwells:
            creature2.sayTo(creature, creature2.base.speakFarewell % _sayParams)
            creature2.focus.remove(creature)
            if creature2.activeModule:
                creature2.activeModule.close()
            try:
                creature2.base._onSaid[creature2.activeSaid][1](creature2, creature)
            except:
                pass
        
        elif creature2.activeModule:
            try:
                creature2.activeModule.send(said)
            except StopIteration:
                creature2.activeModule = None
        else:
            creature2.handleSpeak(creature, said)
            


# The offers action
class Shop(ClassAction):
    def action(self):
        self.on.offers = []
        self.on.shopBuy = "Do you want to buy %(itemCount)d %(itemName)s for %(totalcost)d gold coins?"
        self.on.shopOnBuy = "It was a pleasure doing business with you."
        self.on.shopDecline = "Not good enough, is it... ?"
        self.on.shopClose = "Thank you, come back when you want something more."
        self.on.shopWalkAway = "How rude!"
        self.on.shopEmpty = "Sorry, I'm not offering anything."
        self.on.shopTrade = "Here's my offer, %(playerName)s. Don't you like it?"
        
        self.on.onSaid(offers, self.handleOffers, self.handleClose)
        
    def offer(self, name, sellPrice=-1, buyPrice=-1, count=255):
        if type(name) == str:
            name = game.item.itemNames[name]
            
        self.on.offers.append( (name, sellPrice, buyPrice, count) )

    def offerContainer(self, name, contains, count, buyPrice=0):
        pass # TODO
    
    def handleOffers(self, npc, player):
        _sayParams = {"playerName":player.name()}
        
        if self.on.offers:
            npc.sayTo(player, self.on.shopTrade % _sayParams)
            npc.sendTradeOffers(player)
            player.setTrade(npc)
        else:
            npc.sayTo(player, self.on.shopEmpty % _sayParams)

    def handleClose(self, npc, player):
        player.closeTrade()
        
    def decline(self, decline):
        self.on.shopDecline = decline
        
regClassAction('shop', Shop)

# Runes
class RuneShop(Shop):
    def action(self):
        Shop.action(self)
        # Include shop actions
        self.on.actions.append('shop')
        self.offer('intense healing rune', 95, -1, 1)
        self.offer('ultimate healing rune', 175, -1, 1)
        self.offer('magic wall rune', 2293, -1, 3)
        self.offer('destroy field rune', 45, -1, 3)
        self.offer('light magic missile rune', 40, -1, 10)
        self.offer('heavy magic missile rune', 120, -1, 10)
        self.offer('great fireball rune', 180, -1, 4)
        self.offer('explosion rune', 250, -1, 6)
        self.offer('sudden death rune', 350, -1, 3)
        #self.offer('death arrow rune', 300, -1, 3)
        self.offer('paralyze rune', 700, -1, 1)
        self.offer('animate dead rune', 375, -1, 1)
        self.offer('convince creature rune', 80, -1, 1)
        self.offer('chameleon rune', 210, -1, 1)
        self.offer('desintegrate rune', 80, -1, 3)

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

        self.offer('small health potion', 20, -1, 1)
        self.offer('health potion', 45, -1, 1)
        self.offer('mana potion', 50, -1, 1)
        self.offer('strong health potion', 100, -1, 1)
        self.offer('strong mana potion', 80, -1, 1)
        self.offer('great health potion', 190, -1, 1)
        self.offer('great mana potion', 120, -1, 1)
        self.offer('great spirit potion', 190, -1, 1)
        self.offer('ultimate health potion', 310, -1, 1)
        self.offer('antidote potion', 50, -1, 1)
        
regClassAction('runeshop', RuneShop)

# Have to apply on all prestores
reg("playerSayTo", 'npc', saidTo)