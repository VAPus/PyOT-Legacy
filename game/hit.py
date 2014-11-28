import language
import time
import const as enum

class Hit(object):
    __slots__ = ("creature", "damage", "element", "time")

    def __init__(self, damage, element=enum.PHYSICAL, creature=None):
        self.damage = damage
        self.element = element
        self.creature = creature
        self.time = time.time()

    def byElement(self):
        return not self.creature

    def byPlayer(self):
        return self.creature and self.creature.isPlayer()

    def bySummon(self):
        return self.creature and self.creature.isSummon()

    def byMonster(self): #By wild monster actually
        return self.creature and (self.creature.isMonster() and not self.creature.isSummon())

    def __str__(self):
        if self.byElement():
            if self.element == enum.FIRE:
                return _("fire")
            elif self.element == enum.EARTH:
                return _("earth")
            elif self.element == enum.ENERGY:
                return _("energy")
            elif self.element == enum.ICE:
                return _("ice")
            elif self.element == enum.HOLY:
                return _("holiness")
            elif self.element == enum.DEATH:
                return _("death")
            elif self.element == enum.DROWN:
                return _("drowning")
            elif self.element == enum.LIFEDRAIN:
                return _("life drain")
        elif self.byPlayer():
            return self.creature.name()
        elif self.bySummon():
            return "%s of %s" % (self.creature.name(), self.creature.master.name())
        elif self.byMonster():
            return self.creature.base.data["description"]

        return "unkown force"
