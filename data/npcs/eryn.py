import game.npc as npc

soya = npc.genNPC("Eryn", (130, 39, 122, 125, 37, 2212), "Eryn, the rune vendor")
soya.setWalkable(False)
#soya.setActions('shop')
shop = soya.regAction('runeshop')

shop.greet("Hello %(playerName)s. I sell runes, potions, wands and rods.")
shop.decline("Is %(totalcost)d gold coins too much for you? Get out of here!")