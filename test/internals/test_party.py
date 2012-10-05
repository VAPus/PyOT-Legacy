from .. import framework

class TestParty(framework.FrameworkTestGame):
    def test_create_party(self):
        # We have no party.
        self.assertFalse(self.player.party())
        
        # Make a new party
        party = self.player.newParty()
        
        self.assertTrue(party)
        self.assertEqual(party, self.player.party())
        self.assertIsInstance(party, game.party.Party)
        
        # We're leader?
        self.assertEqual(party.leader, self.player)
        
        # We're member?
        self.assertTrue(self.player in party.members)
        
        
    def test_disband_party(self):
        party = self.player.newParty()
        
        party.disband()
        
        self.assertFalse(self.player.party())
        
    def test_leave_party(self):
        party = self.player.newParty()
        
        self.player.leaveParty()
        
        self.assertFalse(self.player in party.members)
        
    def test_leave_party_disband(self):
        party = self.player.newParty()
        
        self.player.leaveParty()
        
        self.assertFalse(party.members)
        self.assertFalse(party.leader)
        
    def test_party_invite(self):
        party = self.player.newParty()
        
        member = self.setupPlayer()
        
        party.addInvite(member)
        
        self.assertTrue(member in party.invites)
        
        # Leaders shield?
        self.assertEqual(member.getShield(self.player), SHIELD_LEADER_INVITE)
        
        # Members shield?
        self.assertEqual(self.player.getShield(member), SHIELD_MEMBER_INVITE)
        
        # Only invite?
        self.assertEqual(len(party.invites), 1)
        
    def test_multiple_invites(self):
        partyLeader = self.setupPlayer()
        member = self.setupPlayer()
        
        party1 = partyLeader.newParty()
        party2 = self.player.newParty()
        
        party1.addInvite(member)
        party2.addInvite(member)
        
        self.assertTrue(member in party1.invites)
        self.assertTrue(member in party2.invites)
        
        # Leaders shield?
        self.assertEqual(member.getShield(self.player), SHIELD_LEADER_INVITE)
        self.assertEqual(member.getShield(partyLeader), SHIELD_LEADER_INVITE)
        
        # Members shield?
        self.assertEqual(self.player.getShield(member), SHIELD_MEMBER_INVITE)
        self.assertEqual(partyLeader.getShield(member), SHIELD_MEMBER_INVITE)
        
        # Only invite?
        self.assertEqual(len(party1.invites), 1)
        self.assertEqual(len(party2.invites), 1)
        
    def test_join(self):
        party = self.player.newParty()
        
        member = self.setupPlayer()
        
        party.addInvite(member)
        
        party.addMember(member)
        
        # Now invites should be empty
        self.assertFalse(party.invites)
        
        # And we'll be a member.
        self.assertTrue(member in party.members)
        
        # We should also have a party shield.
        self.assertEqual(member.getShield(self.player), SHIELD_MEMBER)
        
        # And leader a leader shield.
        self.assertEqual(self.player.getShield(member), SHIELD_LEADER)
        
        # And get the correct party object.
        self.assertEqual(party, member.party())
        
    def test_change_leader(self):
        party = self.player.newParty()
        
        member = self.setupPlayer()
        
        party.addMember(member)
        
        party.changeLeader(member)
        
        # We're leader?
        self.assertEqual(party.leader, member)
        
        # Old leader is member?
        self.assertTrue(self.player in party.members)
        
        # Shields are already tested...
        
    def test_leave_party(self):
        party = self.player.newParty()
        
        member = self.setupPlayer()
        
        party.addMember(member)
        
        party.removeMember(member)
            
        self.assertFalse(member in party.members)
        self.assertFalse(member.party())
        
    def test_leave_party_disband(self):
        party = self.player.newParty()
        
        member = self.setupPlayer()
        
        party.addMember(member)
        
        party.removeMember(member)
            
        self.assertFalse(party.members)
        self.assertFalse(party.leader)
        
    def test_leave_pass_leadership(self):
        party = self.player.newParty()
        
        member = self.setupPlayer()
        member2 = self.setupPlayer()
        
        party.addMember(member)
        party.addMember(member2)
        
        # Leader leave.
        party.removeMember(self.player)
            
        # Member1 is new leader?
        self.assertEqual(member, party.leader)
        self.assertEqual(len(party.members), 2)