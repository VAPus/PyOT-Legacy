from game import enum
import config

class CreatureAttacks(object):
    def hitEffects(self):
        if self.isPlayer() or self.base.blood == enum.FLUID_BLOOD:
            return enum.COLOR_RED, enum.EFFECT_DRAWBLOOD
        elif self.base.blood == enum.FLUID_SLIME:
            return enum.COLOR_LIGHTGREEN, enum.EFFECT_HITBYPOISON
        elif self.base.blood == enum.FLUID_ENERGY:
            return enum.COLOR_PURPLE, enum.EFFECT_PURPLEENERGY
        elif self.base.blood == enum.FLUID_UNDEAD:
            return enum.COLOR_GREY, enum.EFFECT_HITAREA
        elif self.base.blood == enum.FLUID_FIRE:
            return enum.COLOR_ORANGE, enum.EFFECT_DRAWBLOOD

    def damageToBlock(self, dmg, type):
        # Overrided to creatures.
        return dmg

    def onHit(self, by, dmg, type, effect=None):
        
        if not type == enum.DISTANCE:
            if not by.ignoreBlock and by.doBlock:
                dmg = min(self.damageToBlock(dmg, type), 0) # Armor calculations(shielding+armor)

        if type == enum.ICE:
            textColor = enum.COLOR_TEAL
            magicEffect = enum.EFFECT_ICEATTACK

        elif type == enum.FIRE:
            textColor = enum.COLOR_ORANGE
            magicEffect = enum.EFFECT_HITBYFIRE

        elif type == enum.EARTH:
            textColor = enum.COLOR_LIGHTGREEN
            magicEffect = enum.EFFECT_HITBYPOSION

        elif type == enum.ENERGY:
            textColor = enum.COLOR_PURPLE
            magicEffect = enum.EFFECT_ENERGYHIT

        elif type == enum.HOLY:
            textColor = enum.COLOR_YELLOW
            magicEffect = enum.EFFECT_HOLYDAMAGE

        elif type == enum.DEATH:
            textColor = enum.COLOR_DARKRED
            magicEffect = enum.EFFECT_SMALLCLOUDS

        elif type == enum.DROWN:
            textColor = enum.COLOR_LIGHTBLUE
            magicEffect = enum.EFFECT_ICEATTACK

        elif type == enum.DISTANCE:
            textColor, magicEffect = enum.COLOR_RED, None
            if not by.ignoreBlock and by.doBlock:
                dmg = min(self.damageToBlock(dmg, type), 0) # Armor calculations(armor only. for now its the same function)
        elif type == enum.LIFEDRAIN:
            textColor = enum.COLOR_TEAL
            magicEffect = enum.EFFECT_ICEATTACK

        else: ### type == enum.MELEE:
            textColor, magicEffect = self.hitEffects()
        if effect:
            magicEffect = effect

        # pvpDamageFactor.
        if self.isPlayer() and by.isPlayer() and (not config.blackSkullFullDamage or by.getSkull() != SKULL_BLACK):
            dmg = int(dmg * config.pvpDamageFactor)
            
        dmg = [dmg]
        textColor = [textColor]
        magicEffect = [magicEffect]
        type = [type]

        process = game.scriptsystem.get("hit").runSync(self, by, damage=dmg, type=type, textColor=textColor, magicEffect=magicEffect)
        if process == False:
            return

        dmg = dmg[0]
        textColor = textColor[0]
        magicEffect = magicEffect[0]
        type = type[0]

        dmg = max(-self.data["health"], dmg)
        
        if dmg:
            self.lastDamagers.appendleft(by)
            by.lastPassedDamage = time.time()
            
            if magicEffect:
                self.magicEffect(magicEffect)
            tile = game.map.getTile(self.position)
            for item in tile.getItems():
                if item.itemId in SMALLSPLASHES or item.itemId in FULLSPLASHES:
                    tile.removeItem(item)

            splash = game.item.Item(enum.SMALLSPLASH)

            if self.isPlayer():
                splash.fluidSource = enum.FLUID_BLOOD
            else:
                splash.fluidSource = self.base.blood
            if splash.fluidSource in (enum.FLUID_BLOOD, enum.FLUID_SLIME):
                splash.place(self.position)

                # Start decay
                splash.decay()

            updateTile(self.position, tile)

            if by and by.isPlayer():
                by.condition(Condition(CONDITION_INFIGHT, length=config.loginBlock), CONDITION_REPLACE)
                by.message(_lp(by, "%(who)s loses %(amount)d hitpoint due to your attack.", "%(who)s loses %(amount)d hitpoints due to your attack.", -dmg) % {"who": self.name().capitalize(), "amount": -dmg}, MSG_DAMAGE_DEALT, value = -1 * dmg, color = textColor, pos=self.position)
                
            if self.isPlayer():
                self.condition(Condition(CONDITION_INFIGHT, length=config.loginBlock), CONDITION_REPLACE)
                if by:
                    self.message(_lp(self, "You lose %(amount)d hitpoint due to an attack by %(who)s.", "You lose %(amount)d hitpoints due to an attack by %(who)s.", -dmg) % {"amount": -dmg, "who": by.name().capitalize()}, MSG_DAMAGE_RECEIVED, value = -1 * dmg, color = textColor, pos=self.position)
                else:
                    self.message(_lp(self, "You lose %(amount)d hitpoint.", "You lose %d hitpoints.", -dmg) % -dmg, MSG_DAMAGE_RECEIVED, value = -1 * dmg, color = textColor, pos=self.position)

            elif not self.target and self.data["health"] < 1:
                self.follow(by) # If I'm a creature, set my target

            self.modifyHealth(dmg)

            if by and self.data["health"] < 1:
                by.target = None
                by.targetMode = 0
                if by.isPlayer():
                    by.cancelTarget()

            return True
        else:
            return False

    def onHeal(self, by, amount):
        if self.data["healthmax"] != self.data["health"]:
            if by and by.isPlayer() and by != self:
                by.message(_lp(by, "%(who)s gain %(amount)d hitpoint.", "%(who)s gain %(amount)d hitpoints.", amount) % {"who": self.name().capitalize(), "amount": amount}, MSG_HEALED, value = amount, color = COLOR_GREEN, pos=self.position)

            if self.isPlayer():
                if by is self:
                    self.message(_lp(self, "You healed yourself for %(amount)d hitpoint.", "You healed yourself for %(amount)d hitpoints.", amount)  % {"amount": amount}, MSG_HEALED, value = amount, color = COLOR_GREEN, pos=self.position)
                elif by is not None:
                    self.message(_lp(self, "You gain %(amount)d hitpoint due to healing by %(who)s.", "You gain %(amount)d hitpoints due to healing by %(who)s.", amount)  % {"amount": amount, "who": by.name().capitalize()}, MSG_HEALED, value = amount, color = COLOR_GREEN, pos=self.position)
                else:
                    self.message(_lp(self, "You gain %d hitpoint.", "You gain %d hitpoints.", amount) % amount, MSG_HEALED, value = amount, color = COLOR_GREEN, pos=self.position)
             
                self.modifyHealth(amount)
        else:
            return False
            
            
class PlayerAttacks(CreatureAttacks):
    # Damage calculation:
    def damageToBlock(self, dmg, type):
        if dmg > 0:
            return int(dmg)
        
        if type == enum.MELEE or type == enum.PHYSICAL:
            # Armor and defence
            armor = 0
            defence = 0
            extradef = 0

            for item in self.inventory:
                if item:
                    armor += item.armor or 0
                    extradef += item.extradef or 0
                    block = (item.absorbPercentPhysical or 0) + (item.absorbPercentAll or 0)
                    if block:
                        dmg += (-dmg * block / 100.0)

            if self.inventory[enum.SLOT_LEFT]:
                defence = self.inventory[enum.SLOT_LEFT].defence
            elif self.inventory[enum.SLOT_RIGHT]:
                defence = self.inventory[enum.SLOT_RIGHT].defence

            if not defence:
                defence = 0
                
            defence += extradef
            defRate = 1
            if self.modes[1] == enum.OFFENSIVE:
                defRate = 0.5
            elif self.modes[1] == enum.BALANCED:
                defRate = 0.75

            if random.randint(1, 100) <= defence * defRate:
                self.lmessage("You blocked an attack!")
                
            # Apply some shielding effects
            dmg  = int((dmg + random.uniform(armor*0.475, (armor*0.95)-1)) + ((-dmg * armor) / 100.0))
            if dmg > 0:
                return 0
            else:
                return dmg

        return dmg

    def attackTarget(self, dmg = None):
        if dmg:
            assert dmg < 0, "Damage must be negative"
            
        atkRange = 1
        weapon = self.inventory[SLOT_RIGHT]
        ammo = None
        ok = True
        if weapon and weapon.range:
            atkRange = weapon.range
            # This is probably a slot consuming weapon.
            ammo = self.inventory[SLOT_AMMO]
            if weapon.ammoType == "bolt" and (not ammo or ammo.ammoType != "bolt" or ammo.count <= 0):
                self.cancelMessage("You are out of bolts.")
                ok = False
            elif weapon.ammoType == "arrow" and (not ammo or ammo.ammoType != "arrow" or ammo.count <= 0):
                self.cancelMessage("You are out of arrows.")
                ok = False
            
        if ok and self.target and self.target.isAttackable(self) and self.inRange(self.target.position, atkRange, atkRange):
            if not self.target.data["health"]:
                self.target = None
            else:
                atkType = MELEE
                factor = 1
                if self.modes[1] == enum.BALANCED:
                    factor = 0.75
                elif self.modes[1] == enum.DEFENSIVE:
                    factor = 0.5

                if not self.inventory[5]:
                    skillType = enum.SKILL_FIST
                    if dmg is None:
                        dmg = -random.randint(0, round(config.meleeDamage(1, self.getActiveSkill(skillType), self.data["level"], factor)))

                elif not dmg and atkRange > 1:
                    # First, hitChance.
                    chance = min(ammo.maxHitChance, config.hitChance(self.getActiveSkill(SKILL_DISTANCE), weapon.hitChance))
                    
                    self.modifyItem(ammo, Position(0xFFFF, SLOT_AMMO+1), -1)
                    
                    if chance < random.randint(1,100):
                        self.message("You missed!")
                        self.targetChecker = reactor.callLater(config.meleeAttackSpeed, self.attackTarget)
                        return
                    
                    minDmg = config.minDistanceDamage(self.data["level"])
                    maxDmg = config.distanceDamage(weapon.attack + ammo.attack, self.getActiveSkill(SKILL_DISTANCE), factor)
                    
                    dmg = -random.randint(round(minDmg), round(maxDmg))
                    
                    skillType = SKILL_DISTANCE
                    atkType = DISTANCE
                    
                    # Critical hit
                    if config.criticalHitRate > random.randint(1, 100):
                        dmg = dmg * config.criticalHitMultiplier
                        self.criticalHit()
                    # Charges.
                    if self.inventory[5].charges:
                        self.inventory[5].useCharge()

                else:
                    skillType = self.inventory[5].weaponSkillType
                    
                    if dmg is None:
                        dmg = -random.randint(0, round(config.meleeDamage(self.inventory[5].attack, self.getActiveSkill(skillType), self.data["level"], factor)))

                        # Critical hit
                        if config.criticalHitRate > random.randint(1, 100):
                            dmg = dmg * config.criticalHitMultiplier
                            self.criticalHit()

                        # Use charge.
                        if self.inventory[5].charges:
                            self.inventory[5].useCharge()

                targetIsPlayer = self.target.isPlayer() # onHit might remove this.
                target = self.target
                
                if dmg:
                    """if self.target.isPlayer() and (self.target.data["level"] <= config.protectionLevel and self.data["level"] <= config.protectionLevel):
                            self.cancelTarget()
                            self.cancelMessage(_l(self, "In order to engage in combat you and your target must be at least level %s." % config.protectionLevel))
                    else:
                        self.target.onHit(self, dmg, enum.MELEE)
                        self.skillAttempt(skillType)"""
                    target.onHit(self, dmg, atkType)
                    self.skillAttempt(skillType)
                else:
                    target.magicEffect(EFFECT_BLOCKHIT)
                    
                if targetIsPlayer:
                    self.lastDmgPlayer = time.time()
                    # If target do not have a green skull.
                    if target.getSkull(self) != SKULL_GREEN:
                        # If he is unmarked.
                        if config.whiteSkull and target.getSkull(self) not in (SKULL_ORANGE, SKULL_YELLOW) and target.getSkull(self) not in SKULL_JUSTIFIED:
                            self.setSkull(SKULL_WHITE)
                        elif config.yellowSkull and (target.getSkull(self) == SKULL_ORANGE or target.getSkull() in SKULL_JUSTIFIED):
                            # Allow him to fight back.
                            if self.getSkull(target) == SKULL_NONE:
                                self.setSkull(SKULL_YELLOW, target, config.loginBlock)
                if config.loginBlock:
                    # PZ block.
                    self.condition(Condition(CONDITION_INFIGHT, length=config.loginBlock), CONDITION_REPLACE)
                    if targetIsPlayer:
                        self.condition(Condition(CONDITION_PZBLOCK, length=config.loginBlock), CONDITION_REPLACE)

        if self.target:
            self.targetChecker = reactor.callLater(config.meleeAttackSpeed, self.attackTarget)

    def criticalHit(self):
        self.message(_l(self, "You strike a critical hit!"), MSG_STATUS_CONSOLE_RED)

    def cancelTarget(self, streamX=None):
        if not streamX:
            stream = self.packet()
        else:
            stream = streamX
        if self.target:
            self.target.scripts["onNextStep"] = filter(lambda a: a != self.followCallback, self.target.scripts["onNextStep"])
            """try:
                self.targetChecker.cancel()
            except:
                pass"""
            #self.walkPattern  =deque()
        stream.uint8(0xA3)

        stream.uint32(0)
        
        if not streamX:
            stream.send(self.client)

    def setAttackTarget(self, cid):
        if self.targetMode == 1 and self.target:
            self.targetMode = 0
            self.target = None
            return

        if time.time() - self.lastStairHop < config.stairHopDelay:
            print 'attack canceled: ', 1
            self.cancelTarget()
            self.message("You can't attack so fast after changing level or teleporting.")
            return
        
        if cid in game.creature.allCreatures:
            if game.creature.allCreatures[cid].isAttackable(self):
                target = game.creature.allCreatures[cid]
                if target.isPlayer() and self.modes[2]:
                    print 'attack canceled: ', 2
                    self.cancelTarget()
                    return self.unmarkedPlayer()
                ret = game.scriptsystem.get('target').runSync(self, target, attack=True)
                if ret == False:
                   print 'attack canceled: ', 3
                   self.cancelTarget()
                   return
                elif ret != None:
                    self.target = ret
                else:
                    self.target = target

                self.targetMode = 1
                if not target.target and isinstance(target, game.monster.Monster):
                    target.target = self
                    target.targetMode = 1
            else:
                print 'attack canceled: ', 4
                self.cancelTarget()
                return
        else:
            print 'attack canceled: ', 5
            self.cancelTarget()
            return self.notPossible()

        if not self.target:
            print 'attack canceled: ', 6
            self.cancelTarget()
            return self.notPossible()


        if self.modes[1] == enum.CHASE:
            print "did"
            game.engine.autoWalkCreatureTo(self, self.target.position, -1, True)
            self.target.scripts["onNextStep"].append(self.followCallback)

        if not self.targetChecker or not self.targetChecker.active():
            self.attackTarget()
            
