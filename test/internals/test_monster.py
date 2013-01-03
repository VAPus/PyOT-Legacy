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
            if not item.name:
                printer("[WARNING] Monster %s (corpse: %d) doesn't have a name, likely invalid\n" % (monsterName, corpse))

            else:
                name = item.name.lower()
                if not "dead" in name and not "slain" in name and not "undead" in name and not "remains" in name:
                    printer("[WARNING] Monster %s (corpse: %d) doesn't have dead/slain/undead/remains in it's name, likely invalid\n" % (monsterName, corpse))
