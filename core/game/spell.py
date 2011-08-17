import game.scriptsystem # We use the talkactions from here
import game.item
import game.enum
import game.engine
import game.map
import random

spells = {}
fieldRunes = {}
targetRunes = {}
ATTACK_GROUP = 1
HEALING_GROUP = 2
SUPPORT_GROUP=3
SPECIAL_GROUP = 4

AREA_ONE = (0,0),

AREA_WAVE3 = (-1, 1), (0, 1), (1, 1), \
            (-1, 2), (0, 2), (1, 2), \
            (-2, 3), (-1, 3), (0, 3), (1, 3), (2, 3)
            
AREA_WAVE4 = (0, 1), \
             (-1, 2), (0, 2), (1, 2), \
             (-1, 3), (0, 3), (1, 3), \
             (-1, 4), (0, 4), (1, 4)
             
AREA_BEAM4 = (0, 1), (0, 2), (0, 3), (0, 4)

AREA_BEAM7 = (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)

AREA_CIRCLE = (-1, 0), (1, 0), (0, -1), (0, 1)

AREA_CIRCLE2 = (-1, -2), (0, -2), (1, -2), \
               (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1), \
               (-2, 0), (-1, 0), (1, 0), (2, 0), \
               (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1), \
               (-1, 2), (0, 2), (1, 2)

AREA_SQUARE = (-1, -1), (0, -1), (1, -1), \
              (-1, 0), (1, 0), \
              (-1, 1), (0, 1), (1, 1)

AREA_WALL = (-2, 0), (-1, 0), (1, 0), (2, 0)

def calculateAreaDirection(position, direction, area):
    positions = []
    if direction == 0: # North:
        for a in area:
            x = position[0] - a[0]
            y = position[1] - a[1]
            
            positions.append([x,y, position[2]])
            
    elif direction == 1: # east
        for a in area:
            x = position[0] + a[1]
            y = position[1] + a[0]
            
            positions.append([x,y, position[2]])            
    elif direction == 2: # South
        for a in area:
            x = position[0] + a[0]
            y = position[1] + a[1]
            
            positions.append([x,y,position[2]])
    elif direction == 3: # west
        for a in area:
            x = position[0] - a[1]
            y = position[1] - a[0]
            
            positions.append([x,y, position[2]])              
    return positions
    
def typeToEffect(type):
    if type == "fire":
        return (game.enum.EFFECT_HITBYFIRE, game.enum.ANIMATION_FIRE)
    elif type == "poison":
        return (game.enum.EFFECT_HITBYPOISON, game.enum.ANIMATION_POISON)
        
def makeField(fieldId):
    def make(position, **k):
        item = game.item.Item(fieldId)
        
        def effectOverTime(creature, damage, perTime, effect, forTicks, ticks=0):
            if not creature.alive:
                return
                
            ticks += 1
            creature.modifyHealth(-1 * damage)
            creature.magicEffect(creature.position, effect)
            
            
            if ticks < forTicks:
                game.engine.safeCallLater(perTime, effectOverTime, creature, damage, perTime, effect, forTicks, ticks)
                
        def callback(creature, thing, **k):
            if thing.damage:
                creature.magicEffect(creature.position, typeToEffect(thing.field)[0])
                creature.modifyHealth(-1 * thing.damage)
                
            if thing.turns:
                effectOverTime(creature, thing.damage, thing.ticks / 1000, typeToEffect(thing.field)[1], thing.turns)
        
        stackpos = game.engine.placeItem(item, position)
        if item.damage:
            game.scriptsystem.reg('walkOn', item, callback)
            if item.duration:
                item.decay(position, callback=lambda i: game.scriptsystem.reg('walkOn', i, callback))
                
    return make

def damageTarget(mlvlMin, mlvlMax, constantMin, constantMax, type, lvlMin=5, lvlMax=5):
    def callback(creature, position, onCreature, onPosition, effect, strength):
        creature.shoot(position, onPosition, effect)
        maxDmg = -1 * (creature.data["level"]/lvlMax)+(creature.data["maglevel"]*mlvlMax)+constantMax
        minDmg = -1 * (creature.data["level"]/lvlMin)+(creature.data["maglevel"]*mlvlMin)+constantMin
        dmg = round(random.randint(round(minDmg), round(maxDmg))) * strength
        onCreature.modifyHealth(dmg)
        onCreature.onHit(creature, dmg, type)
        onCreature.lastDamager = creature
        
    return callback
    
def healTarget(mlvlMin, mlvlMax, constantMin, constantMax, lvlMin=5, lvlMax=5):
    def callback(creature, position, onCreature, onPosition, effect, strength):
        creature.shoot(position, onPosition, effect)
        maxHP = (creature.data["level"]/lvlMax)+(creature.data["maglevel"]*mlvlMax)+constantMax
        minHP = (creature.data["level"]/lvlMin)+(creature.data["maglevel"]*mlvlMin)+constantMin

        onCreature.modifyHealth(round(random.randint(round(minHP), round(maxHP)) * strength))
    return callback

def damageArea(mlvlMin, mlvlMax, constantMin, constantMax, type, lvlMin=5, lvlMax=5):
    def callback(creature, position, effect, strength):
        creature.magicEffect(position, effect)
        maxDmg = -1 * (creature.data["level"]/lvlMax)+(creature.data["maglevel"]*mlvlMax)+constantMax
        minDmg = -1 * (creature.data["level"]/lvlMin)+(creature.data["maglevel"]*mlvlMin)+constantMin
        creatures = game.map.getTile(position).creatures()
        if creatures:
            for onCreature in creatures:
                dmg = round(random.randint(round(minDmg), round(maxDmg)) * strength)
                onCreature.onHit(creature, -1 * dmg, type)
                onCreature.lastDamager = creature
        
    return callback
    
def conjureRune(words, make, icon, mana=0, level=0, mlevel=0, soul=1, vocation=None, use=2260, useCount=1, makeCount=1, teached=0, group=3, cooldown=2):
    def conjure(creature, text):
        if not creature.canDoSpell(icon, group):
            creature.exhausted()
            return False
            
        # Checks
        if creature.data["level"] < level:
            creature.notEnough("level")
        elif creature.data["mana"] < mana:
            creature.notEnough("mana")
        elif creature.data["soul"] < soul:
            creature.notEnough("soul")
        elif creature.data["maglevel"] < mlevel:
            creature.notEnough("magic level")
        elif vocation and not creature.data["vocation"] in vocation:
            creature.notPossible()
        else:
            useItem = creature.findItemById(use, useCount)
                
            if not useItem:
                creature.needMagicItem()
                creature.magicEffect(creature.position, game.enum.EFFECT_POFF)
                
            else:
                item = game.item.Item(make,makeCount)

                ret = creature.itemToUse(item)
                if not ret:
                    creature.notEnoughRoom()
                
                if mana:
                    creature.modifyMana(-1 * mana)
                if soul:
                    creature.modifySoul(-1 * soul)
                creature.cooldownSpell(icon, group, cooldown)
                creature.message("Made %dx%s" % (makeCount, item.rawName()))
                creature.magicEffect(creature.position, game.enum.EFFECT_MAGIC_RED)
    if game.item.items[make]["name"].title() in spells:
        print "Warning: Duplicate spell with name %s" % name
    spells[game.item.items[make]["name"].title()] = (words, conjure)
    game.scriptsystem.get("talkaction").reg(words, conjure)
    
def fieldRune(rune, level, mlevel, icon, group, area, callback, cooldown=2, useCount=1):
    def fieldrune(creature, position, thing, stackpos, onPosition, **k):

        if not creature.canDoSpell(icon, group):
            creature.exhausted()
            return False
            
        if creature.data["level"] < level:
            creature.notEnough("level")
        elif creature.data["maglevel"] < mlevel:
            creature.notEnough("magic level")
            
        else:
            if not thing.count:
                creature.needMagicItem()
                creature.magicEffect(creature.position, game.enum.EFFECT_POFF)
                
            else:
                thing.count -= useCount
                if thing.count:
                    creature.replaceItem(position, stackpos, thing)
                else:
                    creature.removeItem(position, stackpos)
                
                creature.cooldownSpell(icon, group, cooldown)
                for a in area:
                    pos = onPosition[:]
                    pos[0] += a[0]
                    pos[1] += a[1]
                    callback(pos)

    fieldRunes[rune] = fieldrune # Just to prevent reset
    game.scriptsystem.get("useWith").reg(rune, fieldrune)

def targetRune(rune, level, mlevel, icon, group, effect, callback, cooldown=2, useCount=1):
    def targetrune(creature, thing, position, onPosition, stackpos, onStackpos, **k):

        if not creature.canDoSpell(icon, group):
            creature.exhausted()
            return False
            
        if creature.data["level"] < level:
            creature.notEnough("level")
        elif creature.data["maglevel"] < mlevel:
            creature.notEnough("magic level")
            
        else:
            if not thing.count:
                creature.needMagicItem()
                creature.magicEffect(creature.position, game.enum.EFFECT_POFF)
                
            else:
                thing.count -= useCount
                if thing.count:
                    creature.replaceItem(position, stackpos, thing)
                else:
                    creature.removeItem(position, stackpos)
                    
                creature.cooldownSpell(icon, group, cooldown)
                try:
                    onCreature = game.map.getTile(onPosition).getThing(onStackpos)
                    onCreature.isPlayer()
                except:
                    creature.onlyOnCreatures()
                else:
                    callback(creature, creature.position, onCreature, onPosition, effect)
                
    targetRunes[rune] = targetrune # Just to prevent reset
    game.scriptsystem.get("useWith").reg(rune, targetrune)

def selfTargetSpell(words, icon, level, mana, group, effect, callback, cooldown=1):
    def selftargetspell(creature, strength=1, **k):
        if creature.isPlayer():
            if not creature.canDoSpell(icon, group):
                creature.exhausted()
                return False
                    
            if creature.data["level"] < level:
                creature.notEnough("level")
                return False
                
            elif creature.data["mana"] < mana:
                creature.notEnough("mana")
                return False
            
            creature.modifyMana(-1 * mana)
            creature.cooldownSpell(icon, group, cooldown)
        callback(creature, creature.position, creature, creature.position, effect, strength)
            
    spells[words] = selftargetspell
    game.scriptsystem.reg("talkaction", words, selftargetspell)
        
def targetSpell(words, icon, level, mana, group, effect, area, targetType, callback, cooldown=2):
    def targetspell(creature, strength=1, **k):
        if creature.isPlayer():
            if not creature.canDoSpell(icon, group):
                creature.exhausted()
                return False
                    
            if creature.data["level"] < level:
                creature.notEnough("level")
                return False
                
            elif creature.data["mana"] < mana:
                creature.notEnough("mana")
                return False
            
            creature.modifyMana(-1 * mana)
            creature.cooldownSpell(icon, group, cooldown)
            
        positions = calculateAreaDirection(creature.position, creature.direction, area)
        for pos in positions:
            callback(creature, pos, effect, strength)
            
    spells[words] = targetspell
    game.scriptsystem.reg("talkaction", words, targetspell)
    
def clear():
    fieldRunes.clear()
    targetRunes.clear()
    spells.clear()