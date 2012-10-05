from .. import framework

class TestRaiseMessages(framework.FrameworkTestGame):
    def init(self):
        # Turn off protection zones.
        self.overrideConfig("protectedZones", False)
            
    def test_raise(self):
        # Simplest test.
        # Turn on raise messages
        self.player.toggleRaiseMessages()

        self.assertRaises(MsgNotPossible, self.player.notPossible)

        self.player.toggleRaiseMessages()

    def test_unmarked(self):
        # Turn on raise messages
        self.player.toggleRaiseMessages()

        # Make target
        target = self.setupPlayer()

        # Make sure we got unmarked warnings on.
        self.player.modes[2] = True
                
        # Should raise MsgUnmarkedPlayer
        self.assertRaises(MsgUnmarkedPlayer, self.player.setAttackTarget, (target.cid))
        
        # Cleanup. Good practice.
        self.player.toggleRaiseMessages()
