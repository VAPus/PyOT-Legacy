import game.npc as npc

soya = npc.genNPC("Soya", (139, 132, 79, 97, 132, 2212))
soya.setWalkable(False)
#soya.setActions('shop')
shop = soya.regAction('shop')
shop.offer('royal helmet', 5000, 10000)