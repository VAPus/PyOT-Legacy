# regVocation() # ID, ClientId, name, description, (health, per sec), (mana, per sec), soulseconds)
vocation = regVocation(0, 1, "Rookie", "a rookie", (1, 12), (2, 6), 120)

vocation = regVocation(1, 8, "Sorcerer", "a sorcerer", (1, 12), (2, 3), 120)
vocation.manaFormula(lambda x: x*30 - 205)
vocation.mlevelConstant(1.1)

vocation = regVocation(2, 16, "Druid", "a druid", (1, 12), (2, 3), 120)
vocation.manaFormula(lambda x: x*30 - 205)
vocation.mlevelConstant(1.1)
vocation.meleeSkillConstant(1.8)

vocation = regVocation(3, 4, "Paladin", "a paladin", (1, 8), (2, 4), 120)
vocation.hpFormula(lambda x: x*10+105)
vocation.manaFormula(lambda x: x*15-85)
vocation.capasityFormula(lambda x: x*20+310)
vocation.mlevelConstant(1.4)
vocation.meleeSkillConstant(1.2)

vocation = regVocation(4, 2, "Knight", "a knight", (1, 6), (2, 6), 120)
vocation.hpFormula(lambda x: x*15+65)
vocation.capasityFormula(lambda x: x*25+270)
vocation.meleeSkillConstant(1.1)


vocation = regVocation(5, 8, "Master Sorcerer", "a master sorcerer", (1, 12), (2, 2), 15)
vocation.manaFormula(lambda x: x*30 - 205)
vocation.mlevelConstant(1.1)
vocation.maxSoul(200)

vocation = regVocation(6, 16, "Elder Druid", "an elder druid", (1, 12), (2, 2), 15)
vocation.manaFormula(lambda x: x*30 - 205)
vocation.mlevelConstant(1.1)
vocation.meleeSkillConstant(1.8)
vocation.maxSoul(200)

vocation = regVocation(7, 4, "Royal Paladin", "a royal paladin", (1, 6), (2, 3), 15)
vocation.hpFormula(lambda x: x*10+105)
vocation.manaFormula(lambda x: x*15-85)
vocation.capasityFormula(lambda x: x*20+310)
vocation.mlevelConstant(1.4)
vocation.meleeSkillConstant(1.2)
vocation.maxSoul(200)

vocation = regVocation(8, 2, "Elite Knight", "an elite knight", (1, 4), (2, 6), 15)
vocation.hpFormula(lambda x: x*15+65)
vocation.capasityFormula(lambda x: x*25+270)
vocation.meleeSkillConstant(1.1)
vocation.maxSoul(200)

# TODO:
"""
set those:
        
    def hpFormula(self, formula):
        
        
    def manaFormula(self, formula): 
        
        
    def capasityFormula(self, formula):

        
    def meleeSkillConstant(self, constant):
        
    def mlevelConstant(self, constant):
    
    TODO: Shielding etc

"""
