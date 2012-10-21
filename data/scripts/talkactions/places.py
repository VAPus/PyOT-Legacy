# Gives the ability to save, remove and teleport to positions for quick traveling to places
# Mainly for development purposes, but it's possible that server owners could use it too.
import json

# Type /pos <whatever> for a list of saved locations.
# /pos save/goto/remove <name>
@register("talkactionFirstWord", "/pos")
@access("DEVELOPER")
def doPosMagic(creature, text):

	places = json.loads(creature.getGlobal('Locations', '{}'))
	
	s = text.split(' ')
	if s[0] == 'save':
		if s[1]:
			pos = creature.position
			places[s[1]] = '%s,%s,%s' %(pos.x, pos.y, pos.z)
			creature.message('Location [%s] saved.' % s[1])
		else:
			creature.message('You have to give this location a name.')
	elif s[0] == 'goto':
		if s[1] and s[1] in places:
			pos = places[s[1]].split(',')
			x, y, z = int(pos[0]), int(pos[1]), int(pos[2])
			pos = creature.position.copy()
			pos.x, pos.y, pos.z = x, y, z
			
			# this is weird as it only sends the effect to the new position
			creature.magicEffect(EFFECT_TELEPORT)
			creature.teleport(pos)
			creature.magicEffect(EFFECT_TELEPORT)
		else:
			creature.message('There is no such place in database.')
	elif s[0] == 'remove':
		if s[1] and s[1] in places:
			del places[s[1]]
			creature.message('%s has been deleted from database.' % s[1])
		else:
			creature.message('There is no such place in database.')
	else:
		out = ''
		for k in places.iterkeys():
			out += ' [%s]' % k
		creature.message('Available locations are: %s' % out)
		
	
	creature.setGlobal('Locations', json.dumps(places))
	return False