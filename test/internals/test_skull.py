from .. import framework

class TestAttackSkulls(framework.FrameworkTestGame):
    def test_yellowskull(self):
        # Create player to attack.
        target = self.setupPlayer(random.randint(1, 0x7FFFF), "__TARGET__")
        
        # Set target
        # Avoid auto attacks.
        self.player.target = target
        self.player.targetMode = 1
        
        # Give him a white skull.
        target.setSkull(SKULL_WHITE)

        # Ignore blocking.
        self.player.ignoreBlock = True
        
        # Damage him
        self.player.attackTarget(10)
        
        self.assertEqual(self.player.getSkull(target), SKULL_YELLOW)
        
    def test_whiteskull(self):
        # Create player to attack.
        target = self.setupPlayer(random.randint(1, 0x7FFFF), "__TARGET2__")
        
        # Set target
        # Avoid auto attacks.
        self.player.target = target
        self.player.targetMode = 1
        
        # Ignore blocking.
        self.player.ignoreBlock = True
        
        # Damage him
        self.player.attackTarget(10)
        
        self.assertEqual(self.player.getSkull(), SKULL_WHITE)