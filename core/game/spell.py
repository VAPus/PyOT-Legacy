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

AREA_WAVE4 = game.enum.TARGET_DIRECTION, (0,), \
            (-1, 0, 1), \
            (-1, 0, 1), \
            (-2, -1, 0, 1, 2)
            
AREA_WAVE5 = game.enum.TARGET_DIRECTION, (0,), \
            (-1, 0, 1), \
            (-2, -1, 0, 1, 2), \
            (-2, -1, 0, 1, 2), \
            (-2, -1, 0, 1, 2), \
             
AREA_BEAM4 = game.enum.TARGET_DIRECTION,(0,), (0,), (0,), (0,)

AREA_BEAM7 = game.enum.TARGET_DIRECTION,(0,), (0,), (0,), (0,), (0,), (0,), (0,)

AREA_CIRCLE = game.enum.TARGET_CASTER_AREA, (-1, 1), (0, -1), (0, 1)

AREA_CIRCLE2 = game.enum.TARGET_CASTER_AREA, (-1, -2), (0, -2), (1, -2), \
               (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1), \
               (-2, 0), (-1, 0), (1, 0), (2, 0), \
               (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1), \
               (-1, 2), (0, 2), (1, 2)

AREA_SQUARE = game.enum.TARGET_CASTER_AREA, (-1, -1), (0, -1), (1, -1), \
              (-1, 0), (1, 0), \
              (-1, 1), (0, 1), (1, 1)

AREA_WALL = game.enum.TARGET_DIRECTION, (-2, -1, 1, 2)

def calculateAreaDirection(position, direction, area):
    positions = []
    if area[0] == game.enum.TARGET_DIRECTION:
        if direction == 0: # North:
            yp = 1
            for yo in area[1:]:
                for xp in yo:
                    x = position[0] - xp
                    y = position[1] - yp
                    positions.append([x,y, position[2]])
                yp += 1
                    
                
        elif direction == 1: # east
            xp = 1
            for xo in area[1:]:
                for yp in xo:
                    x = position[0] + xp
                    y = position[1] + yp
                    positions.append([x,y, position[2]])
                xp += 1          
        elif direction == 2: # South
            yp = 1
            for yo in area[1:]:
                for xp in yo:
                    x = position[0] + xp
                    y = position[1] + yp
                    positions.append([x,y, position[2]])
                yp += 1
        elif direction == 3: # west
            xp = 1
            for xo in area[1:]:
                for yp in xo:
                    x = position[0] - xp
                    y = position[1] - yp
                    positions.append([x,y, position[2]])
                xp += 1
    elif area[0] == game.enum.TARGET_CASTER_AREA:
        for a in area[1:]:
            x = position[0] - a[0]
            y = position[1] - a[1]
           
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
        if strength:
            minDmg, maxDmg = strength
        else:    
            maxDmg = -1 * (creature.data["level"]/lvlMax)+(creature.data["maglevel"]*mlvlMax)+constantMax
            minDmg = -1 * (creature.data["level"]/lvlMin)+(creature.data["maglevel"]*mlvlMin)+constantMin
        dmg = random.randint(round(minDmg), round(maxDmg))
        onCreature.modifyHealth(dmg)
        onCreature.onHit(creature, dmg, type)
        onCreature.lastDamager = creature
        
    return callback
    
def healTarget(mlvlMin, mlvlMax, constantMin, constantMax, lvlMin=5, lvlMax=5):
    def callback(creature, position, onCreature, onPosition, effect, strength):
        creature.shoot(position, onPosition, effect)
        if strength:
            minHP, maxHP = strength
        else:
            maxHP = (creature.data["level"]/lvlMax)+(creature.data["maglevel"]*mlvlMax)+constantMax
            minHP = (creature.data["level"]/lvlMin)+(creature.data["maglevel"]*mlvlMin)+constantMin

        onCreature.modifyHealth(random.randint(round(minHP), round(maxHP)))
    return callback

def damageArea(mlvlMin, mlvlMax, constantMin, constantMax, type, lvlMin=5, lvlMax=5):
    def callback(creature, position, effect, strength):
        tile = game.map.getTile(position)

        if tile == None:
            return # We don't do this on none 
            
        for item in tile.getItems():
            if item.blockprojectile: # or blockprojectile tiles
                return    
                
        creature.magicEffect(position, effect)
        if strength:
            minDmg, maxDmg = strength
        else:
            maxDmg = round(-1 * (creature.data["level"]/lvlMax)+(creature.data["maglevel"]*mlvlMax)+constantMax)
            minDmg = round(-1 * (creature.data["level"]/lvlMin)+(creature.data["maglevel"]*mlvlMin)+constantMin)
            
        creatures = tile.creatures()
        if creatures:
            for onCreature in creatures:
                dmg = round(random.randint(minDmg, maxDmg))
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
    def selftargetspell(creature, strength=None, **k):
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
        
def targetSpell(words, icon, level, mana, group, effect, area, callback, cooldown=2):
    def targetspell(creature, strength=None, **k):
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