import game.scriptsystem
import game.item

# Magicly transform closed doors to open doors!
def addMapItem(creature, item, options):
    if game.item.items[item.itemId]["name"] == "closed door": # Also bad
        if game.item.items[item.itemId+1]["name"] == "open door":
            item = game.item.Item(item.itemId+1, **options)
        else:
            item = game.item.Item(1238, **options)
        
    return item # Must always do that

game.scriptsystem.get("addMapItem").reg(1209, addMapItem, toid=1257) # Bad, very very bad!