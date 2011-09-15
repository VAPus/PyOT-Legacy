vocations = {}
vocationsId = {}
class Vocation(object):
    def __init__(self, id, name, description, health, mana, soulticks):
        self.id = id
        self.name = name
        self.description = description
        self.health = health
        self.mana = mana
        self.soulticks = soulticks
        self.calcMaxHP = lambda x: x*5 + 145
        self.calcMaxMana = lambda x: x*5 - 5
        self.calcMaxCapasity = lambda x: x*10 + 390
        self.soul = 100
        self.mlevel = 3
        self.meleeSkill = 2
        
        
    def maxHP(self, x):
        return self.calcMaxHP(x)
        
    def hpFormula(self, formula):
        self.calcMaxHP = formula
        
    def maxMana(self, x):
        return self.calcMaxMana(x)
        
    def manaFormula(self, formula):
        self.calcMaxMana = formula   
        
    def maxCapasity(self, x):
        return self.calcMaxCapasity(x)
        
    def capasityFormula(self, formula):
        self.calcMaxCapasity = formula   

    def maxSoul(self, soul):
        self.soul = soul
        
    def meleeSkillConstant(self, constant):
        self.meleeSkill = constant
        
    def mlevelConstant(self, constant):
        self.mlevel = constant
    
    def description(self):
        return "a %s" % self.name
        
def regVocation(id, name, description, health, mana, soulticks):
    vocation = Vocation(id, name, description, health, mana, soulticks)
    vocations[name] = vocation
    vocationsId[id] = vocations[name]
    return vocation

def getVocation(name):
    try:
        return vocations[name]
    except:
        return

def getVocationById(id):
    try:
        return vocationsId[id]
    except:
        return