addons = game.npc.genNPC("Addons", (130, 39, 122, 125, 37, 2212))
addons.setWalkable(False)
outfits=('Citizen', 'Hunter', 'Mage', 'Knight', 'Warrior', 'Summoner', 'Nobleman', 'Oriental', 'Wizard', 'Assassin', 'Beggar', 'Shaman', 'Barbarian', 'Druid', 'Pirate', 'Norseman', 'Jester', 'Brotherhood', 'Hunter', 'Yalaharian', 'Newly Wed', 'Warmaster', 'Wayfarer', 'Elementalist', 'Afflicted')

addons.greet("Greetings %(playerName)s.. Will you help me? If you do, I'll reward you with nice addons! Just say {addon} if you don't know what to do.")
class Addon(game.npc.ClassAction):
    def action(self):
        self.on.onSaid('addon', self.test)
    def test(self, npc, player):
        npc.sayTo(player, "I can give you citizen, hunter, knight, mage, nobleman, summoner, warrior, barbarian, druid, wizard, oriental, pirate, assassin,beggar, shaman, norseman, nighmare, jester, yalaharian and brotherhood addons.")
        word = yield
        word =word.title()
        print(word)
        if word in outfits:
            player.addOutfit(word)            
            npc.sayTo(player, "Now you can wear %s outfit"  % word)
        npc.sayTo(player, "You may say {addon} to get another one or {bye}.")
addons.module(Addon)