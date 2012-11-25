from test.framework import FrameworkTestGame

class TestMonster(FrameworkTestGame):
    def test_corpses(self):
        printer = self.fail
        #printer = sys.__stdout__.write
        for monsterName in game.monster.monsters:
            monster = getMonster(monsterName)
            if not monster.data['corpse']:
                printer("[ERROR] Monster %s got no corpse!\n" % monsterName)
                continue
            corpse = monster.data['corpse']
            item = Item(corpse)
            if not item.containerSize:
                printer("[WARNING] Monster %s (corpse: %d) is not a container. Likely invalid\n" % (monsterName, corpse))
            if not item.name:
                printer("[WARNING] Monster %s (corpse: %d) doesn't have a name, likely invalid\n" % (monsterName, corpse))
            elif not "dead" in item.name:
                printer("[WARNING] Monster %s (corpse: %d) doesn't have dead in it's name, likely invalid\n" % (monsterName, corpse))
