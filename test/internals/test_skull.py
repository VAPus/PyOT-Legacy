from .. import framework

class TestAttackSkulls(framework.FrameworkTestGame):
    def init(self):
        # Turn off protection zones.
        self.overrideConfig("protectedZones", False)
        
    def test_yellowskull(self):
        # Create player to attack.
        target = self.setupPlayer()
        
        # Set target
        # Avoid auto attacks.
        self.player.target = target
        self.player.targetMode = 1
        
        # Give him a white skull.
        target.setSkull(SKULL_WHITE)

        # He is white right?
        self.assertEqual(target.getSkull(self.player), SKULL_WHITE)
        
        # Ignore blocking.
        self.player.ignoreBlock = True
        
        # We're suppose to have no skull to begin with.
        self.assertFalse(self.player.getSkull(target))
        
        # Damage him
        self.player.attackTarget(-10)
        self.assertEqual(self.player.getSkull(target), SKULL_YELLOW)
        
    def test_whiteskull(self):
        # Create player to attack.
        target = self.setupPlayer()
        
        # Set target
        # Avoid auto attacks.
        self.player.target = target
        self.player.targetMode = 1
        
        # Ignore blocking.
        self.player.ignoreBlock = True
        
        # Damage him
        self.player.attackTarget(-10)
        
        self.assertEqual(self.player.getSkull(target), SKULL_WHITE)
        
    def test_orangeskull(self):
        # Create player to attack.
        target = self.setupPlayer()
        
        # Set target
        # Avoid auto attacks.
        self.player.target = target
        self.player.targetMode = 1

        # Ignore blocking.
        self.player.ignoreBlock = True
        
        # Kill him.
        self.player.attackTarget(-1000)
        self.assertFalse(target.alive)
        
        self.assertEqual(self.player.getSkull(None), SKULL_WHITE)
        
        # Remove white skull.
        self.player.setSkull(SKULL_NONE)
        
        # Respawn.
        target.onSpawn()

        
        # 
        self.assertTrue(self.player.data["id"] in deathlist.byKiller)
        self.assertEqual(self.player.getSkull(target), SKULL_ORANGE)           