function onUse(cid, item, fromPosition, itemEx, toPosition)
    doAccountAddVipTime(getPlayerAccount(cid), 30 * 86400) 
	doSendMagicEffect(getThingPos(cid), CONST_ME_FIREWORK_BLUE)
	doPlayerSendTextMessage(cid, MESSAGE_EVENT_ADVANCE, "Congratulations! Now you have 30 days of vip account to enjoy!")
	doRemoveItem(item.uid)
	return true
end
