# The quest itself
quest = game.resource.genQuest("The hello world")
quest.mission("Say hello world")
quest.description("Simply type 'hello world' to finish this quest")

# Some actions to deal with it
def startQuest(creature, **k):
    creature.say("Wow, a quest just began")
    creature.beginQuest("The hello world")
    
    return False

def endQuest(creature, **k):
    if creature.isPlayer() and creature.questStarted("The hello world") and not creature.questCompleted("The hello world"):
        creature.finishQuest("The hello world")
    
reg("talkaction", "begin quest", startQuest)
reg("talkaction", "hello world", endQuest)



