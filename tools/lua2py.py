import re

from xml.dom.minidom import parse

fileName = raw_input("File: ")
file = open(fileName).read()

dom = parse("actions.xml")
list = []
for element in dom.getElementsByTagName("action"):
        if element.getAttribute("script") == fileName:
                list.append(int(element.getAttribute("itemid")))

lenRe = re.compile(r"#(?P<a>[^)]*)")
file = lenRe.sub(r"len(\g<a>)-1", file)
file = file.replace("local ", "").replace(" then", ":").replace(" true", " True").replace(" false", " False").replace(" .. ", " + ").replace("-- ", "# ").replace("elseif", "elif").replace("else", "else:")
newcode = ""
level = 0
regLine = ""
if file.count("item2") >= 2 or file.count("topos") >= 2:
    file = file.replace("onUse(cid, item, frompos, item2, topos)", "onUseWith(creature, thing, position, stackpos, onThing, onPosition, onStackpos, **k)")
    try:
        regLine = 'reg("useWith", %s, onUseWith)' % tuple(list)
    except:
        regLine = 'reg("useWith", %s, onUseWith)' % repr(tuple(list))
else:
    file = file.replace("onUse(cid, item, frompos, item2, topos)", "onUse(creature, thing, position, stackpos, **k)")
    regLine = 'reg("use", %s, onUse)' % tuple(list)
    
file = file.replace("math.random", "random.randint").replace("doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, ", "creature.message(")
file = file.replace("doDecayItem(item2.uid)", "onThing.decay(onPosition)")
file = file.replace("doDecayItem(item.uid)", "thing.decay(position)").replace("doSendMagicEffect(getThingPos(item2.uid), ", "magicEffect(onPosition, ")
file = file.replace("doSendMagicEffect(getThingPos(item.uid)", "magicEffect(position").replace(".itemid", ".itemId").replace("CONST_ME", "EFFECT").replace("doRemoveItem(item2.uid)", "creature.removeItem(onPosition, onStackpos)")
file = file.replace("doRemoveItem(item.uid)", "creature.removeItem(position, stackpos)").replace("getCreatureName(cid)", "creature.name()").replace(" ~= ", " != ").replace("doSendMagicEffect(frompos, ", "creature.magicEffect(")
file = file.replace("TALKTYPE_ORANGE_1", "'MSG_SPEAK_MONSTER_SAY'").replace("doPlayerSay(cid, ", "creature.say(").replace("doCreatureSay(cid, ", "creature.say(").replace("doPlayerSendCancel(cid, ", "creature.message(").replace("doPlayerAddHealth(cid, ", "creature.modifyHealth(")
file = file.replace("doRemoveItem(item.uid, ", "creature.modifyItem(thing, position, stackpos, -").replace("doRemoveItem(item2.uid, ", "creature.modifyItem(onThing, onPosition, onStackpos, -")
file = file.replace("hasProperty(item2.uid, CONST_PROP_BLOCKSOLID)", "onThing.solid").replace("hasProperty(item.uid, CONST_PROP_BLOCKSOLID)", "thing.solid")
file = file.replace("isCreature(item2.uid)", "onThing.isCreature()").replace("isPlayer(item2.uid)", "onThing.isPlayer()").replace("isMonster(item2.uid)", "onThing.isMonster()").replace("isItem(item2.uid)", "onThing.isItem()")
file = file.replace("getThingPos(cid)", "creature.position").replace(".x", "[0]").replace(".y", "[1]").replace(".z", "[2]").replace("CONTAINER_POSITION", "0xFFFF")
file = file.replace("item2.uid == cid", "onThing == creature").replace("doPlayerSendDefaultCancel(cid, RETURNVALUE_YOUAREEXHAUSTED)", "creature.exhausted()").replace("== true", "")
file = file.replace("getPlayerLevel(cid)", 'creature.data["level"]').replace("hasCondition(cid, ", "creature.hasCondition(").replace("getPlayerPosition(cid)", "creature.position").replace("getPlayerHealth(cid)", 'creature.data["health"]').replace("getPlayerMaxHealth(cid)", 'creature.data["healthmax"]')
file = file.replace("getPlayerName(cid)", "creature.name()").replace("getCreaturePos(pos)", "creature.position").replace("getPlayerMoney(cid)", "creature.getMoney()")
file = file.replace("doPlayerAddLevel(cid, ", "creature.modifyLevel(").replace("doPlayerRemoveLevel(cid, ", "creature.modifyLevel(-").replace("doPlayerSendCancel(cid, ", "creature.cancelMessage(").replace("ITEM_GOLD_COIN", "2148").replace("ITEM_PLATINUM_COIN", "2152")
file = file.replace("doPlayerSendDefaultCancel(cid, RETURNVALUE_NOTENOUGHLEVEL)", "creature.notEnough('level')").replace("doPlayerSendDefaultCancel(cid, RETURNVALUE_NOTENOUGHMANA)", "creature.notEnough('mana')").replace("doPlayerSendDefaultCancel(cid, RETURNVALUE_NOTENOUGHSOUL)", "creature.notEnough('soul')")
file = file.replace("getPlayerSoul(cid)", 'creature.data["soul"]').replace("getPlayerMana(cid)", 'creature.data["mana"]').replace("isPremium(cid)", "creature.isPremium()").replace("doPlayerSendDefaultCancel(cid, RETURNVALUE_YOUNEEDPREMIUMACCOUNT)", "creature.needPremium()")
file = file.replace("doPlayerAddMana(cid, ", "creature.modifyMana(").replace("doPlayerAddSoul(cid, ", "creature.modifySoul(").replace(" <> ", " != ").replace("doSendMagicEffect(topos, ", "magicEffect(onPosition, ")
inArrayRe = re.compile(r"isInArray\((?P<a>[^,]*), (?P<b>[^)]*)\)", re.I)
file = inArrayRe.sub(r"\g<b> in \g<a>", file)



inArrayRe2 = re.compile(r"(?P<a>\w+)\[(?P<b>[a-zA-Z0-9_.]*)\] == nil")
file = inArrayRe2.sub(r"\g<b> not in \g<a>", file)

inArrayRe3 = re.compile(r"(?P<a>\w+)\[(?P<b>[a-zA-Z0-9_.]*)\] != nil")
file = inArrayRe3.sub("\g<a> in \g<b>", file)

getItemName = re.compile(r"getItemName\((?P<arg>\w+)\)", re.I)
file = getItemName.sub("\g<arg>.rawName()", file)

transformItem = re.compile(r"doTransformItem\(item\.uid, (?P<to>[^,]*)\)")
file = transformItem.sub(r"thing.transform(\g<to>, position)", file)

transformItem = re.compile(r"doTransformItem\(item2\.uid, (?P<to>[^,]*)\)")
file = transformItem.sub(r"onThing.transform(\g<to>, onPosition)", file)

transformItem = re.compile(r"doTransformItem\(item\.uid, (?P<to>[^,]*), (?P<count>\w+)\)")
file = transformItem.sub(r"\nthing.count = \g<count>\nthing.transform(\g<to>, position)", file)

transformItem = re.compile(r"doTransformItem\(item2\.uid, (?P<to>[^,]*), (?P<count>\w+)\)")
file = transformItem.sub(r"\nonThing.count = \g<count>\nonThing.transform(\g<to>, onPosition)", file)

arrays = re.compile(r"\[(?P<a>\w+)\]([ \t]*)=([ \t]*)")
file = arrays.sub("\g<a>: ", file)

arrays = re.compile(r"\{(?P<a>[0-9, ]+)\},", re.M)
file = arrays.sub(r"(\g<a>),\\", file)

arrays = re.compile(r"\{(?P<a>[0-9, ]+)\}", re.M)
file = arrays.sub(r"(\g<a>)\\", file)

doChangeTypeItem = re.compile(r"doChangeTypeItem\((?P<item>\w+)\.uid, (?P<type>[^)]+)\)")
file = doChangeTypeItem.sub("\g<item>.type = \g<type>", file)

doSetItemSpecialDescription = re.compile(r"doSetItemSpecialDescription\((?P<item>\w+)\.uid, (?P<type>[^)]+)\)")
file = doSetItemSpecialDescription.sub("\g<item>.description = \g<type>", file)

doSetItemActionId = re.compile(r"doSetItemActionId\((?P<item>\w+)\.uid, (?P<type>[^)]+)\)")
file = doSetItemActionId.sub("\g<item>.actions.append('\g<type>')", file)

doPlayerAddItem = re.compile(r"doPlayerAddItem\(cid, (?P<item>\w+), (?P<count>\w+)\)")
file = doPlayerAddItem.sub("creature.addItem(Item(\g<item>, \g<count>))", file)

doPlayerAddItem = re.compile(r"doPlayerAddItem\(cid, (?P<item>\w+)\)")
file = doPlayerAddItem.sub("creature.addItem(Item(\g<item>))", file)

doCreateItem = re.compile(r"doCreateItem\((?P<item>\w+), (?P<count>\w+), (?P<pos>\w+)\)")
file = doCreateItem.sub("placeItem(Item(\g<item>, \g<count>), \g<pos>)", file)

file = file.replace("item.", "thing.").replace("item2", "onThing").replace("frompos", "position").replace("topos", "onPosition").replace("{\n", "{\\\n")
file = file.replace(" ~= nil", "").replace("nil", "None")

skipNext = 0
for line in file.split("\n"):
    if skipNext:
        skipNext -= 1
        continue
    
    line = line.strip()
    thislevel = level
    if line == "end":
        level -= 1
        continue
    elif line[:9] == "function ":
        newcode += "def %s:\n" % (line[9:])
        level += 1
        continue
    elif line == "if onThing.actionid != 0:" or line == "if thing.actionid != 0:" or line == "if onThing.actionid ~= 0:" or line == "if thing.actionid ~= 0:":
        skipNext = 2
        continue
    elif line[:2] == "if":
        level += 1
    elif line[:4] == "elif":
        thislevel -= 1
    elif line[:5] == "else:":
        thislevel -= 1

    newcode += "%s%s\n" % ("    "*thislevel, line)

# Finalize by doing a bit of a cleanup
doSetItemActionId = re.compile(r"(?P<item>\w+)\.actionid == (?P<type>\w+)")
file = doSetItemActionId.sub("'\g<type>' in \g<item>.actions", file)

doSetItemActionId = re.compile(r"(?P<item>\w+)\.actionid != (?P<type>\w+)")
file = doSetItemActionId.sub("'\g<type>' not in \g<item>.actions", file)

ifs = re.compile(r"(?P<type>(if|elif))([ \t]*)\((?P<param>(.*?))\)([ \t]*):", re.M)
newcode = ifs.sub(r"\g<type> \g<param>:", newcode).replace(" :\n", ":\n").replace("'0' not in ", "not ")

print newcode + "\n" + regLine
raw_input()