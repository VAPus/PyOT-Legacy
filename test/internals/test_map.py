from test.framework import FrameworkTestGame

class TestMap(FrameworkTestGame):
    def test_settile(self):
        tile = game.map.Tile(Item(100), None)
        pos = Position(1001, 1000, 7)
        orgTile = pos.getTile()

        pos.setTile(tile)

        self.assertNotEqual(pos.getTile(), orgTile)
        self.assertEqual(pos.getTile(), tile)

        # Cleanup
        pos.setTile(orgTile)

    def test_copytile(self):
        pos = Position(1001, 1000, 7)
        orgTile = pos.getTile()
        copy = orgTile.copy()

        self.assertNotEqual(orgTile, copy)

        self.assertEqual(orgTile.flags, copy.flags)
        self.assertEqual(orgTile.ground.itemId, copy.ground.itemId)
