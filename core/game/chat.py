import weakref

channels = {}

class Channel(object):
    def __init__(self, name, id):
        self.id = id
        self.members = []
        self.messages = []
        self.name = name

    def addMember(self, player):
        self.members.append(weakref.ref(player))

    def removeMember(self, player):
        for member in self.members:
            if member() == player:
                self.members.remove(member)


def openChannel(channelName, id = None):
    channelId = id or len(channels)
    channel = Channel(channelName, channelId)
    channels[channelId] = channel
    return channel

def delChannel(channelId):
    try:
        del channels[channelId]
    except:
        pass

def getChannelsWithPlayer(player):
    channelList = []
    for channelId in channels:
        channel = channels[channelId]
        if player in channel.members:
            channelList.append(channel)

    return channelList

def getChannels(player):
    channelList = []
    for channelId in channels:
        # TODO: Accesslist
        channelList.append(channels[channelId])

    return channelList
    
def getChannel(id):
    try:
        return channels[id]
    except:
        return