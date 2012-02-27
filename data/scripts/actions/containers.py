# First use of actions :p
def container(creature, thing, position, index):
    print position
    print index
    if thing.owners and creature not in thing.owners: # Prevent people to open owned things
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
            ok = creature.openContainer(thing, parent=parent)

        # Opened from ground, close it on next step :)
        if ok and position.x != 0xFFFF:
            def _vertifyClose(who):
                if thing.openIndex != None:
                    if not who.inRange(position, 1, 1):
                        who.closeContainer(thing)
                    else:
                        who.scripts["onNextStep"].append(_vertifyClose)
                    
            creature.scripts["onNextStep"].insert(0, _vertifyClose)
    else:
        creature.closeContainer(thing)

_script_ = game.scriptsystem.get("use")

for item in game.item.items:
    if item and "containerSize" in item:
        _script_.register(game.item.reverseItems[item["cid"]], container)