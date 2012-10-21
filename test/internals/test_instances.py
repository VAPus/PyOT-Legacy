from test.framework import FrameworkTestGame

class TestInstances(FrameworkTestGame):
    def init(self):
        # Turn off protection zones.
        self.overrideConfig("protectedZones", False)
    
    def test_newinstance(self):
        # Make a instance.
        instanceId = game.map.newInstance()
        self.assertNotEqual(instanceId, None)
        self.assertIn(instanceId, game.map.instances)
        
    def test_loadmap(self):
        instanceId = game.map.newInstance()
        Position(1000,1000,7, instanceId).getTile() # Loads.
        
        self.assertIn(instanceId, game.map.knownMap)
        
    def test_cansee(self):
        # Make a item
        item  = Item(7449)
        
        # Place on a instance.
        instanceId = game.map.newInstance()
        position = Position(1000,1001,7,instanceId)
        
        item.place(position)
        
        self.assertFalse(self.player.canSee(position))
        
    def test_cansee_reverse(self):
        # Make a item
        item  = Item(7449)
        
        # Place on a default
        instanceId = game.map.newInstance()
        position = Position(1000,1001,7)
        
        item.place(position)
        
        self.player.setInstance(instanceId)
        self.assertFalse(self.player.canSee(position))