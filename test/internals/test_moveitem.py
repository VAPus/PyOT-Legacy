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
            if _item.itemId == item.itemId:
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
        item2.place(self.player.position)
        stack = self.player.position.getTile().things.index(item2)
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
        

    def test_move_ground(self):
        # Make some gold.
        item = Item(2148, 10)
        item.place(self.player.position)
        
        # Move.
        self.assertTrue(moveItem(self.player, item.position, self.player.positionInDirection(SOUTH), 10))

        things = self.player.position.getTile().things
        self.assertNotIn(item, things)
        
        ok = False
        for thing in self.player.positionInDirection(SOUTH).getTile().things:
            if thing.itemId == item.itemId:
                ok = True
                
        self.assertTrue(ok)
        
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
        
    def test_move_ground_no_count(self):
        # Make some gold.
        item = Item(2148, 10)
        item.place(self.player.position)
        
        self.assertEqual(self.player.position, item.position)
        
        # Move.
        self.assertTrue(moveItem(self.player, item.position, self.player.positionInDirection(SOUTH)))

        things = self.player.position.getTile().things
        self.assertNotIn(item, things)
        
        ok = False
        for thing in self.player.positionInDirection(SOUTH).getTile().things:
            if thing.itemId == item.itemId:
                ok = True
                
        self.assertTrue(ok)

    def test_move_ammo_bag_ground(self):
        self.player.toggleRaiseMessages()

        # Make some arrows
        item = Item(2544, 100)

        # Make a bag.
        bag = Item(1987)

        # Place to inventory.
        self.player.itemToInventory(item, SLOT_AMMO)
        self.player.itemToInventory(bag, SLOT_BACKPACK)

        # Open bag.
        self.player.openContainer(bag)

        # Move to bag.
        position = Position(0xFFFF, SLOT_AMMO+1, 0)
        bagPosition = Position(0xFFFF, SLOT_BACKPACK+1, 0)

        self.assertTrue(moveItem(self.player, position, bagPosition, 100))

        self.assertFalse(config.ammoSlotOnlyForAmmo)

        # Move to ground.
        self.assertTrue(moveItem(self.player, Position(0xFFFF, bag.openIndex+64,0), self.player.position))

        # Is it still there?
        self.assertEqual(self.player.inventory[SLOT_AMMO], None)

        self.player.toggleRaiseMessages()

    def test_move_to_self(self):
        # Make a gold coin 
        item = Item(2148, 1)

        # Make a bag.
        bag = Item(1987)

        # Place to inventory
        self.player.itemToInventory(bag, SLOT_BACKPACK)

        # Item to bag.
        self.player.itemToContainer(bag, item)

        # Open bag.
        self.player.openContainer(bag)

        # Move to bag.
        self.assertFalse(moveItem(self.player, Position(0xFFFF, bag.openIndex+64, 0), Position(0xFFFF, SLOT_BACKPACK+1, 0))) 

    def test_dual_handed(self):
        # Make a dual handed sword
        item = Item(7449)

        self.assertEqual(item.slotType, "two-handed")

        # Place it.
        self.player.itemToInventory(item, SLOT_RIGHT)

        # Make a shield
        item = Item(2509)
        
        # Place it.
        item.place(self.player.position)

        # Move it. Shouldn't work.
        self.assertFalse(moveItem(self.player, item.position, Position(0xFFFF, SLOT_LEFT-1, 0)))

    def test_courpse_to_corpse_stack(self):
        """ Bug #78 """
        # Set meat to 100%.
        wolf = getMonster("Wolf")
        if not wolf.prepared:
            wolf.prepare()

        for loot in wolf.lootTable:
           if loot[0] == 2666:
               loot[1] = 100.0

        # Spawn and kill two wolfs
        position1 = self.player.positionInDirection(NORTH)
        position2 = self.player.positionInDirection(SOUTH)

        wolf1 = wolf.spawn(position1, spawnDelay=0)
        wolf2 = wolf.spawn(position2, spawnDelay=0)

        wolf1.modifyHealth(-1000)
        wolf2.modifyHealth(-1000)

        # Get the corpses.
        corpse1 = position1.getTile().findItem(wolf.data["corpse"])
        corpse2 = position2.getTile().findItem(wolf.data["corpse"])

        # Open corpses.
        self.player.use(corpse1)
        self.player.use(corpse2)

        # Find meat and move from corpse1 to corpse2.
        for index in xrange(len(corpse1.container)):
            if corpse1.container[index].itemId == 2666:
                break

        # Move
        self.assertTrue(moveItem(self.player, Position(0xFFFF, 64, index), Position(0xFFFF, 65, 3)))

        # Find new meat.
        for item in corpse2.container:
            if item.itemId == 2666:
                self.assertGreater(item.count, 1)
                break

        self.assertEqual(item.itemId, 2666)

    def test_courpse_to_corpse_specific_stack(self):
        """ Bug #78 """

        # Set meat to 100%.
        wolf = getMonster("Wolf")
        if not wolf.prepared:
            wolf.prepare()

        for loot in wolf.lootTable:
           if loot[0] == 2666:
               loot[1] = 100.0

        # Spawn and kill two wolfs
        position1 = self.player.positionInDirection(NORTH)
        position2 = self.player.positionInDirection(SOUTH)

        wolf1 = wolf.spawn(position1, spawnDelay=0)
        wolf2 = wolf.spawn(position2, spawnDelay=0)

        wolf1.modifyHealth(-1000)
        wolf2.modifyHealth(-1000)

        # Get the corpses.
        corpse1 = position1.getTile().findItem(wolf.data["corpse"])
        corpse2 = position2.getTile().findItem(wolf.data["corpse"])

        # Open corpses.
        self.player.use(corpse1)
        self.player.use(corpse2)

        # Find meat and move from corpse1 to corpse2.
        for index in xrange(len(corpse1.container)):
            if corpse1.container[index].itemId == 2666:
                break

        for index2 in xrange(len(corpse2.container)):
            if corpse2.container[index].itemId == 2666:
                break

        # Move
        self.assertTrue(moveItem(self.player, Position(0xFFFF, 64, index), Position(0xFFFF, 65, index2)))

        # Find new meat.
        for item in corpse2.container:
            if item.itemId == 2666:
                self.assertGreater(item.count, 1)
                break

        self.assertEqual(item.itemId, 2666)

