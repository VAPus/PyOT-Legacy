guilds = {}

def getGuildById(id):
    try:
        return guilds[id]
    except:
        return None
        
def getGuildId(name):
    try:
        return guilds[name]
    except:
    	return None
        
class Guild(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
