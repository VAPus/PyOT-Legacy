guilds = {}

def getGuildById(id):
    try:
        return guilds[id]
    except:
        return None
        
def getGuildNameById(id):
    return getGuildById(id).name
        
def guildExists(id):
    if getGuildById(id) is not None:
        return True
    else
        return False
        
class Guild(object):
    def __init__(self, id, name, leader):
        self.id = id
        self.name = name
        self.leader = leader
        self.members = [leader]
        self.invites = []
        