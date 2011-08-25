import game.monster
import game.engine
import random
import game.enum
import time
import config

def defaultBrainFeaturePriority(self, monster):
        # Walking
        if monster.target: # We need a target for this code check to run
            # If target is out of sight, stop following it and begin moving back to base position
            if not monster.canSee(monster.target.position) or monster.target.data["health"] < 1:
                monster.base.onTargetLost(monster.target)
                monster.target = None
                monster.intervals = {} # Zero them out
                if monster.walkPer == 0.1:
                    monster.walkPer = config.monsterWalkPer
                    monster.setSpeed(monster.speed / 2)
                
                if config.monsterWalkBack:
                    game.engine.autoWalkCreatureTo(monster, monster.spawnPosition, 0, True) # Yes, last step might be diagonal to speed it up
                else:
                    game.engine.safeCallLater(2, monster.teleport, monster.spawnPosition)
                    
                return
            
                
            elif monster.data["health"] <= monster.base.runOnHealth and monster.walkPer == config.monsterWalkPer:
                monster.walkPer = 0.5
                monster.setSpeed(monster.speed * 2)
            
            else:
                # First stratigic manuver
                for id, spell in enumerate(monster.base.defenceSpells):
                    key = "s%d"%id
                    if not key in monster.intervals or monster.intervals[key]+spell[0] > time.time():
                        if spell[2](monster):
                            game.spell.spells[spell[1]](monster, spell[3])
                            monster.intervals[key] = time.time()
                            return True # Until next brain tick
                
                # Melee attacks
                if monster.base.meleeAttacks and monster.inRange(monster.target.position, 1, 1):
                    attack = random.choice(monster.base.meleeAttacks)
                    if monster.lastMelee + attack[0] <= time.time() and attack[1](monster):
                        monster.target.onHit(monster, -1 * random.randint(0, round(attack[2] * config.monsterMeleeFactor)), game.enum.PHYSICAL)
                        monster.lastMelee = time.time()
                    
                    return True # If we do have a target, we stop here
                
                # Attack attacks
                for id, spell in enumerate(monster.base.defenceSpells):
                    key = "a%d"%id
                    if not key in monster.intervals or monster.intervals[key]+spell[0] > time.time():
                        if monster.inRange(monster.target.position, spell[3], spell[3]) and spell[2](monster):
                            game.spell.spells[spell[1]](monster, spell[4])
                            monster.intervals[key] = time.time()
                            return True # Until next brain tick     
                            


def defaultBrainFeature(self, monster):
        # Only run this check if there is no target, we are hostile and targetChance checksout
        if not monster.target and monster.base.hostile and monster.base.targetChance > random.randint(0, 100) and monster.data["health"] > monster.base.runOnHealth:
            spectators = game.engine.getSpectatorList(monster.position) # Get all creaturse in range
            if spectators: # If we find any
                target = None
                
                # Only run this code if there is more then one in range
                if len(spectators) > 1: 
                    bestDist = 0
                    for x in spectators:
                        # Calc x+y distance, diagonal is honored too.
                        dist = monster.distanceStepsTo(x.position) 
                        if dist < bestDist:
                            # If it's smaller then the previous value
                            bestDist = dist
                            target = x.player
                else:
                    # Target the singel spectator
                    target = spectators.pop().player
                monster.target = target
                
                # Call the scripts
                monster.base.onFollow(monster.target)
                
                # Begin autowalking
                game.engine.autoWalkCreatureTo(monster, monster.target.position, -1 * monster.base.targetDistance, lambda x: monster.turnAgainst(monster.target.position))
                
                # If the target moves, we need to recalculate, if he moves out of sight it will be caught in next brainThink
                def __followCallback(who):
                    if monster.target == who:
                        monster.stopAction()
                        game.engine.autoWalkCreatureTo(monster, monster.target.position, -1 * monster.base.targetDistance, lambda x: monster.turnAgainst(monster.target.position))
                        monster.target.scripts["onNextStep"].append(__followCallback)
                        
                monster.target.scripts["onNextStep"].append(__followCallback)
                return True # Prevent random walking


game.monster.regBrainFeature("default", defaultBrainFeaturePriority, 0)
game.monster.regBrainFeature("default", defaultBrainFeature, 1)