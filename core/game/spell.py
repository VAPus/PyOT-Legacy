import game.scriptsystem # We use the talkactions from here
import game.item
import game.enum
import game.engine
import game.map
import random
import game.creature

spells = {}
fieldRunes = {}
targetRunes = {}

def calculateAreaDirection(position, direction, area):
    positions = []
    if area[0] == game.enum.TARGET_DIRECTION:
        # We begin on row 1, right in front of us
        yp = 1
        blocking = [] # We keep the blocking tiles from this row because we are using them in the next
        prevBlocking = []
        count = 0 # Count of fields in previous row, so we can calculate fields required
        minEntry = maxEntry = 0
        prevMinEntry = prevMaxEntry = 0
        for yo in area[1:]: # As you might know, area[0] is used to determin the type. yo == y list
                
            for xp in yo: # xp == x position from y list
                # First agenda is to determin whatever a previous field blocked us
                if count and prevBlocking:
                    if prevBlocking[0] == prevMinEntry and prevBlocking[0] >= xp: # Are we extending the so called minEntry border?
                        blocking.append(prevBlocking[0])
                        minEntry = prevMinEntry
                        continue
                    elif prevBlocking[-1] == prevMaxEntry and prevBlocking[-1] <= xp: # Are we extending the so called maxEntry border?
                        blocking.append(prevBlocking[-1])
                        maxEntry = prevMaxEntry
                        continue
                    elif xp in prevBlocking:
                        continue

                if direction == 0: # North:
                    pos = game.map.Position(position.x - xp, position.y - yp, position.z) # Our new position
                    
                elif direction == 1: # East
                    pos = game.map.Position(position.x + yp, position.y + xp, position.z) # Our new position
                    
                elif direction == 2: # South
                    pos = game.map.Position(position.x + xp, position.y + yp, position.z) # Our new position
                    
                elif direction == 3: # West
                    pos = game.map.Position(position.x - yp, position.y - xp, position.z) # Our new position
                    
                if xp > maxEntry: # Determin this as our new min/max
                    maxEntry = xp
                elif xp < minEntry:
                    minEntry = xp
                    
                tile = game.map.getTile(pos)
                if not tile:
                    blocking.append(xp)
                    continue
                    
                ret = 0
                for item in tile.getItems():
                    if item.blockprojectile:
                        blocking.append(xp)
                        ret = 1
                        break
                    
                if not ret:
                    positions.append(pos)


            count = len(yo)
            
            if count and count == len(blocking): # 100% blocking, it basicly means we're done
                return positions
                
            prevBlocking = blocking[:]
            blocking = [] # New blocking, from this level
            prevMaxEntry = maxEntry
            prevMinEntry = minEntry
            yp += 1
                    
    elif area[0] == game.enum.TARGET_CASTER_AREA:
        for a in area[1:]:
            x = position.x - a[0]
            y = position.y - a[1]
           
            positions.append(Position(x,y, position.z))
                  

    return positions
    
def typeToEffect(type):
    if type == "fire":
        return (game.enum.EFFECT_HITBYFIRE, game.enum.ANIMATION_FIRE)
    elif type == "poison":
        return (game.enum.EFFECT_HITBYPOISON, game.enum.ANIMATION_POISON)
  

def clear():
    fieldRunes.clear()
    targetRunes.clear()
    spells.clear()
    
    
    
### The new way ###

def damage(mlvlMin, mlvlMax, constantMin, constantMax, type=game.enum.MELEE, lvlMin=5, lvlMax=5):
    def damageCallback(caster, target, strength=None):  
        if strength:
            dmg = random.randint(strength[0], strength[1])
        else:
            maxDmg = (round((caster.data["level"]/lvlMax)+(caster.data["maglevel"]*mlvlMax)+constantMax))
            minDmg = (round((caster.data["level"]/lvlMin)+(caster.data["maglevel"]*mlvlMin)+constantMin))
            dmg = -random.randint(minDmg, maxDmg)
        

        target.modifyHealth(dmg)
        
        target.onHit(caster, dmg, type)
        target.lastDamager = caster
        
    return damageCallback
    
def heal(mlvlMin, mlvlMax, constantMin, constantMax, lvlMin=5, lvlMax=5, cure=True):
    def healCallback(caster, target, strength=None):
        if strength:
            minDmg, maxDmg = strength
        else:
            maxDmg = round((caster.data["level"]/lvlMax)+(caster.data["maglevel"]*mlvlMax)+constantMax)
            minDmg = round((caster.data["level"]/lvlMin)+(caster.data["maglevel"]*mlvlMin)+constantMin)
        

        target.modifyHealth(random.randint(minDmg, maxDmg))
        
        # Cure paralyzation if configurated to do so.
        if cure:
            target.loseCondition(game.enum.CONDITION_PARALYZE)
        
    return healCallback

def conjure(make, count=1, **kwargs):
    def conjureCallback(caster, target, strength=None):
        if target.isPlayer():
            item = game.item.Item(make, count, **kwargs)

            ret = target.itemToUse(item)
            if not ret:
                return target.notEnoughRoom()
                
            target.message("Made %dx%s" % (count, item.rawName()))
            
    return conjureCallback

def field(fieldId):
    def makeFieldCallback(position, **k):
        item = game.item.Item(fieldId)
        
        def effectOverTime(creature, damage, perTime, effect, forTicks, ticks=0):
            if not creature.alive:
                return
                
            ticks += 1
            creature.modifyHealth(-damage)
            creature.magicEffect(creature.position, effect)
            
            
            if ticks < forTicks:
                game.engine.safeCallLater(perTime, effectOverTime, creature, damage, perTime, effect, forTicks, ticks)
                
        def callback(creature, thing, **k):
            if thing.damage:
                creature.magicEffect(creature.position, typeToEffect(thing.field)[0])
                creature.modifyHealth(-thing.damage)
                
            if thing.turns:
                effectOverTime(creature, thing.damage, thing.ticks / 1000, typeToEffect(thing.field)[1], thing.turns)
        
        game.engine.placeItem(item, position)
            
        if item.damage:
            game.scriptsystem.reg('walkOn', item, callback)
            if item.duration:
                item.decay(position, callback=lambda i: game.scriptsystem.reg('walkOn', i, callback))
                
    return makeFieldCallback
    
class Spell(object):
    def __init__(self, name, words=None, icon=0, target=game.enum.TARGET_TARGET, group=game.enum.ATTACK_GROUP):
        self.name = name
        self.words = words
        self.targetType = target
        
        self.vocations = None
        
        self.castEffect = None
        self._targetEffect = None
        self.shootEffect = None
        self.areaEffect = None
        
        self.targetRange = 1
        
        self.targetArea = None
        
        self.effectOnCaster = []
        self.effectOnTarget = []
        self.conditionOnCaster = []
        self.conditionOnTarget = []
        
        self.icon = icon
        self.group = group
        
        self.learned = False
        
        self._requireGreater = []
        self._requireLess = []
        self._requireCallback = []
        
        self.cooldown = 2
        self.groupCooldown = 2

        func = self.doEffect()
        def l():
            try:
                mana = self._requireGreater["mana"]
            except:
                mana = 0
                
            try:
                level = self._requireGreater["level"]
            except:
                level = 0
                
            spells[name] = (func, words, level, mana)
        
        # Delay the input a little.
        game.engine.safeCallLater(0.1, l)
        
        if words:
            game.scriptsystem.reg("talkaction", words, func)
            
    def effects(self, caster=None, shoot=None, target=None, area=None):
        self.castEffect = caster
        self.shootEffect = shoot
        self._targetEffect = target
        self.areaEffect = area
        
    def area(self, area):
        self.targetArea = area
        self.targetType = TARGET_AREA
        
    def casterEffect(self, mana=0, health=0, soul=0, callback=None):
        if mana or health:
            def _effect(caster, target, **k):
                # Target = caster
                if health:
                    target.modifyHealth(health)
                if mana:
                    target.modifyMana(mana)
                if soul:
                    target.modifySoul(soul)
                    
            self.effectOnCaster.append(_effect)
            
        if callback:
            self.effectOnCaster.append(callback)
            
    def targetEffect(self, mana=0, health=0, soul=0, callback=None):
        if mana or health:
            def _effect(target, caster, **k):
                # Target = actual target
                if health:
                    if health < 0:
                        target.lastDamager = caster
                    target.modifyHealth(health)
                if mana:
                    target.modifyMana(mana)
                    
                if soul:
                    target.modifySoul(soul)
                    
            self.effectOnTarget.append(_effect)
            
        if callback:
            self.effectOnTarget.append(callback)
            
    def casterCondition(self, *argc, **kwargs):
        try:
            stack = kwargs['stackbehavior']
        except:
            stack = CONDITION_LATER
            
        for con in argc:
            self.conditionOnCaster.append((con, stack))

    def targetCondition(self, *argc, **kwargs):
        try:
            stack = kwargs['stackbehavior']
        except:
            stack = CONDITION_LATER
            
        for con in argc:
            self.conditionOnTarget.append((con, stack))
   
    def require(self, learned=False, vocations=None, **kwargs):
        self._requireGreater = kwargs
        self.vocations = vocations
        self.learned = learned
   
    def requireLess(self, **kwargs):
        self._requireLess = kwargs

    def requireCallback(self, *args):
        self._requireCallback.extend(args)

    def use(self, itemId=2260, count=1):
        def check(caster):
            useItem = caster.findItemById(itemId, count)
                
            if not useItem:
                caster.needMagicItem()
                caster.magicEffect(game.enum.EFFECT_POFF)
                return False
                
            return True
            
        self._requireCallback.append(check)
    
    def cooldowns(self, cooldown=0, groupCooldown=None):
        if cooldown and groupCooldown == None:
            groupCooldown = cooldown
           
        self.cooldown = cooldown
        self.groupCooldown = groupCooldown
       
    def doEffect(self):
        # Stupid weakrefs can't deal with me directly since i can't be a strong ref. Yeye, I'll just cheat and wrap myself!
        def spellCallback(creature, strength=None, **k):
            if creature.isPlayer():
                if not creature.canDoSpell(self.icon, self.group):
                    creature.exhausted()
                    return False
                
                if self.learned and not creature.canUseSpell(self.name):
                    return creature.cancelMessage("You need to learn this spell first.")
                    
                if self.vocations and creature.getVocationId() not in self.vocations:
                    return creature.cancelMessage("Your vocation cannot use this spell.")
                    
                if self._requireGreater:
                    for var in self._requireGreater:
                        if creature.data[var] < self._requireGreater[var]:
                            creature.notEnough(var)
                            return False
                            
                if self._requireLess:
                    for var in self._requireLess:
                        if creature.data[var] > self._requireLess[var]:
                            creature.message("Your %s is too high!" % var)
                            return False
                
                if self._requireCallback:
                    for call in self._requireCallback:
                        if not call(caster=creature): return
                        
                # Integrate mana seeker
                try:
                    creature.modifyMana(-self._requireGreater["mana"])
                    creature.modifySpentMana(self._requireGreater["mana"])
                except:
                    pass

                # Integrate soul seeker
                try:
                    creature.modifySoul(-self._requireGreater["soul"])
                except:
                    pass
                
                creature.cooldownSpell(self.icon, self.group, self.cooldown, self.groupCooldown)
                
            target = creature
            if self.targetType == TARGET_TARGET or self.targetType == TARGET_TARGETSELF:
                if creature.target:
                    target = creature.target
                elif not self.targetType == TARGET_TARGETSELF:
                    return
                    
            if self.castEffect:
                creature.magicEffect(self.castEffect)
            
            for call in self.effectOnCaster:
                call(caster=creature, target=creature, strength=strength)
            
            for array in self.conditionOnCaster:
                creature.condition(array[0].copy(), array[1])
                
            if self.targetType in (TARGET_TARGET, TARGET_TARGETSELF) and target and target != creature and self.shootEffect:
                creature.shoot(creature.position, target.position, self.shootEffect)
                
            if not self.targetType == TARGET_AREA:
                for call in self.effectOnTarget:
                    call(target=target, caster=creature, strength=strength)
                
                if self._targetEffect:
                    target.magicEffect(self._targetEffect)
                    
                for array in self.conditionOnTarget:
                    target.condition(array[0].copy(), array[1])

            if self.targetType == TARGET_AREA:
                area = self.targetArea(caster=creature) if callable(self.targetArea) else self.targetArea
                positions = calculateAreaDirection(creature.position, creature.direction, area)
                targets = []
                for pos in positions:
                    if self.areaEffect:
                        creature.magicEffect(self.areaEffect, pos)
                        
                    creatures = game.map.getTile(pos).creatures()
                    if creatures:
                        targets.extend(creatures)
                        
                print targets
                for targ in targets:
                    if self._targetEffect:
                        targ.magicEffect(self._targetEffect)
                        
                    for call in self.effectOnTarget:
                        call(target=targ, caster=creature, strength=strength)
                        
        return spellCallback
        
        
class Rune(Spell):
    def __init__(self, rune, icon=0, count=1, target=game.enum.TARGET_TARGET, group=game.enum.ATTACK_GROUP):
        self.rune = rune
        self.targetType = target
        self.count = count
        
        self.vocations = None
        
        self.castEffect = None
        self._targetEffect = None
        self.shootEffect = None
        self.areaEffect = None
        
        self.targetRange = 1
        
        self.targetArea = None
        
        self.effectOnCaster = []
        self.effectOnTarget = []
        self.conditionOnCaster = []
        self.conditionOnTarget = []
        
        self.icon = icon
        self.group = group
        
        self.learned = False
        
        self._requireGreater = []
        self._requireLess = []
        self._requireCallback = []
        
        self.cooldown = 2
        self.groupCooldown = 2

        func = self.doEffect()
        targetRunes[rune] = func # Just to prevent reset
        game.scriptsystem.get("useWith").reg(rune, func)
        
    def doEffect(self):
        # Stupid weakrefs can't deal with me directly since i can't be a strong ref. Yeye, I'll just cheat and wrap myself!
        def runeCallback(thing, creature, position, onPosition, onThing, strength=None, **k):

            if creature.isPlayer():
                if not creature.canDoSpell(self.icon, self.group):
                    creature.exhausted()
                    return False

                if self.learned and not creature.canUseSpell(self.name):
                    return creature.cancelMessage("You need to learn this spell first.")
                    
                if self.vocations and creature.getVocationId() not in self.vocations:
                    return creature.cancelMessage("Your vocation cannot use this spell.")
                    
                if self._requireGreater:
                    for var in self._requireGreater:
                        if creature.data[var] < self._requireGreater[var]:
                            creature.notEnough(var)
                            return False
                            
                if self._requireLess:
                    for var in self._requireLess:
                        if creature.data[var] > self._requireLess[var]:
                            creature.message("Your %s is too high!" % var)
                            return False
                
                if self._requireCallback:
                    for call in self._requireCallback:
                        if not call(caster=creature): return

                if not thing.count:
                    creature.needMagicItem()
                    creature.magicEffect(creature.position, game.enum.EFFECT_POFF)
                        
                else:
                    
                    if self.targetType == game.enum.TARGET_TARGET:
                        try:
                            onCreature = onThing
                            onCreature.isPlayer()
                        except:
                            return creature.onlyOnCreatures()
                        
                    creature.modifyItem(thing, position, -self.count)  
                    
                    # Integrate mana seeker
                    try:
                        creature.modifyMana(-self._requireGreater["mana"])
                        creature.modifySpentMana(self._requireGreater["mana"])
                    except:
                        pass

                    # Integrate soul seeker
                    try:
                        creature.modifySoul(-self._requireGreater["soul"])
                    except:
                        pass
                    
                    creature.cooldownSpell(self.icon, self.group, self.cooldown, self.groupCooldown)
                
            target = creature
            if self.targetType == TARGET_TARGET:
                target = onCreature
                if not target:
                    return
                    
            if self.castEffect:
                creature.magicEffect(self.castEffect)
            
            for call in self.effectOnCaster:
                call(caster=creature, target=creature, strength=strength)
            
            for array in self.conditionOnCaster:
                creature.condition(array[0].copy(), array[1])
                
            if self.targetType == TARGET_TARGET and self.shootEffect:
                creature.shoot(creature.position, target.position, self.shootEffect)
                
            if not self.targetType == TARGET_AREA:
                for call in self.effectOnTarget:
                    call(target=target, caster=creature, strength=strength)
                
                if self._targetEffect:
                    target.magicEffect(self._targetEffect)
                    
                for array in self.conditionOnTarget:
                    target.condition(array[0].copy(), array[1])
        
            else:
                for call in self.effectOnTarget:
                    call(target=None, caster=creature, strength=strength, position=onPosition)
                if self._targetEffect:
                    caster.magicEffect(self._targetEffect, onPosition)
                    
        if config.runeCastDelay:
            def castDelay(**k):
                game.engine.safeCallLater(config.runeCastDelay, runeCallback, **k)
                
            return castDelay
            
        return runeCallback