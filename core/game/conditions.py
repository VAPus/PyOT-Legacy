class Condition(object):
    def __init__(self, type, subtype="", length=1, every=1, check=None, *argc, **kwargs):
        self.length = length
        self.every = every
        self.creature = None
        self.tickEvent = None
        self.check = check

        if subtype and isinstance(type, str):
            self.type = "%s_%s" % (type, subtype)
        else:
            self.type = type
        self.effectArgs = argc
        self.effectKwargs = kwargs

        try:
            self.effect
        except:
            if type == CONDITION_FIRE:
                self.effect = self.effectFire
            elif type == CONDITION_POISON:
                self.effect = self.effectPoison
            elif type == CONDITION_REGENERATEHEALTH:
                self.effect = self.effectRegenerateHealth
            elif type == CONDITION_REGENERATEMANA:
                self.effect = self.effectRegenerateMana

    def start(self, creature):
        self.creature = creature
        if self.creature.isPlayer():
            self.saveCondition = True

        self.init()
        self.tick()

    def stop(self):
        try:
            self.tickEvent.cancel()
        except:
            pass

        self.finish()

    def init(self):
        pass

    def callback(self): pass

    def finish(self):
        del self.creature.conditions[self.type]
        if self.creature.isPlayer():
            self.saveCondition = True
        self.creature.refreshConditions()
        self.callback()

    def effectPoison(self, damage=0, minDamage=0, maxDamage=0):
        self.creature.magicEffect(EFFECT_HITBYPOISON)
        self.creature.modifyHealth(-(damage or random.randint(minDamage, maxDamage)))

    def effectFire(self, damage=0, minDamage=0, maxDamage=0):
        self.creature.magicEffect(EFFECT_HITBYFIRE)
        self.creature.modifyHealth(-(damage or random.randint(minDamage, maxDamage)))

    def effectRegenerateHealth(self, gainhp=None):
        if not gainhp:
            gainhp = self.creature.getVocation().health
            self.creature.onHeal(None, gainhp[0])

        else:
            self.creature.onHeal(None, gainhp)

    def effectRegenerateMana(self, gainmana=None):
        if not gainmana:
            gainmana = self.creature.getVocation().mana
            self.creature.modifyMana(gainmana[0])

        else:
            self.creature.modifyMana(gainmana)

    def tick(self):
        if not self.creature:
            return

        self.effect(*self.effectArgs, **self.effectKwargs)
        self.length -= self.every # This "can" become negative!

        if self.check: # This is what we do if we got a check function, independantly of the length
            if self.check(self.creature):
                self.tickEvent = reactor.callLater(self.every, self.tick)
            else:
                self.finish()

        elif self.length > 0:
            self.tickEvent = reactor.callLater(self.every, self.tick)
        else:
            self.finish()

    def copy(self):
        return copy.deepcopy(self)

    def __getstate__(self):
        d = self.__dict__.copy()
        d["creature"] = None
        del d["tickEvent"]
        return d

class Boost(Condition):
    def __init__(self, type, mod, length, subtype="", percent=False, *argc, **kwargs):
        self.length = length
        self.creature = None
        self.tickEvent = None
        if subtype and isinstance(type, str):
            self.type = "%s_%s" % (type, subtype)
        else:
            self.type = '_'.join(type)
        self.ptype = [type] if not isinstance(type, list) else type
        self.effectArgs = argc
        self.effectKwargs = kwargs
        self.mod = [mod] if not isinstance(mod, list) else mod
        self.percent = percent

    def add(self, type, mod):
        self.ptype.append(type)
        self.mod.append(mod)
        return self

    def tick(self): pass
    def init(self):
        pid = 0
        for ptype in self.ptype:
            # Apply
            try:
                pvalue = getattr(self.creature, ptype)
                inStruct = 0
            except:
                pvalue = self.creature.data[ptype]
                inStruct = 1

            if isinstance(self.mod[pid], int):
                if self.percent:
                    pvalue *= self.mod[pid]
                else:
                    pvalue += self.mod[pid]
            else:
                pvalue = self.mod[pid](self.creature, ptype, True)

            # Hack
            if ptype == "speed":
                self.type = game.enum.CONDITION_HASTE
                self.creature.setSpeed(pvalue)
            else:
                if inStruct == 0:
                    setattr(self.creature, ptype, pvalue)
                else:
                    self.creature.data[ptype] = pvalue
            pid += 1

        self.tickEvent = reactor.callLater(self.length, self.finish)

        self.creature.refreshStatus()
    def callback(self):
        pid = 0
        for ptype in self.ptype:
            # Apply
            try:
                pvalue = getattr(self.creature, ptype)
                inStruct = 0
            except:
                pvalue = self.creature.data[ptype]
                inStruct = 1

            if isinstance(self.mod[pid], int):
                if self.percent:
                    pvalue /= self.mod[pid]
                else:
                    pvalue -= self.mod[pid]
            else:
                pvalue = self.mod[pid](self.creature, ptype, False)

            # Hack
            if ptype == "speed":
                self.creature.setSpeed(pvalue)
            else:
                if inStruct == 0:
                    setattr(self.creature, ptype, pvalue)
                else:
                    self.creature.data[ptype] = pvalue

            pid += 1
        self.creature.refreshStatus()
        
def MultiCondition(type, subtype="", *argc):
    conditions = []
    for x in argc:
        conditions.append(Condition(type, subtype, **x))

    for index in len(conditions):
        if index != len(conditions)-1:
            conditions[index].callback = lambda self: self.creature.condition(conditions[index+1])

    return conditions[0]

class CountdownCondition(Condition):
    pass

class CountupCondition(Condition):
    pass

class RepeatCondition(Condition):
    pass
