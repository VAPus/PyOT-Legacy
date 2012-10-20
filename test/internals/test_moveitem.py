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
        
    def test_bug59(self):
        """ Issue #59 part 2. http://vapus.net/forum/project.php?issueid=59 """
        
        # Make some gold
        item = Item(2148, 100)
        
        # Place to inventory.
        self.player.itemToInventory(item, SLOT_AMMO)
        
        # Split stack.
        # Move to ground.
        position = Position(0xFFFF, SLOT_AMMO+1, 0)
        
        self.assertTrue(moveItem(self.player, position, self.player.position, 50))
        
        # Is it still there?
        self.assertEqual(self.player.inventory[SLOT_AMMO], item)
        
        # Correct count?
        self.assertEqual(item.count, 50)
        
    def test_stack(self):
        """ Reverse of the above. """
        
        # Make some gold
        item = Item(2148, 50)
        item2 = Item(2148, 50)
        stack = self.player.position.getTile().placeItem(item2)
        groundPosition = self.player.position.setStackpos(stack)
        
        # Place to inventory.
        self.player.itemToInventory(item, SLOT_AMMO)
        
        # Move stack from ground to inventory.
        position = Position(0xFFFF, SLOT_AMMO+1, 0)
        
        self.assertTrue(moveItem(self.player, groundPosition, position, 50))
        
        # Is it still there?
        self.assertEqual(self.player.inventory[SLOT_AMMO], item)
        
        # And not on the ground?
        self.assertFalse(item2 in self.player.position.getTile().things)
        
        # Correct count?
        self.assertEqual(item.count, 100)
        
    def test_closebag(self):
        # Make a bag.
        item = Item(1987)
        self.player.itemToInventory(item, SLOT_BACKPACK)
        
        # Open bag.
        self.player.openContainer(item)
        
        # Move to ground.
        newPosition = self.player.position.copy()
        newPosition.x += 2
        self.assertTrue(moveItem(self.player, Position(0xFFFF, SLOT_BACKPACK+1, 0), newPosition))
        self.assertFalse(item.openIndex)