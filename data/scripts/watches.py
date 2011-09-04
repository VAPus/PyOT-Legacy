import game.scriptsystem as scriptsystem
import game.enum as enum
from game.engine import getTibiaTime

watches = 1728, 1729, 1730, 1731, 1873, 1874, 1875, 1876, 1877, 1881, 2036, 6091, 6092, 8187

def useWatch(creature, **k):
    time = getTibiaTime()
    creature.message("The time is %02d:%02d." % (time[0], time[1]), enum.MSG_INFO_DESCR)

scriptsystem.reg('use', watches, useWatch)