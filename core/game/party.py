class Party(object):
    def __init__(self, leader):
        self.leader = leader
        self.members = [leader]
        self.invites = []

    def addMember(self, creature):
        
        try:
            self.invites.remove(creature)
        except:
            pass

        self.broadcast("%s has joined the party." % creature.name())
        creature.partyObj = self
        
        self.members.append(creature)
        
        creature.message("You have joined %s's party. Open the party channel to communicate with your companions")
        
        
    def removeMember(self, creature):
        try:
            self.members.remove(creature)
            return True
        except:
            return False


    def addInvite(self, creature):
        if creature in self.invites:
            return # Already in it
            
        self.leader.message("%s has been invited. Open the party channel to communicate with your members." % creature.name())
        self.invites.append(creature)
        
        creature.message("%s has invited you to %s oarty." % (self.leader.name(), self.leader.sexAdjective()))

    def removeInvite(self, creature):
        try:
            self.invites.remove(creature)
            return True
        except:
            return False

        self.leader.message("Invitation for %s has been revoked." % creature.name())
        player.message("%s has revoked your invitation." % self.leader.name())
        
        
    def disband(self):
        for member in self.members:
            pass #TODO

    def changeLeader(self, creature):
        pass # TODO

    def icons(self):
        pass # TODO
        
    def broadcast(self, text):
        for member in self.members:
            member.message(text)