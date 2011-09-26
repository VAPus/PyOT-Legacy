rustyItems = {\
# Rusty armor
9808: (2463, 2464, 2465, 2476, 2483),\
9809: (2463, 2464, 2465, 2476, 2483, 2487,8891),\
9810: (2463, 2464, 2465, 2466, 2472, 2476, 2483, 2487, 8891),\

# Rusty legs
9811: (2468, 2477, 2478, 2647, 2648),\
9812: (2468, 2477, 2478, 2488, 2647, 2648 ),\
9813: (2468, 2470, 2477, 2478, 2488, 2647, 2648),\

# Rusty Shield
9814: (2509, 2510, 2511, 2513, 2515, 2530),\
9815: (2509, 2510, 2511, 2513, 2515, 2516, 2519, 2530),\
9816: (2509, 2510, 2511, 2513, 2514, 2515, 2516, 2519, 2520, 2530),\

# Rusty Boots
9817: (2643, 3982, 5462, 7457),\
9818: (2195, 2643, 3982, 5462, 7457),\
9819: (2195, 2643, 2645, 3982, 5462, 7457),\

# Rusty Helmet
9820: (2457, 2458, 2460, 2480, 2481, 2491),\
9821: (2457, 2458, 2460, 2480, 2481, 2491, 2497),\
9822: (2457, 2458, 2460, 2475, 2480, 2481, 2491, 2497, 2498)\

}

def onUseWith(creature, thing, position, onThing, onPosition, **k):
    if onThing.itemId not in rustyItems:
        return False
    
    if random.randint(1, 100) > 50:
        creature.removeItem(onPosition, onStackpos)
        creature.message("You broken it.")
    else:
        revealedItem = rustyItems[onThing.itemId][random.randint(len(rustyItems[onThing.itemId])-1)]
        onThing.transform(revealedItem, onPosition)
        creature.message("You removed the rust, revealing a " + revealedItem.rawName() )
    
    creature.modifyItem(thing, position, stackpos, -1)
    
    return True



reg("useWith", 9930, onUseWith)