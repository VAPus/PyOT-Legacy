class Party(object):
    def __init__(self, leader):
        self.leader = leader
        self.members = [leader]
        self.invites = []

    def addMember(self, creature):
        self.members.append(creature)

    def removeMember(self, creature):
        try:
            self.members.remove(creature)
            return True
        except:
            return False

    def addInvite(self, creature):
        self.invites.append(creature)

    def removeInvite(self, creature):
        try:
            self.invites.remove(creature)
            return True
        except:
            return False

    def disband(self):
        for member in self.members:
            pass #TODO

    def changeLeader(self, creature):
        pass # TODO

    def icons(self):
        pass # TODO

