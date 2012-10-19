# The quest itself
quest = genQuest("The hello world")
quest.mission("Say hello world")
quest.description("Simply type 'hello world' to finish this quest")

# Some actions to deal with it
@register("talkaction", "begin quest")
def startQuest(creature, **k):
    creature.say("Wow, a quest just began")
    creature.beginQuest("The hello world")
    
    return False
    
@register("talkaction", "hello world")
def endQuest(creature, **k):
    if creature.isPlayer() and creature.questStarted("The hello world") and not creature.questCompleted("The hello world"):
        creature.finishQuest("The hello world")


# Another example quest, with missions this time

q = genQuest("The hunger games")
q.mission("Look at yourself.")
q.description("That's a pretty clear objective, no?")
q.mission("Look at the wolf.")
q.description("It isn't getting any harder, is it?")
q.mission("Look at the scorpion.")
q.description("You like forkfeeding, right?")


# Type 'missions quest' to start this quest.
# It doesn't check if you've already started or done it, so you can start over indefinately.

@register("talkaction", "missions quest")
def letsRoll(creature, **k):
    creature.say("Shit has just got serious, so I'll better check my questlog.")
    creature.beginQuest(qname) 
    return False

@register("lookAt", "creature")
def annoyingQuest(creature, thing, **k):
	p = creature
	qname = "The hunger games"
	
	if not p.questStarted(qname) or p.questCompleted(qname):
		return True
	
	if p == thing and p.questProgress(qname) == 0:
		p.say("I've just looked at myself. Mission accomplished!")
		p.progressQuest(qname)	# sets the mission as 'completed'
		p.progressQuestMission(qname)	# advances to next mission
	elif thing.name() == "Wolf" and p.questProgress(qname) == 1:
		p.say("I did it! I can do anything!")
		p.progressQuest(qname)
		p.progressQuestMission(qname)
	elif thing.name() == "Scorpion" and p.questProgress(qname) == 2:
		p.say("A hero like me is always there to save the day!")
		p.progressQuest(qname)
		p.finishQuest(qname)
	return True