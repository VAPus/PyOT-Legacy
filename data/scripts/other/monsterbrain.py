def defaultBrainFeaturePriority(self, monster):
        # Walking
        if monster.target: # We need a target for this code check to run
            # If target is out of sight, stop following it and begin moving back to base position
            if not monster.canTarget(monster.target.position) or monster.target.data["health"] < 1:
                monster.base.onTargetLost(monster.target)
                monster.intervals = {} # Zero them out
                if monster.master:
                    monster.target = monster.master
                    monster.targetMode = 2
                    #engine.autoWalkCreatureTo(monster, monster.master.position, -1, False)
                    return
                else:
                    monster.target = None
                    monster.targetMode = 0
                
                if monster.walkPer == 0.1:
                    monster.walkPer = config.monsterWalkPer
                    monster.setSpeed(monster.speed / 2)
                
                if config.monsterWalkBack:
                    engine.autoWalkCreatureTo(monster, monster.spawnPosition, 0, True) # Yes, last step might be diagonal to speed it up
                elif not engine.hasSpectators(monster.position, (15, 15)):
                    engine.safeCallLater(2, monster.teleport, monster.spawnPosition)
                    
                return
            
                
            elif monster.data["health"] <= monster.base.runOnHealth and monster.walkPer == config.monsterWalkPer:
                monster.walkPer = 0.5
                monster.setSpeed(monster.speed * 2)
            
            elif monster.distanceStepsTo(monster.target.position) > monster.base.targetDistance:
                # When we reach our destination, can we target check
                def __walkComplete(x):
                    if not x:
                        # Walk not possible. Loose target
                        monster.target = None
                        monster.targetMode = 0
                        return
                        
                    # Are we OK?
                    if monster.distanceStepsTo(monster.target.position) <= monster.base.targetDistance:
                        monster.turnAgainst(monster.target.position)
                            
                # Begin autowalking
                engine.autoWalkCreatureTo(monster, monster.target.position, -monster.base.targetDistance, __walkComplete)
                    
            elif monster.targetMode == 1:
                # First stratigic manuver
                _time = time.time()
                for id, spell in enumerate(monster.base.defenceSpells):
                    key = "s%d"%id
                    if not key in monster.intervals or monster.intervals[key]+spell[0] > _time:
                        if spell[2](monster):
                            if type(spell[1]) == int:
                                game.spell.targetRunes[spell[1]](None, monster, None, None, monster, strength=spell[3])
                                    
                            else:
                                game.spell.spells[spell[1]][0](monster, spell[3])
                                
                                monster.intervals[key] = _time

                            return True # Until next brain tick
                
                # Summons
                if len(monster.activeSummons) < monster.base.maxSummon:
                    for summon in monster.base.summons:
                        if summon[1] > random.randint(0, 100):
                            try:
                                creature = game.monster.getMonster(summon[0]).spawn(monster.positionInDirection(random.randint(0,3)), spawnDelay=0)
                                creature.setMaster(monster)
                                monster.activeSummons.append(creature)
                            except:
                                print "%s tries to summon a invalid monster '%s'" % (monster.name(), summon[0])
                                
                            break
                """else:
                    for summon in monster.activeSummons[:]:
                        if not summon.alive:
                            monster.activeSummons.remove(summon)"""
                            
                # Melee attacks
                if monster.base.meleeAttacks and monster.inRange(monster.target.position, 1, 1):
                    attack = random.choice(monster.base.meleeAttacks)
                    if monster.lastMelee + attack[0] <= _time and attack[1](monster):
                        if attack[3] and random.randint(1,100) < attack[4]:
                            monster.target.condition(attack[3], attack[5])
                            
                        monster.target.onHit(monster, -1 * random.randint(0, round(attack[2] * config.monsterMeleeFactor)), game.enum.PHYSICAL)
                        monster.lastMelee = _time
                    
                    return True # If we do have a target, we stop here
                
                # Attack attacks
                for id, spell in enumerate(monster.base.defenceSpells):
                    key = "a%d"%id
                    if not key in monster.intervals or monster.intervals[key]+spell[0] > _time:
                        if monster.inRange(monster.target.position, spell[3], spell[3]) and spell[2](monster):
                            if type(spell[1]) == int:
                                game.spell.targetRunes[spell[1]](None, monster, None, None, monster.target, strength=spell[4])
                                    
                            else:
                                game.spell.spells[spell[1]][0](monster, spell[4])
                                
                            monster.intervals[key] = _time
                            return True # Until next brain tick     
                            


def defaultBrainFeature(self, monster):
        # Only run this check if there is no target, we are hostile and targetChance checksout
        if not monster.master:
            if not monster.target and monster.base.hostile and monster.base.targetChance > random.randint(0, 100) and monster.data["health"] > monster.base.runOnHealth:
                spectators = engine.getPlayers(monster.position) # Get all creaturse in range
                if spectators: # If we find any
                    target = None

                    bestDist = 127
                    for player in spectators:
                        # Can we target him, same floor
                        if monster.canTarget(player.position):
                            # Calc x+y distance, diagonal is honored too.
                            dist = monster.distanceStepsTo(player.position) 
                            if dist < bestDist:
                                # If it's smaller then the previous value
                                bestDist = dist
                                target = player
                    if target:
                        ret = game.scriptsystem.get('target').run(monster, target, attack=True)
                        
                        if ret == False:
                            return
                        elif ret != None:
                            monster.target = ret
                        else:
                            monster.target = target
                        monster.targetMode = 1
                    else:
                        return
                        
                    # Call the scripts
                    monster.base.onFollow(monster.target)
                    
                    # When we reach our destination, can we target check
                    def __walkComplete(x):
                        if not x:
                            # Walk not possible. Loose target
                            monster.target = None
                            monster.targetMode = 0
                            return
                        # Are we OK?
                        if monster.distanceStepsTo(monster.target.position) <= monster.base.targetDistance:
                            monster.turnAgainst(monster.target.position)
                        else:
                            # Apperently not. Try walking again.
                            engine.autoWalkCreatureTo(monster, monster.target.position, -monster.base.targetDistance, __walkComplete)
                            
                    # Begin autowalking
                    engine.autoWalkCreatureTo(monster, monster.target.position, -monster.base.targetDistance, __walkComplete)
                    
                    # If the target moves, we need to recalculate, if he moves out of sight it will be caught in next brainThink
                    def __followCallback(who):
                        if monster.target == who:
                            # Steps below is the old way of doing it, slow and ugly!
                            """monster.stopAction()
                            engine.autoWalkCreatureTo(monster, monster.target.position, -monster.base.targetDistance, lambda x: monster.turnAgainst(monster.target.position))
                            """
                            
                            # Remove the last entry. This will force us to do ONE more pathcalculation 50% of the times. It also might fail if there is no more
                            try:
                                # If the step are in the same direction as the player moved, then obiosly this is wasted since we'll just end up doing A* where we already know this is the ideal one.
                                if who.direction != monster.walkPattern[-1]:
                                    monster.walkPattern.pop()
                            except:
                                if monster.canTarget(monster.target.position):
                                    engine.autoWalkCreatureTo(monster, monster.target.position, -monster.base.targetDistance, __walkComplete)
                                elif not monster.canTarget(monster.target.position, allowGroundChange=True):
                                    monster.target = None
                                    monster.targetMode = 0
                                    
                            if monster.target:
                                # We shall be called again later
                                monster.target.scripts["onNextStep"].append(__followCallback)
                            
                    monster.target.scripts["onNextStep"].append(__followCallback)
                    return True # Prevent random walking
        else:
            if not monster.master.alive:
                monster.master = None # I've become independant
            elif monster.master.target and monster.master.targetMode == 1:
                # Target change
                if monster.master.target != monster.target:
                    monster.target = monster.master.target
                    monster.targetMode = 1
                    # Call the scripts
                    monster.base.onFollow(monster.target)
                    
                    # When we reach our destination, can we target check
                    def __walkComplete(x):
                        # Are we OK?
                        if monster.distanceStepsTo(monster.target.position) <= monster.base.targetDistance:
                            monster.turnAgainst(monster.target.position)
                        else:
                            # Apperently not. Try walking again.
                            engine.autoWalkCreatureTo(monster, monster.target.position, -monster.base.targetDistance, __walkComplete)
                            
                    # Begin autowalking
                    engine.autoWalkCreatureTo(monster, monster.target.position, -monster.base.targetDistance, __walkComplete)
                    
                    # If the target moves, we need to recalculate, if he moves out of sight it will be caught in next brainThink
                    def __followCallback(who):
                        if monster.target == who:
                            # Steps below is the old way of doing it, slow and ugly!
                            """monster.stopAction()
                            engine.autoWalkCreatureTo(monster, monster.target.position, -monster.base.targetDistance, lambda x: monster.turnAgainst(monster.target.position))
                            """
                            
                            # Remove the last entry. This will force us to do ONE more pathcalculation 50% of the times. It also might fail if there is no more
                            try:
                                # If the step are in the same direction as the player moved, then obiosly this is wasted since we'll just end up doing A* where we already know this is the ideal one.
                                if who.direction != monster.walkPattern[-1]:
                                    monster.walkPattern.pop()
                            except:
                                if monster.canTarget(monster.target.position):
                                    engine.autoWalkCreatureTo(monster, monster.target.position, -monster.base.targetDistance, __walkComplete)
                                else:
                                    monster.target = None
                                    monster.targetMode = 0
                                    
                            if monster.target:
                                # We shall be called again later
                                monster.target.scripts["onNextStep"].append(__followCallback)
                            
                    monster.target.scripts["onNextStep"].append(__followCallback)
                    return True # Prevent random walking
                else:
                    return
            elif not monster.inRange(monster.master.position, 1, 1):
                # Follow the master
                monster.target = monster.master
                monster.targetMode = 2
                # Call the scripts
                monster.base.onFollow(monster.target)

                # When we reach our destination, can we target check
                def __walkComplete(x):
                    # Are we OK?
                    if monster.distanceStepsTo(monster.target.position) <= monster.base.targetDistance:
                        monster.turnAgainst(monster.target.position)
                    else:
                        # Apperently not. Try walking again.
                        engine.autoWalkCreatureTo(monster, monster.target.position, -monster.base.targetDistance, __walkComplete)
                            
                # Begin autowalking
                engine.autoWalkCreatureTo(monster, monster.target.position, -monster.base.targetDistance, __walkComplete)
                    
                # If the target moves, we need to recalculate, if he moves out of sight it will be caught in next brainThink
                def __followCallback(who):
                    if monster.target == who:
                        # Steps below is the old way of doing it, slow and ugly!
                        """monster.stopAction()
                        engine.autoWalkCreatureTo(monster, monster.target.position, -monster.base.targetDistance, lambda x: monster.turnAgainst(monster.target.position))
                        """
                            
                        # Remove the last entry. This will force us to do ONE more pathcalculation 50% of the times. It also might fail if there is no more
                        try:
                            # If the step are in the same direction as the player moved, then obiosly this is wasted since we'll just end up doing A* where we already know this is the ideal one.
                            if who.direction != monster.walkPattern[-1]:
                                monster.walkPattern.pop()
                        except:
                            if monster.canTarget(monster.target.position):
                                engine.autoWalkCreatureTo(monster, monster.target.position, -monster.base.targetDistance, __walkComplete)
                            else:
                                monster.target = None
                                monster.targetMode = 0
                                
                        if monster.target:
                            # We shall be called again later
                            monster.target.scripts["onNextStep"].append(__followCallback)
                            
                monster.target.scripts["onNextStep"].append(__followCallback)
                return True # Prevent random walking                

game.monster.regBrainFeature("default", defaultBrainFeaturePriority, 0)
game.monster.regBrainFeature("default", defaultBrainFeature, 1)
