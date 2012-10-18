from test.framework import FrameworkTestGame

class TestMoveItem(FrameworkTestGame):
    def init(self):
        # Turn off ammo slot only for ammo.
        self.overrideConfig("ammoSlotOnlyForAmmo", False)
        
    def test_bug992(self):
        """ Aga bug #992. Drop item from ammo slot. http://vapus.net/forum/pyot-opentibia-server-287/debug-serious-bugs-thread-2925-100/#post31503 """
        
        # Turn on raises.
        self.player.toggleRaiseMessages()
        
        # Make some gold
        item = Item(2148, 10)
        
        # Place to inventory
        self.player.itemToInventory(item, SLOT_AMMO)
        
        # Assert position.
        self.assertIs(self.player.inventory[SLOT_AMMO], item)
        position = Position(0xFFFF, SLOT_AMMO+1, 0)
        
        # Move to ground.
        newPosition = self.player.positionInDirection(SOUTH)
        self.assertTrue(moveItem(self.player, position, newPosition))
        
        # Is it there?
        found = False
        for _item in newPosition.getTile().getItems():
            if _item == item:
                found = True
                
        self.assertTrue(found)
        
        self.player.toggleRaiseMessages()