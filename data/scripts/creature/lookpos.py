@register("lookAt", ("creature", "item"))
@access("KICK")
# I think it's better to show the position in default window, instead of merging it with description and looking for it in server log.
def givePosition(creature, thing, **pos):
	if creature.getStorage("showpos") == 'enabled':
		# not a pretty output, but w/e
		creature.message('Position:  %s' % str(pos['position']), MSG_STATUS_CONSOLE_ORANGE)
	return True


@register('talkaction', '/showpos')
@access("KICK")
def showToggle(creature, text):
	show = 'enabled'

	if creature.getStorage("showpos") == 'enabled':
		show = 'disabled'
	
	creature.setStorage("showpos", show)
	creature.message("Position showing has been %s" % show)
	
	return False