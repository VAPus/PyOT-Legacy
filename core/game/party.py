class Party(object):
    def __init__(self, leader):
        self.leader = leader
        self.members = [leader]
        self.invites = []
        self.shareExperience = False
        self.shareExperienceOk = False

    def addMember(self, creature):
        if creature in self.members:
            raise Exception("%s is already a member of this party!" % (creature))
        try:
            self.invites.remove(creature)
        except:
            pass

        self.broadcast("%s has joined the party." % creature.name())
        creature.setParty(self)
        
        self.members.append(creature)
        
        if self.shareExperience:
            self.checkShareExperience()
        
        self.refreshMemberShields()
        
        creature.message("You have joined %s's party. Open the party channel to communicate with your companions" % self.leader.name())
        
        
    def removeMember(self, creature):
        if len(self.members) <= 2:
            self.disband()
            return
        
        try:
            self.members.remove(creature)
        except:
            return

        creature.partyObj = None
        creature.message("You have left the party.")
        self.broadcast("%s has left the party." % creature.name())
        creature.refreshShield()
        
        # Send empty shield on all of us.
        for member in self.members:
            with creature.packet() as stream:
                stream.shield(member.cid, SHIELD_NONE)
        
        if creature == self.leader:
            self.leader = None
            
            # Pick a new leader or disband
            if len(self.members) > 1:
                self.changeLeader(self.members[0])
                
        
    def addInvite(self, creature):
        if creature in self.invites:
            return # Already in it
            
        self.leader.message("%s has been invited. Open the party channel to communicate with your members." % creature.name())
        self.invites.append(creature)

        creature.refreshShield()
        self.leader.refreshShield()
        
        creature.message("%s has invited you to %s party." % (self.leader.name(), self.leader.sexAdjective()))

    def removeInvite(self, player):
        try:
            self.invites.remove(player)
        
        except:
            return

        self.leader.message("Invitation for %s has been revoked." % player.name())
        player.message("%s has revoked your invitation." % self.leader.name())
        player.partyObj = None
        
        # Is the party dead. Aga, no members or invites?
        if len(self.members) <= 1 and len(self.invites) == 0:
            self.disband()
            player.refreshShield()
        else:
            player.refreshShield()
            self.leader.refreshShield()
    
    def toggleShareExperience(self):
        self.shareExperience = not self.shareExperience
        
        if self.shareExperience:
            self.checkShareExperience()
        
    def checkShareExperience(self):
        isOk = True
        
        lowestLevel = 9000000000
        highestLevel = 0
        contributeTime = time.time() - config.partyExperienceContributeTime
        
        for member in self.members:
            if member.data["level"] < lowestLevel:
                lowestLevel = member.data["level"]
            if member.data["level"] > highestLevel:
                highestLevel = member.data["level"]
                
            if not member.inRange(self.leader.position, config.partyExperienceDistance, config.partyExperienceDistance):
                isOk = False
                break
                
            
            if member.lastPassedDamage < contributeTime: # TODO healing.
                isOk = False
                break
                
        if isOk:
            if float(lowestLevel) / highestLevel < config.partyExperienceLevelFactor:
                isOk = False
        
        if isOk != self.shareExperienceOk:
            self.shareExperienceOk = isOk
            self.refreshMemberShields()
            
        return isOk
                
                
    def disband(self):
        for member in self.members:
            for formember in self.members:
                with formember.packet() as stream:
                    stream.shield(member.cid, SHIELD_NONE) 
            member.partyObj = None
            member.message("Your party has been disbanded")
            
        self.members = []
        self.leader = None

    def changeLeader(self, creature):
        if creature not in self.members:
            raise Exception("Trying to make a non-member leader of the party")
        
        self.leader = creature
        self.broadcast("%s is now the leader of the party." % creature.name())
        self.refreshMemberShields()

    def getShield(self, forMember, byMember):
        if byMember in self.invites:
            if forMember is self.leader:
                return SHIELD_MEMBER_INVITE
            return SHIELD_NONE
        elif forMember in self.invites and byMember is self.leader:
            return SHIELD_LEADER_INVITE
        
        if forMember is self.leader:
            if self.shareExperience:
                return SHIELD_LEADER_SHAREDEXP if self.shareExperienceOk else SHIELD_LEADER_NOSHAREDEXP
            return SHIELD_LEADER
        elif forMember in self.members:
            if self.shareExperience:
                return SHIELD_MEMBER_SHAREDEXP if self.shareExperienceOk else SHIELD_MEMBER_NOSHAREDEXP
            return SHIELD_MEMBER
        
        return SHIELD_NONE
    
    def refreshMemberShields(self):
        # send all shields to every member.
        for member in self.members:
            for formember in self.members:
                with formember.packet() as stream:
                    stream.shield(member.cid, self.getShield(member, formember))
                    
    def broadcast(self, text):
        for member in self.members:
            member.message(text)