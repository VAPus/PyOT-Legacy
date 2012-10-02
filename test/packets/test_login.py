from .. import framework

class TestLogin(framework.FrameworkTest):
    def test_login(self):
        packet = self.tr.sendPacket("bhhbsss", 0xFF, 0x00, 963, 0, "111", "Test", "111", ret=True)
        d = self.client.onFirstPacket(packet)
        def _(x):
            self.assertEqual(self.tr._packet.uint8(), 0x0A)
        d.addCallback(_)
        return d