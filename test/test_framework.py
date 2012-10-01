import framework

# Test if the framework is even working
class TestFramework(framework.FrameworkTest):
    def test_hasClient(self):
        assert self.client
        
    def test_isConnected(self):
        assert self.tr.connected
        
    def test_canReadWrite(self):
        self.tr.sendPacket('bb', 0, 0)
        assert self.tr.value()
        assert self.client._data