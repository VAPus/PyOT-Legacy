guilds = {}

def getGuildById(id):
    try:
        return guilds[id]
    except:
        return None
        
def getGuildNameById(id):
    return getGuildById(id).name
        
class Guild(object):
    def __init__(self, id, name, owner):
        self.id = id
        self.name = name
        self.owner = owner
