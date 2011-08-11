from game.vocation import regVocation

# regVocation() # ID, name, description, (health, per sec), (mana, per sec), soulseconds)
vocation = regVocation(0, "Rookie", "a rookie", (1, 12), (2, 6), 120)
vocation = regVocation(1, "Sorcerer", "a sorcerer", (1, 12), (2, 3), 120)
vocation = regVocation(2, "Druid", "a druid", (1, 12), (2, 3), 120)
vocation = regVocation(3, "Paladin", "a paladin", (1, 8), (2, 4), 120)
vocation = regVocation(4, "Knight", "a knight", (1, 6), (2, 6), 120)
vocation = regVocation(5, "Master Sorcerer", "a master sorcerer", (1, 12), (2, 2), 120)
vocation = regVocation(6, "Elder Druid", "an elder druid", (1, 12), (2, 2), 120)
vocation = regVocation(7, "Royal Paladin", "a royal paladin", (1, 6), (2, 3), 120)
vocation = regVocation(8, "Elite Knight", "an elite knight", (1, 4), (2, 6), 120)
# TODO formula adjustments