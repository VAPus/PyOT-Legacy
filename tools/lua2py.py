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
file = file.replace("local ", "").replace(" then", ":").replace("else", "else:").replace(" true", " True").replace(" false", " False").replace(" .. ", " + ").replace("-- ", "# ").replace("else if", "elif")
newcode = ""
level = 0
regLine = ""
if file.count("item2") >= 2 or file.count("topos") >= 2:
    file = file.replace("onUse(cid, item, frompos, item2, topos)", "onUseWith(creature, thing, position, onThing, onPosition)")
    regLine = 'reg("useWith", %s, onUseWith)' % tuple(list)
else:
    file = file.replace("onUse(cid, item, frompos, item2, topos)", "onUse(creature, thing, position)")
    regLine = 'reg("use", %s, onUse)' % tuple(list)
    
file = file.replace("math.random", "random.randint").replace("doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, ", "creature.message(")
file = file.replace("doDecayItem(item2.uid)", "onThing.decay(onPosition)")
file = file.replace("doDecayItem(item.uid)", "thing.decay(position)").replace("doSendMagicEffect(getThingPos(item2.uid), ", "magicEffect(onPosition, ")
file = file.replace("doSendMagicEffect(getThingPos(item.uid)", "magicEffect(position").replace(".itemid", ".itemId").replace("CONST_ME", "EFFECT").replace("doRemoveItem(item2.uid)", "creature.removeItem(onPosition, onStackpos)")
file = file.replace("doRemoveItem(item.uid)", "creature.removeItem(position, stackpos)").replace("getCreatureName(cid)", "creature.name()").replace(" ~= ", " != ").replace("doPlayerAddItem(cid, ", "creature.addItem(Item(").replace("doSendMagicEffect(frompos, ", "creature.magicEffect(")
file = file.replace("TALKTYPE_ORANGE_1", "'MSG_SPEAK_MONSTER_SAY'").replace("doPlayerSay(cid, ", "creature.say(").replace("doPlayerSendCancel(cid, ", "creature.message(").replace("doPlayerAddHealth(cid, ", "creature.modifyHealth(")
file = file.replace("doRemoveItem(item.uid, ", "creature.modifyItem(thing, position, stackpos, -").replace("doRemoveItem(item2.uid, ", "creature.modifyItem(onThing, onPosition, onStackpos, -")

inArrayRe = re.compile(r"isInArray\((?P<a>[^,]*), (?P<b>[^,]*)\)", re.I)
file = inArrayRe.sub(r"\g<b> in \g<a>", file)



inArrayRe2 = re.compile(r"(?P<a>\w+)\[(?P<b>[a-zA-Z0-9_.]*)\] == nil")
file = inArrayRe2.sub(r"\g<b> not in \g<a>", file)

inArrayRe3 = re.compile(r"(?P<a>\w+)\[(?P<b>[a-zA-Z0-9_.]*)\] != nil")
file = inArrayRe3.sub("\g<a> in \g<b>", file)

getItemName = re.compile(r"getItemName\((?P<arg>\w+)\)", re.I)
file = getItemName.sub("\g<arg>.rawName()", file)

transformItem = re.compile(r"doTransformItem\(item.uid, (?P<to>[a-zA-Z0-9_.]*)\)")
file = transformItem.sub(r"thing.transform(\g<to>, position)", file)

transformItem = re.compile(r"doTransformItem\(item2.uid, (?P<to>[a-zA-Z0-9_.]*)\)")
file = transformItem.sub(r"onThing.transform(\g<to>, onPosition)", file)

arrays = re.compile(r"\[(?P<a>\w+)\] = ")
file = arrays.sub("\g<a>: ", file)

arrays = re.compile(r"\{(?P<a>[0-9, ]+)\},", re.M)
file = arrays.sub(r"(\g<a>),\\", file)

arrays = re.compile(r"\{(?P<a>[0-9, ]+)\}", re.M)
file = arrays.sub(r"(\g<a>)\\", file)



file = file.replace("item.", "thing.").replace("item2", "onThing").replace("frompos", "position").replace("topos", "onPosition").replace("{\n", "{\\\n")
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
    elif line == "if onThing.actionid != 0:" or line == "if thing.actionid != 0:":
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
ifs = re.compile(r"(?P<type>(if|elif)) \((?P<param>.*)\):", re.M)
newcode = ifs.sub(r"\g<type> \g<param>:", newcode)

print newcode + "\n" + regLine