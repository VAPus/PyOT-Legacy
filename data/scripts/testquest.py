import game.resource as resource
import game.scriptsystem as scriptsystem

# The quest itself
quest = resource.genQuest("The hello world")
quest.mission("Say hello world")
quest.description("Simply type 'hello world' to finish this quest")

# Some actions to deal with it
def startQuest(creature, **k):
    creature.say("Wow, a quest just began")
    creature.beginQuest("The hello world")
    
    return False

def endQuest(creature, **k):
    creature.finishQuest("The hello world")
    
scriptsystem.reg("talkaction", "begin quest", startQuest)
scriptsystem.reg("talkaction", "hello world", endQuest)



