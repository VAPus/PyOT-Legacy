
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