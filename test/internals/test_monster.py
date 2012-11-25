from test.framework import FrameworkTestGame

class TestMonster(FrameworkTestGame):
    def test_corpses(self):
        for monsterName in game.monster.monsters:
            monster = getMonster(monsterName)
            if not monster.data['corpse']:
                sys.__stdout__.write("[ERROR] Monster %s got no corpse!\n" % monsterName)
                #self.fail("%s got no corpse!" % monsterName)
            corpse = monster.data['corpse']
            item = Item(corpse)
            if not item.containerSize:
                sys.__stdout__.write("[WARNING] Monster %s (corpse: %d) is not a container. Likely invalid\n" % (monsterName, corpse))
            if not item.name:
                sys.__stdout__.write("[WARNING] Monster %s (corpse: %d) doesn't have a name, likely invalid\n" % (monsterName, corpse))
            elif not "dead" in item.name:
                sys.__stdout__.write("[WARNING] Monster %s (corpse: %d) doesn't have dead in it's name, likely invalid\n" % (monsterName, corpse))
