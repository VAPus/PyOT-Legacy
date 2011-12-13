************************************
  A TFS to PyOT script function map
************************************

:Author: Stian (:vapus:`members/stian`)
:Release: |release|
:Date: |today|

**NB! This page is work in progress!**

First some important class (type) names:
    **Creature** means it's part of any creature
    **Player** means it's only part of a player
    **Item** means it's a item

getCreatureHealth(cid) -> Creature.data["health"]
getCreatureMaxHealth(cid[, ignoreModifiers = false]) -> Creature.data["healthmax"]
getCreatureMana(cid) -> Player.data["mana"]
getCreatureMaxMana(cid[, ignoreModifiers = false]) -> Player.data["manamax"]
getCreatureHideHealth(cid) -> NOT IMPLANTED YET
doCreatureSetHideHealth(cid, hide) -> NOT IMPLANTED YET
getCreatureSpeakType(cid) -> NOT IMPLANTED YET
doCreatureSetSpeakType(cid, type) -> NOT IMPLANTED YET
getCreatureLookDirection(cid) -> Creature.direction
getPlayerLevel(cid) -> Player.data["level"]
getPlayerExperience(cid) -> Player.data["experience"]
getPlayerMagLevel(cid[, ignoreModifiers = false]) -> Player.data["maglevel"]
getPlayerSpentMana(cid) -> Player.data["manaspent"]
getPlayerFood(cid) -> No equalent (it's a Condition in PyOT so use Creature.getCondition())
getPlayerAccess(cid) -> PyOT doesn't have access levels, only access flags
getPlayerGhostAccess(cid) -> PyOT doesn't have access levels, only access flags
getPlayerSkillLevel(cid, skill[, ignoreModifiers = false]) -> Player.getActiveSkill(skill) (with modifiers) and Player.skill[skill] (without modifers)
getPlayerSkillTries(cid, skill) -> Player.getSkillAttempts(skill)
getPlayerTown(cid) -> Player.data["town_id"]
getPlayerVocation(cid) -> Player.getVocation() (for the vocation object), Player.getVocationId() (for the Id)
getPlayerIp(cid) -> Player.getIP()
getPlayerRequiredMana(cid, magicLevel) -> config.magicLevelFormula(magicLevel, Vocation.mlevel)
getPlayerRequiredSkillTries(cid, skillId, skillLevel) -> I'll get back on this one
getPlayerItemCount(cid, itemid[, subType = -1]) -> Player.itemCount(Item)
getPlayerMoney(cid) -> Player.getMoney()
getPlayerSoul(cid[, ignoreModifiers = false]) -> Player.data["soul"]
getPlayerFreeCap(cid) -> Player.freeCapasity()
getPlayerLight(cid) -> INVIDIDUAL PLAYER LIGHT NOT IMPLANTED
getPlayerSlotItem(cid, slot) -> Player.inventory[slot-1]
getPlayerWeapon(cid[, ignoreAmmo = false]) -> Player.inventory[SLOT_RIGHT-1]
getPlayerItemById(cid, deepSearch, itemId[, subType = -1]) -> Player.findItemById(itemId, count/subType)
getPlayerDepotItems(cid, depotid) -> Player.getDepot(depotId)

** part of the guild system, yet to be implanted **
getPlayerGuildId(cid)
getPlayerGuildName(cid)
getPlayerGuildRankId(cid)
getPlayerGuildRank(cid)
getPlayerGuildNick(cid)
getPlayerGuildLevel(cid)
getPlayerGUID(cid)
getPlayerNameDescription(cid)
doPlayerSetNameDescription(cid, desc)
getPlayerSpecialDescription(cid)
doPlayerSetSpecialDescription(cid, desc)


getPlayerAccountId(cid) -> Player.data["account_id"]
getPlayerAccount(cid) -> Grab it form SQL?
getPlayerFlagValue(cid, flag) -> We don't have such flags
getPlayerCustomFlagValue(cid, flag) -> We don't have such flags
getPlayerPromotionLevel(cid) - Figure it out from the vocation id
doPlayerSetPromotionLevel(cid, level) -> Change the vocation
getPlayerGroupId(cid) -> Again, no groups, just access flags
doPlayerSetGroupId(cid, newGroupId) -> no groups, just access flags
doPlayerSendOutfitWindow(cid) -> Player.outfitWindow()
doPlayerLearnInstantSpell(cid, name) -> Player.learnSpell(name)
doPlayerUnlearnInstantSpell(cid, name) -> Player.unlearnSpell(name)
getPlayerLearnedInstantSpell(cid, name) -> Player.canUseSpell(name)
getPlayerInstantSpellCount(cid)
getPlayerInstantSpellInfo(cid, index)
getInstantSpellInfo(cid, name)
getCreatureStorageList(cid) -> Player.storage
getCreatureStorage(uid, key) -> Player.getStorage(key)
doCreatureSetStorage(uid, key, value) -> Player.setStorage(key, value)
getStorageList()
getStorage(key) -> Creature.getGlobal(key)
doSetStorage(key, value) -> Creature.setGlobal(key, value)
getChannelUsers(channelId)
getPlayersOnline()
getTileInfo(pos)
getThingFromPos(pos[, displayError = true]) -> StackPosition.getThing()
getThing(uid[, recursive = RECURSE _FIRST])
doTileQueryAdd(uid, pos[, flags[, displayError = true]])
doItemRaidUnref(uid)
getThingPosition(uid) -> You can't do this, just grab the position from arguments or the one you used to get the item.
getTileItemById(pos, itemId[, subType = -1])
getTileItemByType(pos, type)
getTileThingByPos(pos) -> StackPosition.getThing()
getTopCreature(pos) -> Position.getTile().creatures()[0] (might raise an exception)
doRemoveItem(uid[, count = -1])
doPlayerFeed(cid, food)
doPlayerSendCancel(cid, text)
doPlayerSendDefaultCancel(cid, ReturnValue)
getSearchString(fromPosition, toPosition[, fromIsCreature = false[, toIsCreature = false]])
getClosestFreeTile(cid, targetpos[, extended = false[, ignoreHouse = true]])
doTeleportThing(cid, newpos[, pushmove = true[, fullTeleport = true]])
doTransformItem(uid, newId[, count/subType])
doCreatureSay(uid, text[, type = SPEAK _SAY[, ghost = false[, cid = 0[, pos]]]])
doSendCreatureSquare(cid, color[, player])
doSendMagicEffect(pos, type[, player])
doSendDistanceShoot(fromPos, toPos, type[, player])
doSendAnimatedText(pos, text, color[, player])
doPlayerAddSkillTry(cid, skillid, n[, useMultiplier = true])
doCreatureAddHealth(cid, health[, hitEffect[, hitColor[, force]]]) -> Creature.modifyHealth(health)
doCreatureAddMana(cid, mana) -> Creature.modifyMana(mana)
setCreatureMaxHealth(cid, health) -> Creature.data["healthmax"] += health
setCreatureMaxMana(cid, mana) -> Player.data["manamax"] += health
doPlayerSetMaxCapacity(cid, cap) -> Player.data["capasity"] = cap
doPlayerAddSpentMana(cid, amount[, useMultiplier = true])
doPlayerAddSoul(cid, amount)
doPlayerAddItem(cid, itemid[, count/subtype = 1[, canDropOnMap = true[, slot = 0]]])
doPlayerAddItem(cid, itemid[, count = 1[, canDropOnMap = true[, subtype = 1[, slot = 0]]]])
doPlayerAddItemEx(cid, uid[, canDropOnMap = false[, slot = 0]])
doPlayerSendTextMessage(cid, MessageClasses, message)
doPlayerSendChannelMessage(cid, author, message, SpeakClasses, channel)
doPlayerSendToChannel(cid, targetId, SpeakClasses, message, channel[, time])
doPlayerOpenChannel(cid, channelId)
doPlayerAddMoney(cid, money)
doPlayerRemoveMoney(cid, money)
doPlayerTransferMoneyTo(cid, target, money)
doShowTextDialog(cid, itemid, text)
doDecayItem(uid)
doCreateItem(itemid[, type/count], pos) -> placeItem(Item(itemid, type/count), pos)
doCreateItemEx(itemid[, count/subType = -1]) -> Item(itemid, count)
doTileAddItemEx(pos, uid) -> placeItem(Item, pos)
doAddContainerItemEx(uid, virtuid)
doRelocate(pos, posTo[, creatures = true[, unmovable = true]])
doCleanTile(pos[, forceMapLoaded = false])
doCreateTeleport(itemid, topos, createpos)
doCreateMonster(name, pos[, extend = false[, force = false[, displayError = true]]])
doCreateNpc(name, pos[, displayError = true])
doSummonMonster(cid, name)
doConvinceCreature(cid, target)
getMonsterTargetList(cid)
getMonsterFriendList(cid)
doMonsterSetTarget(cid, target) -> Creature.target = target
doMonsterChangeTarget(cid) -> Creature.target = None (?)
getMonsterInfo(name)
doAddCondition(cid, condition) -> Creature.condition(condition)
doRemoveCondition(cid, type[, subId]) -> Creature.removeCondition(condition)
doRemoveConditions(cid[, onlyPersistent])
doRemoveCreature(cid[, forceLogout = true])
doMoveCreature(cid, direction[, flag = FLAG _NOLIMIT])
doSteerCreature(cid, position)
doPlayerSetPzLocked(cid, locked)
doPlayerSetTown(cid, townid)
doPlayerSetVocation(cid,voc)
doPlayerRemoveItem(cid, itemid[, count[, subType = -1]])
doPlayerAddExperience(cid, amount)
doPlayerSetGuildId(cid, id)
doPlayerSetGuildLevel(cid, level[, rank])
doPlayerSetGuildNick(cid, nick)
doPlayerAddOutfit(cid, looktype, addon)
doPlayerRemoveOutfit(cid, looktype[, addon = 0])
doPlayerAddOutfitId(cid, outfitId, addon)
doPlayerRemoveOutfitId(cid, outfitId[, addon = 0])
canPlayerWearOutfit(cid, looktype[, addon = 0])
canPlayerWearOutfitId(cid, outfitId[, addon = 0])
getCreatureCondition(cid, condition[, subId = 0])
doCreatureSetDropLoot(cid, doDrop)
getPlayerLossPercent(cid, lossType)
doPlayerSetLossPercent(cid, lossType, newPercent)
doPlayerSetLossSkill(cid, doLose)
getPlayerLossSkill(cid)
doPlayerSwitchSaving(cid)
doPlayerSave(cid[, shallow = false])
isPlayerPzLocked(cid)
isPlayerSaving(cid)
isCreature(cid)
isMovable(uid)
getCreatureByName(name)
getPlayerByGUID(guid)
getPlayerByNameWildcard(name~[, ret = false])
getPlayerGUIDByName(name[, multiworld = false])
getPlayerNameByGUID(guid[, multiworld = false[, displayError = true]])
doPlayerChangeName(guid, oldName, newName)
registerCreatureEvent(uid, eventName) -> reg(eventName, Creature, function)
unregisterCreatureEvent(uid, eventName) -> unreg(eventName, Creature, function)
getContainerSize(uid) -> len(Item.container.items)
getContainerCap(uid) -> Item.containerSize
getContainerItem(uid, slot)
doAddContainerItem(uid, itemid[, count/subType = 1])
getHouseInfo(houseId[, displayError = true])
getHouseAccessList(houseid, listId)
getHouseByPlayerGUID(playerGUID)
getHouseFromPos(pos) -> getHouseByPos(Position)
setHouseAccessList(houseid, listid, listtext)
setHouseOwner(houseId, owner[, clean]) -> House.owner = owner
getWorldType()
setWorldType(type)
getWorldTime()
getWorldLight()
getWorldCreatures(type)
getWorldUpTime()
getGuildId(guildName)
getGuildMotd(guildId)
getPlayerSex(cid[, full = false])
doPlayerSetSex(cid, newSex)

** This also work entierly diffrently **
    createCombatArea({area}[, {extArea}])
    createConditionObject(type[, ticks[, buff[, subId]]])
    setCombatArea(combat, area)
    setCombatCondition(combat, condition)
    setCombatParam(combat, key, value)
    setConditionParam(condition, key, value)
    addDamageCondition(condition, rounds, time, value)
    addOutfitCondition(condition, outfit)
    setCombatCallBack(combat, key, function_name)
    setCombatFormula(combat, type, mina, minb, maxa, maxb[, minl, maxl[, minm, maxm[, minc[, maxc]]]])
    setConditionFormula(combat, mina, minb, maxa, maxb)
    doCombat(cid, combat, param)
    createCombatObject()
    doCombatAreaHealth(cid, type, pos, area, min, max, effect)
    doTargetCombatHealth(cid, target, type, min, max, effect)
    doCombatAreaMana(cid, pos, area, min, max, effect)
    doTargetCombatMana(cid, target, min, max, effect)
    doCombatAreaCondition(cid, pos, area, condition, effect)
    doTargetCombatCondition(cid, target, condition, effect)
    doCombatAreaDispel(cid, pos, area, type, effect)
    doTargetCombatDispel(cid, target, type, effect)
    doChallengeCreature(cid, target)

numberToVariant(number)
stringToVariant(string)
positionToVariant(pos)
targetPositionToVariant(pos)
variantToNumber(var)
variantToString(var)
variantToPosition(var)
doChangeSpeed(cid, delta) -> Creature.setSpeed(Creature.speed + delta)
doCreatureChangeOutfit(cid, outfit)
doSetMonsterOutfit(cid, name[, time = -1])
doSetItemOutfit(cid, item[, time = -1])
doSetCreatureOutfit(cid, outfit[, time = -1])
getCreatureOutfit(cid) -> Creature.outfit
getCreatureLastPosition(cid) -> Creature.position
getCreatureName(cid) -> Creature.name()
getCreatureSpeed(cid) -> Creature.speed
getCreatureBaseSpeed(cid) -> Creature.speed (we don't really deal with base right now)
getCreatureTarget(cid) -> Creature.target
isSightClear(fromPos, toPos, floorCheck)
isInArray(array, value[, caseSensitive = false]) -> value in array
addEvent(callback, delay, ...) -> callLater(delay (in seconds!), callback, ....)
stopEvent(eventid) -> (return value of the event).stop()
getPlayersByAccountId(accId)
getAccountIdByName(name)
getAccountByName(name)
getAccountIdByAccount(accName)
getAccountByAccountId(accId)
getIpByName(name)
getPlayersByIp(ip[, mask = 0xFFFFFFFF])
doPlayerPopupFYI(cid, message) -> Player.windowMessage(message)
doPlayerSendTutorial(cid, id) -> Player.tutorial(id)
doPlayerSendMailByName(name, item[, town[, actor]])
doPlayerAddMapMark(cid, pos, type[, description])
doPlayerAddPremiumDays(cid, days)
getPlayerPremiumDays(cid)
doCreatureSetLookDirection(cid, dir) -> Creature.turn(dir)
getCreatureGuildEmblem(cid[, target])
doCreatureSetGuildEmblem(cid, emblem)
getCreaturePartyShield(cid[, target])
doCreatureSetPartyShield(cid, shield)
getCreatureSkullType(cid[, target])
doCreatureSetSkullType(cid, skull)
getPlayerSkullEnd(cid)
doPlayerSetSkullEnd(cid, time, type)
getPlayerBlessing(cid, blessing)
doPlayerAddBlessing(cid, blessing)
getPlayerStamina(cid)
doPlayerSetStamina(cid, minutes)
getPlayerBalance(cid)
doPlayerSetBalance(cid, balance)
getCreatureNoMove(cid)
doCreatureSetNoMove(cid, block)
getPlayerIdleTime(cid)
doPlayerSetIdleTime(cid, amount)
getPlayerLastLoad(cid)
getPlayerLastLogin(cid)
getPlayerAccountManager(cid)
getPlayerTradeState(cid)
getPlayerModes(cid) -> Player.modes
getPlayerRates(cid)
doPlayerSetRate(cid, type, value)
getPlayerPartner(cid)
doPlayerSetPartner(cid, guid)
doPlayerFollowCreature(cid, target)
getPlayerParty(cid)
doPlayerJoinParty(cid, lid)
doPlayerLeaveParty(cid[, forced = false])
doPlayerAddMount(cid, mountId)
doPlayerRemoveMount(cid, mountId)
getPlayerMount(cid, mountId)
doPlayerSetMount(cid, mountId)
doPlayerSetMountStatus(cid, mounted)
getMountInfo([mountId])
getPartyMembers(lid)
getCreatureMaster(cid) -> Creature.master
getCreatureSummons(cid)
getTownId(townName)
getTownName(townId)
getTownTemplePosition(townId)
getTownHouses(townId)
getSpectators(centerPos, rangex, rangey[, multifloor = false])
getVocationInfo(id)
getGroupInfo(id[, premium = false])
getVocationList()
getGroupList()
getChannelList()
getTownList()
getWaypointList()
getTalkActionList()
getExperienceStageList()
getItemIdByName(name[, displayError = true]) -> game.item.itemNames[name]
getItemInfo(itemid) -> game.item.items[itemid]
getItemAttribute(uid, key) -> Item.<key>
doItemSetAttribute(uid, key, value) -> Item.<key> = value
doItemEraseAttribute(uid, key) -> del Item.<key>
getItemWeight(uid[, precise = true]) -> Item.weight
getItemParent(uid) -> Item.inContainer
hasItemProperty(uid, prop) Item.<prop>
hasPlayerClient(cid) -> Player.client
isIpBanished(ip[, mask])
isPlayerBanished(name/guid, type)
isAccountBanished(accountId[, playerId])
doAddIpBanishment(...)
doAddPlayerBanishment(...)
doAddAccountBanishment(...)
doAddNotation(...)
doAddStatement(...)
doRemoveIpBanishment(ip[, mask])
doRemovePlayerBanishment(name/guid, type)
doRemoveAccountBanishment(accountId[, playerId])
doRemoveNotations(accountId[, playerId])
doRemoveStatements(name/guid[, channelId])
getNotationsCount(accountId[, playerId])
getStatementsCount(name/guid[, channelId])
getBanData(value[, type[, param]])
getBanReason(id)
getBanAction(id[, ipBanishment = false])
getBanList(type[, value[, param]])
getExperienceStage(level)
getDataDir()
getLogsDir()
getConfigFile()
getConfigValue(key) -> config.<key>
getModList()
getHighscoreString(skillId)
getWaypointPosition(name)
doWaypointAddTemporial(name, pos)
getGameState()
doSetGameState(id)
doExecuteRaid(name)
doCreatureExecuteTalkAction(cid, text[, ignoreAccess = false[, channelId = CHANNEL _DEFAULT]]) -> Creature.say(text[,channelId = channelId])
doReloadInfo(id[, cid])
doSaveServer([shallow = false]) -> engine.saveAll()
doCleanHouse(houseId)
doCleanMap()
doRefreshMap()
doGuildAddEnemy(guild, enemy, war, type)
doGuildRemoveEnemy(guild, enemy)
doUpdateHouseAuctions()
loadmodlib(lib)
domodlib(lib)
dodirectory(dir[, recursively = false])

doPlayerGiveItem(cid, itemid, amount, subType)
doPlayerGiveItemContainer(cid, containerid, itemid, amount, subType)
doPlayerTakeItem(cid, itemid, amount)
doPlayerBuyItem(cid, itemid, count, cost, charges)
doPlayerBuyItemContainer(cid, containerid, itemid, count, cost, charges)
doPlayerSellItem(cid, itemid, count, cost)
doPlayerWithdrawMoney(cid, amount)
doPlayerDepositMoney(cid, amount)
doPlayerAddStamina(cid, minutes)
isPremium(cid) -> Desided by player access flags
getMonthDayEnding(day)
getMonthString(m)
getArticle(str)
isNumeric(str) -> type(str) == int
doPlayerAddAddons(cid, addon)
doPlayerWithdrawAllMoney(cid)
doPlayerDepositAllMoney(cid)
doPlayerTransferAllMoneyTo(cid, target)
playerExists(name) -> True if getPlayer(name) else False
getTibiaTime() -> getTibiaTime()
doWriteLogFile(file, text)
getExperienceForLevel(lv)
doMutePlayer(cid, time)
getPlayerGroupName(cid)
getPlayerVocationName(cid)
getPromotedVocation(vid)
doPlayerRemovePremiumDays(cid, days)
getPlayerMasterPos(cid)
getHouseOwner(houseId)
getHouseName(houseId)
getHouseEntry(houseId)
getHouseRent(houseId)
getHousePrice(houseId)
getHouseTown(houseId)
getHouseDoorsCount(houseId)
getHouseBedsCount(houseId)
getHouseTilesCount(houseId)
getItemNameById(itemid) -> game.item.items[itemid]["name"]
getItemPluralNameById(itemid) -> game.item.items[itemid]["plural"]
getItemArticleById(itemid) -> game.item.items[itemid]["article"]
getItemName(uid) -> Item.name
getItemPluralName(uid) -> Item.plural
getItemArticle(uid) -> Item.article
getItemText(uid) -> Item.text
getItemSpecialDescription(uid) -> Item.description
getItemWriter(uid) -> Item.writer
getItemDate(uid) -> Item.written
getTilePzInfo(pos) -> Position.getTile().getFlags() & TILEFLAGS_PROTECTIONZONE
getTileZoneInfo(pos) -> Position.getTile().getFlags()
doShutdown()
doSummonCreature(name, pos, displayError) -> game.monster.getMonster(name).spawn(pos)
getOnlinePlayers() -> len(game.player.allPlayers)
getPlayerByName(name) -> getPlayer(name)
isPlayer(cid) -> Creature.isPlayer()
isPlayerGhost(cid) -> not Creature.alive
isMonster(cid) -> Creature.isMonster()
isNpc(cid) -> Creature.isNPC()
doPlayerSetExperienceRate(cid, value)
doPlayerSetMagicRate(cid, value)
doPlayerAddLevel(cid, amount, round) -> Player.modifyLevel(amount)
doPlayerAddMagLevel(cid, amount) -> Player.modifyMagicLeve(amount)
doPlayerAddSkill(cid, skill, amount, round) -> Player.addSkillLevel(skill, amount)
getPartyLeader(cid)
isInParty(cid)
isPrivateChannel(channelId)
doPlayerResetIdleTime(cid)
doBroadcastMessage(text, class)
doPlayerBroadcastMessage(cid, text, class, checkFlag, ghost)
getBooleanFromString(input)
doCopyItem(item, attributes) -> Item.copy()
doRemoveThing(uid) -> Depends on where the item is.
doChangeTypeItem(uid, subtype) -> Item.count -= 1 (you need to refresh the item tho)
doSetItemText(uid, text, writer, date) Item.test = text, Item.written = date, Item.writtenBy = writer
doItemSetActionId(uid, aid) -> PyOT support multiple actions, so Item.actions.append("action") and Item.actions.remove("action")
getFluidSourceType(itemid)
getDepotId(uid) -> Depots are indexed based on depotid in player.
getItemDescriptions(uid) -> Item.description
getItemWeightById(itemid, count, precision) -> Item.weight
getItemWeaponType(uid) -> Item.weaponType
getItemRWInfo(uid)
getItemLevelDoor(itemid)
isContainer(uid) -> Item.container
isItemStackable(itemid) -> Item.stackable
isItemRune(itemid)
isItemDoor(itemid)
isItemContainer(itemid) -> Item.container
isItemFluidContainer(itemid)
isItemMovable(itemid) -> Item.movable
isCorpse(uid)
getContainerCapById(itemid) Item.containerSize
getMonsterAttackSpells(name)
getMonsterHealingSpells(name)
getMonsterLootList(name)
getMonsterSummonList(name)
choose(...) -> random.choice(Iter)

** We don't do exhaustion like 
    exhaustion.check(cid, storage)
    exhaustion.get(cid, storage)
    exhaustion.set(cid, storage, time)
    exhaustion.make(cid, storage, time)

isInRange(position, fromPosition, toPosition)
getDistanceBetween(fromPosition, toPosition) -> fromPosition.distanceTo(toPosition)
getDirectionTo(pos1, pos2)
getCreatureLookPosition(cid) -> Creature.positionInDirection(Creature.direction)
getPositionByDirection(position, direction, size) -> positionInDirection(position, direction, size)
doComparePositions(position, positionEx) -> position == positionEx
getArea(position, x, y) -> We don't do areas like lua do.
Position(x, y, z, stackpos) -> Position(x, y, z) and StackPosition(z, y, z, stackpos)
isValidPosition(position) -> if getTile(position): True
isSorcerer(cid)
isDruid(cid)
isPaladin(cid)
isKnight(cid)
isRookie(cid)

** string actions (see pythons documentation instead) **
    string.split(str) -> str.split(splitBy)
    string.trim(str) -> str.trim()
    string.explode(str, sep, limit) -> str.split(sep, limit)
    string.expand(str) -> str += str