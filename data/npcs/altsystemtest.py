AltSystemTest = game.npc.genNPC("AltSystemTest", (130, 39, 122, 125, 37, 2212), "AltSystemTest the test char")
AltSystemTest.setWalkable(False)


AltSystemTest.speakTree({"Hello, what do you want?":
    {"icecream":
        {"What flavour?":
            {"chocolate": ("Here you go!", lambda player, **k: player.say("Yum!") ),
            "!": "We don't serve that, sorry!",
            }
        }
    }
})