import re

from xml.dom.minidom import parse

import argparse
parser = argparse.ArgumentParser(description='Process a script')
parser.add_argument('script', metavar='<script>', type=str, help='A script')
                   
args = parser.parse_args()
if args.script:
    fileName = args.script
else:
    fileName = raw_input("File: ")
file = open(fileName).read()

dom = parse("actions.xml")
list = []
for element in dom.getElementsByTagName("action"):
        if element.getAttribute("script").split("/")[-1] == fileName or element.getAttribute("value").split("/")[-1] == fileName:
            try:
                list.append(int(element.getAttribute("itemid")))
            except:
                for i in range(int(element.getAttribute("fromid")), int(element.getAttribute("toid"))+1):
                    list.append(i)

file = file.replace("math.random(1, #", "math.random(0, #")
lenRe = re.compile(r"#(?P<a>[^)]*)")
file = lenRe.sub(r"len(\g<a>)-1", file)
file = file.replace("local ", "").replace(" then", ":").replace(" true", " True").replace(" false", " False").replace(" .. ", " + ").replace("-- ", "# ").replace("elseif", "elif").replace("else", "else:").replace("itemEx", "item2").replace("fromPosition", "frompos").replace("toPosition", "topos")
newcode = ""
level = 0
regLine = ""
if file.find("onUse"):
    if file.count("item2") >= 2 or file.count("topos") >= 2:
        file = file.replace("onUse(cid, item, frompos, item2, topos)", "onUseWith(creature, thing, position, stackpos, onThing, onPosition, onStackpos, **k)")
        try:
            regLine = 'reg("useWith", %s, onUseWith)' % tuple(list)
        except:
            regLine = 'reg("useWith", %s, onUseWith)' % repr(tuple(list))
    else:
        file = file.replace("onUse(cid, item, frompos, item2, topos)", "onUse(creature, thing, position, stackpos, **k)")
        try:
            regLine = 'reg("use", %s, onUse)' % tuple(list)
        except:
            regLine = 'reg("use", %s, onUse)' % repr(tuple(list))

if file.find("onEquip"):
    file = file.replace("onEquip(cid, item, slot)", "onEquip(creature, thing, slot, **k)")
    try:
        regLine = regLine + 'reg("equip", %s, onEquip)' % tuple(list)
    except:
        regLine = regLine + 'reg("equip", %s, onEquip' % repr(tuple(list))
            
if file.find("onDeEquip"):
    file = file.replace("onDeEquip(cid, item, slot)", "unEquip(creature, thing, slot, **k)")
    try:
        regLine = regLine + 'reg("unEquip", %s, unEquip)' % tuple(list)
    except:
        regLine = regLine + 'reg("unEquip", %s, unEquip)' % repr(tuple(list))
            
if file.find("onStepIn"):
    file = file.replace("onStepIn(cid, item, position, fromPosition)", "walkOn(creature, thing, position, fromPosition, **k)")
    try:
        regLine = regLine + 'reg("walkOn", %s, walkOn)' % tuple(list)
    except:
        regLine = regLine + 'reg("walkOn", %s, walkOn)' % repr(tuple(list))

if file.find("onStepOut"):
    file = file.replace("onStepOut(cid, item, position, fromPosition)", "walkOff(creature, thing, position, fromPosition, **k)")
    try:
        regLine = regLine + 'reg("walkOff", %s, walkOff)' % tuple(list)
    except:
        regLine = regLine + 'reg("walkOff", %s, walkOff)' % repr(tuple(list))
        
file = file.replace("math.random", "random.randint").replace("doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, ", "creature.message(")
file = file.replace("doDecayItem(item2.uid)", "onThing.decay(onPosition)")
file = file.replace("doDecayItem(item.uid)", "thing.decay(position)").replace("doSendMagicEffect(", "magicEffect(").replace("getThingPos(item2.uid)", "onPosition").replace("getThingPos(item.uid)", "position")
file = file.replace("doSendMagicEffect(getThingPos(item.uid)", "magicEffect(position").replace(".itemid", ".itemId").replace("CONST_ME", "EFFECT").replace("doRemoveItem(item2.uid)", "creature.removeItem(onPosition, onStackpos)")
file = file.replace("doRemoveItem(item.uid)", "creature.removeItem(position, stackpos)").replace("getCreatureName(cid)", "creature.name()").replace("getCreatureName(item2.uid)", "onThing.name()").replace("getCreatureName(item.uid)", "thing.name()").replace(" ~= ", " != ").replace("doSendMagicEffect(frompos, ", "creature.magicEffect(")
file = file.replace("TALKTYPE_ORANGE_1", "'MSG_SPEAK_MONSTER_SAY'").replace("TALKTYPE_MONSTER", "'MSG_SPEAK_MONSTER_SAY'").replace("doPlayerSay(cid, ", "creature.say(").replace("doCreatureSay(cid, ", "creature.say(").replace("doCreatureSay(item2.uid, ", "onThing.say(").replace("doPlayerSendCancel(cid, ", "creature.message(").replace("doPlayerAddHealth(cid, ", "creature.modifyHealth(")
file = file.replace("doRemoveItem(item.uid, ", "creature.modifyItem(thing, position, stackpos, -").replace("doRemoveItem(item2.uid, ", "creature.modifyItem(onThing, onPosition, onStackpos, -").replace("doPlayerRemoveItem(item.uid, ", "creature.modifyItem(thing, position, stackpos, -").replace("doPlayerRemoveItem(item2.uid, ", "creature.modifyItem(onThing, onPosition, onStackpos, -")
file = file.replace("hasProperty(item2.uid, CONST_PROP_BLOCKSOLID)", "onThing.solid").replace("hasProperty(item.uid, CONST_PROP_BLOCKSOLID)", "thing.solid")
file = file.replace("isCreature(item2.uid)", "onThing.isCreature()").replace("isPlayer(item2.uid)", "onThing.isPlayer()").replace("isMonster(item2.uid)", "onThing.isMonster()").replace("isItem(item2.uid)", "onThing.isItem()")
file = file.replace("getThingPos(cid)", "creature.position").replace("CONTAINER_POSITION", "0xFFFF")
file = file.replace("item2.uid == cid", "onThing == creature").replace("doPlayerSendDefaultCancel(cid, RETURNVALUE_YOUAREEXHAUSTED)", "creature.exhausted()").replace("== true", "")
file = file.replace("getPlayerLevel(cid)", 'creature.data["level"]').replace("hasCondition(cid, ", "creature.hasCondition(").replace("getPlayerPosition(cid)", "creature.position").replace("getPlayerHealth(cid)", 'creature.data["health"]').replace("getPlayerMaxHealth(cid)", 'creature.data["healthmax"]')
file = file.replace("getPlayerName(cid)", "creature.name()").replace("getCreaturePos(pos)", "creature.position").replace("getPlayerMoney(cid)", "creature.getMoney()")
file = file.replace("doPlayerAddLevel(cid, ", "creature.modifyLevel(").replace("doPlayerRemoveLevel(cid, ", "creature.modifyLevel(-").replace("doPlayerSendCancel(cid, ", "creature.cancelMessage(").replace("ITEM_GOLD_COIN", "2148").replace("ITEM_PLATINUM_COIN", "2152")
file = file.replace("doPlayerSendDefaultCancel(cid, RETURNVALUE_NOTENOUGHLEVEL)", "creature.notEnough('level')").replace("doPlayerSendDefaultCancel(cid, RETURNVALUE_NOTENOUGHMANA)", "creature.notEnough('mana')").replace("doPlayerSendDefaultCancel(cid, RETURNVALUE_NOTENOUGHSOUL)", "creature.notEnough('soul')")
file = file.replace("getPlayerSoul(cid)", 'creature.data["soul"]').replace("getPlayerMana(cid)", 'creature.data["mana"]').replace("isPremium(cid)", "creature.isPremium()").replace("doPlayerSendDefaultCancel(cid, RETURNVALUE_YOUNEEDPREMIUMACCOUNT)", "creature.needPremium()")
file = file.replace("doPlayerAddMana(cid, ", "creature.modifyMana(").replace("doPlayerAddSoul(cid, ", "creature.modifySoul(").replace(" <> ", " != ").replace("doSendMagicEffect(topos, ", "magicEffect(onPosition, ")
file = file.replace("getCreaturePosition(cid)", "creature.position").replace("return False", "return").replace("getPlayerVocation(cid)", "creature.getVocationId()")
file = file.replace("for _,", "for").replace("for i,", "for") # TFS specific, properly fixed down below
file = file.replace("CONST_", "") # TFS constants
file = file.replace('"no",', "False,").replace('"yes",', "True,").replace("getPlayerFreeCap(cid)", "creature.freeCapasity()").replace("getHouseFromPos(", "getHouseId(")
file = file.replace("doPlayerSendDefaultCancel(cid, RETURNVALUE_NOTPOSSIBLE)", "creature.notPossible()").replace("getCreatureSkullType(cid)", "creature.skull")
file = file.replace("isNpc(item.uid)", "thing.isNPC()").replace("isNpc(item2.uid)", "onThing.isNPC()").replace("doPlayerSendTextMessage(cid, MESSAGE_STATUS_CONSOLE_ORANGE, ", "creature.orangeStatusMessage(")
file = file.replace("isSummon(item.uid)", "thing.isSummon()").replace("isSummon(item2.uid)", "onThing.isSummon()").replace("doPlayerSetExperienceRate(cid, ", "creature.setExperienceRate(").replace("getPlayerTown(cid)", 'creature.data["town_id"]')

lists = re.compile(r"{(?P<params>[^={}]+)}")
file = lists.sub("[\g<params>]", file)

possibleKeys = []

badKeys = attributes = ('solid','blockprojectile','blockpath','usable','pickable','movable','stackable','ontop','hangable','rotatable','animation', 'itemId', 'actions')
# This is my dict builder
def dictBuilder(m):
    text = m.group("params")
    # Resursive:
    text = re.sub(r"{(?P<params>.+)}", dictBuilder, text)
    parts = re.split(r"""(\w+ = \[[^]]*\])|(\w+ = \"[^"]*\")|, """, text)
    toInsert = []
    for part in parts:
        if part:
            key, value = part.split(" = ")
            try:
                key = "%d" % int(key) # number
            except:
                if not key.isupper() and "[" not in key: # Don't do constants or lists
                    if not key in possibleKeys:
                        possibleKeys.append(key)
                    key = '"%s"' % key # string
                    
            toInsert.append("%s: %s" % (key, value))
    return "{%s}" % ', '.join(toInsert)
    
file = re.sub(r"{(?P<params>.+)}", dictBuilder, file, re.M|re.DOTALL)

for key in possibleKeys[:]:
    if key in badKeys:
        possibleKeys.remove(key)
    
inArrayRe = re.compile(r"isInArray\((?P<a>.*), (?P<b>.*)\)", re.I)
file = inArrayRe.sub(r"\g<b> in \g<a>", file)

inArrayRe2 = re.compile(r"(?P<a>\w+)\[(?P<b>[a-zA-Z0-9_().]*)\] == nil")
file = inArrayRe2.sub(r"\g<b> not in \g<a>", file)

inArrayRe3 = re.compile(r"(?P<a>\w+)\[(?P<b>[a-zA-Z0-9_().]*)\] != nil")
file = inArrayRe3.sub("\g<a> in \g<b>", file)

inArrayRe4 = re.compile(r"(!(=))(?P<a>\w+)\[(?P<b>[a-zA-Z0-9_().]*)\]")
file = inArrayRe4.sub("\g<a> in \g<b> and \g<b>[\g<a>]", file)



getItemName = re.compile(r"getItemName\((?P<arg>\w+)\)", re.I)
file = getItemName.sub("\g<arg>.rawName()", file)

transformItem = re.compile(r"doTransformItem\(item\.uid, (?P<to>[^,()]*)\)")
file = transformItem.sub(r"thing.transform(\g<to>, position)", file)

transformItem = re.compile(r"doTransformItem\(item2\.uid, (?P<to>[^,()]*)\)")
file = transformItem.sub(r"onThing.transform(\g<to>, onPosition)", file)

transformItem = re.compile(r"doTransformItem\(item\.uid, (?P<to>[^,()]*), (?P<count>\w+)\)")
file = transformItem.sub(r"\nthing.count = \g<count>\nthing.transform(\g<to>, position)", file)

transformItem = re.compile(r"doTransformItem\(item2\.uid, (?P<to>[^,()]*), (?P<count>\w+)\)")
file = transformItem.sub(r"\nonThing.count = \g<count>\nonThing.transform(\g<to>, onPosition)", file)

arrays = re.compile(r"\[(?P<a>\w+)\]([ \t]*)=([ \t]*)")
file = arrays.sub("\g<a>: ", file)

"""
arrays = re.compile(r"\{(?P<a>[0-9, ]+)\},", re.M)
file = arrays.sub(r"(\g<a>),\\", file)

arrays = re.compile(r"\{(?P<a>[0-9, ]+)\}", re.M)
file = arrays.sub(r"(\g<a>)\\", file)
"""

doChangeTypeItem = re.compile(r"doChangeTypeItem\((?P<item>\w+)\.uid, (?P<type>[^)]+)\)")
file = doChangeTypeItem.sub("\g<item>.type = \g<type>", file)

doSetItemSpecialDescription = re.compile(r"doSetItemSpecialDescription\((?P<item>\w+)\.uid, (?P<type>[^)]+)\)")
file = doSetItemSpecialDescription.sub("\g<item>.description = \g<type>", file)

doSetItemActionId = re.compile(r"doSetItemActionId\((?P<item>\w+)\.uid, (?P<type>[^)]+)\)")
file = doSetItemActionId.sub("\g<item>.actions.append('\g<type>')", file)

doPlayerAddItem = re.compile(r"doPlayerAddItem\(cid, (?P<item>[^,]+), (?P<count>\w+)\)")
file = doPlayerAddItem.sub("creature.addItem(Item(\g<item>, \g<count>))", file)

doPlayerAddItem = re.compile(r"doPlayerAddItem\(cid, (?P<item>[^,]+)\)")
file = doPlayerAddItem.sub("creature.addItem(Item(\g<item>))", file)

doCreateItem = re.compile(r"doCreateItem\((?P<item>[^,]+), (?P<count>[^,]+), (?P<pos>\w+)\)")
file = doCreateItem.sub("placeItem(Item(\g<item>, \g<count>), \g<pos>)", file)

getContainerSize = re.compile(r"getContainerSize\((?P<item>\w+).uid\)")
file = getContainerSize.sub("\g<item>.container.size()", file)

getContainerCap = re.compile(r"getContainerCap\((?P<item>\w+).uid\)")
file = getContainerCap.sub("\g<item>.containerSize", file)

getPlayerSlotItem = re.compile(r"getPlayerSlotItem\(cid,([ ]*)(?P<slot>\w+)\)")
file = getPlayerSlotItem.sub("creature.inventory[\g<slot>]", file)

doAddContainerItem = re.compile(r"doAddContainerItem\((?P<container>[^,]+).uid, (?P<item>[^,]+)\)")
file = doAddContainerItem.sub("creature.itemToContainer(\g<container>, Item(\g<item>)", file)

doAddContainerItem = re.compile(r"doAddContainerItem\((?P<container>[^,]+).uid, (?P<item>[^,]+), (?P<count>[^,]+)\)")
file = doAddContainerItem.sub("creature.itemToContainer(\g<container>, Item(\g<item>, \g<count>)", file)

ipairs = re.compile(r"ipairs\((?P<param>.*?)\)")
file = ipairs.sub("\g<param>", file)

forLoop = re.compile(r"for([ \t]+)(?P<val>\w+)([ \t]+)=([ \t]+)(\w+),([ \t]+)(?P<in>(.*?))")
file = forLoop.sub("for \g<val> in \g<in>", file)

forOverNumberic = re.compile(r"for (?P<var>\w+) in (?P<what>[^ ()\[\]]+) ")
file = forOverNumberic.sub("for \g<var> in range(\g<what>) ", file)

ifNone = re.compile(r"(?P<item>\w+).uid([ ]+)==([ ]+)")
file = ifNone.sub("not \g<item>", file)

doCreatureAddHealth = re.compile(r"do(Creature|Player)AddHealth\((?P<creature>[^,]+).uid, (?P<param>(.*))\)")
file = doCreatureAddHealth.sub("\g<creature>.modifyHealth(\g<param>)", file)

doCreatureAddMana = re.compile(r"do(Creature|Player)AddMana\((?P<creature>[^,]+).uid, (?P<param>(.*))\)")
file = doCreatureAddMana.sub("\g<creature>.modifyMana(\g<param>)", file)

getItemParent = re.compile(r"getItemParent\((?P<item>[^,]+).uid\)")
file = getItemParent.sub("\g<item>.inContainer", file)

getSpectators = re.compile(r"getSpectators\((?P<position>[^,]+), (?P<x>[^,]+), (?P<y>[^()]+)\)")
file = getSpectators.sub("getPlayers(\g<position>, (\g<x>, \g<y>))", file)

getContainerItem = re.compile(r"getContainerItem\((?P<container>[^,]+).uid, (?P<stackpos>(.*))\)") # Unsafe!
file = getContainerItem.sub("\g<container>.container.getThing(\g<stackpos>)", file)

getItemInfo = re.compile(r"getItemInfo\((?P<itemId>[^,]+)\)\.(?P<attr>\w+)")
file = getItemInfo.sub('itemAttribute(\g<itemId>, "\g<attr>")', file)

getConfigInfo = re.compile(r"""getConfigInfo\(('|")(?P<opt>\w+)('|")\)""")
file = getConfigInfo.sub("config.\g<opt>", file)

getConfigInfo = re.compile(r"""getConfigInfo\((?P<opt>[^() ]+)\)""")
file = getConfigInfo.sub('getattr(config, "\g<opt>")', file)

doAddCondition = re.compile(r"doAddCondition\((?P<creature>[^,]+), (?P<condition>[^,()]+)\)")
file = doAddCondition.sub("""\g<creature>.condition(<Add a PyOT compatible condition replacement for "\g<condition>" here ! >)""", file)

addEvent = re.compile(r"addEvent\((?P<callback>\w+), (?P<time>[^,]+)(?P<param>(.*))\)")
file = addEvent.sub("callLater(\g<time>/1000.0, \g<callback>\g<param>)", file)

doRemoveCreature = re.compile(r"doRemoveCreature\((?P<creature>[^,]+).uid\)")
file = doRemoveCreature.sub("\g<creature>.despawn()", file)

doPlayerAddMount = re.compile(r"doPlayerAddMount\(cid, (?P<id>[^,()]+)\)")
file = doPlayerAddMount.sub("creature.addMount(<Insert name of mount here to replace <'\g<id>'> >)", file)

getPlayerMount = re.compile(r"getPlayerMount\(cid, (?P<id>[^,()]+)\)")
file = getPlayerMount.sub("creature.canMount(<Insert name of mount here to replace <'\g<id>'> >)", file)

getTownTemplePosition = re.compile(r"getTownTemplePosition\((?P<param>(.*))\)")
file = getTownTemplePosition.sub("townPosition(\g<param>)", file)

isStackable = re.compile(r"isStackable\((?P<item>[^,]+).uid\)")
file = isStackable.sub("\g<item>.stackable", file)

isMoveable = re.compile(r"isMoveable\((?P<item>[^,]+).uid\)")
file = isMoveable.sub("\g<item>.moveable", file)

isSolid = re.compile(r"isSolid\((?P<item>[^,]+).uid\)")
file = isMoveable.sub("\g<item>.solid", file)

isHangable = re.compile(r"isHangable\((?P<item>[^,]+).uid\)")
file = isMoveable.sub("\g<item>.hangable", file)

# Do this last in case you convert some params before
dictKeyTransform = re.compile(r"(?P<name>(\w+))\.(?P<key>(%s))(?P<ending>(\)|\n|,| ))" % '|'.join(possibleKeys))
file = dictKeyTransform.sub("""\g<name>["\g<key>"]\g<ending>""", file)

file = file.replace("item.", "thing.").replace("item2", "onThing").replace("frompos", "position").replace("topos", "onPosition").replace("{\n", "{\\\n")
file = file.replace(" ~= nil", "").replace("nil", "None").replace(".x", "[0]").replace(".y", "[1]").replace(".z", "[2]").replace("cid", "creature").replace(".uid", "")

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
    elif line[:3] == "for":
        level += 1
        newcode += "%s%s:\n" % ("    "*thislevel, line[:-3])
        continue
    elif "= getBooleanFromString" in line:
        continue
    elif line[:2] == "--": # Ugly scripts
        line = "# %s" % line[2:]

    newcode += "%s%s\n" % ("    "*thislevel, line)

# Finalize by doing a bit of a cleanup
doSetItemActionId = re.compile(r"(?P<item>\w+)\.actionid == (?P<type>\w+)")
file = doSetItemActionId.sub("'\g<type>' in \g<item>.actions", file)

doSetItemActionId = re.compile(r"(?P<item>\w+)\.actionid != (?P<type>\w+)")
file = doSetItemActionId.sub("'\g<type>' not in \g<item>.actions", file)

ifs = re.compile(r"(?P<type>(if|elif))([ \t]*)\((?P<param>(.*?))\)([ \t]*):", re.M)
newcode = ifs.sub(r"\g<type> \g<param>:", newcode).replace(" :\n", ":\n").replace("'0' not in ", "not ")

print "# Autoconverted script for PyOT"
print "# Untested. Please remove this message when the script is working properly!\n"

print newcode + "\n" + regLine
raw_input()