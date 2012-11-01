# First use of actions :p
def container(creature, thing, position, index, **k):
    if thing.owners:
        party = creature.party()
        ownersParty = thing.owners[0].party()
        if creature not in thing.owners and (not party or party is not ownersParty): # Prevent people to open owned things. + Party features.
            return
    if thing.openIndex == None:
        # Open a bag inside a bag?
        open = True
        bagFound = creature.getContainer(index)
            
        if bagFound:
            print "ok --", index
            # Virtual close
            del creature.openContainers[index].openIndex
                
            # Virtual switch
            thing.openIndex = index
            thing.parent = creature.openContainers[index]
            
            # Virtual reopen
            creature.openContainers[index] = thing
            
            # Update the container
            creature.updateContainer(thing, parent=1)
            open = False
            ok = True
            
        if open:
            # Open a new one
            parent = 0

            #if position.x == 0xFFFF and position.y >= 64:
            if bagFound:
                parent = 1
                #thing.parent = creature.openContainers[position.y-64]
            if position.x != 0xFFFF:
                try:
                    thing.openCreatures.append(creature)
                except:
                    thing.openCreatures = [creature]
            ok = creature.openContainer(thing, parent=parent)

        # Opened from ground, close it on next step and set openCreatures :)
        if ok and position.x != 0xFFFF:
            def _verifyClose(who):
                if thing.openIndex != None:
                    if not who.inRange(position, 1, 1):
                        who.closeContainer(thing)
                    else:
                        who.scripts["onNextStep"].append(_verifyClose)
                    
            creature.scripts["onNextStep"].insert(0, _verifyClose)
    else:
        creature.closeContainer(thing)

_script_ = game.scriptsystem.get("use")
_items = game.item.items

for sid in _items:
    if "containerSize" in _items[sid]:
        _script_.register(sid, container)
