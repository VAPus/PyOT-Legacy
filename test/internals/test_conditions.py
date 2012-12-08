from test.framework import FrameworkTestGame

class TestCondition(FrameworkTestGame):
    def test_addCondition(self):
        condition = Condition(CONDITION_FIRE, length=10, damage=1)
        self.player.condition(condition)

        self.assertTrue(self.player.conditions)
        self.assertTrue(condition.creature)

    def test_hascondition(self):
        condition = Condition(CONDITION_FIRE, length=10, damage=1)
        self.player.condition(condition)

        self.assertTrue(self.player.hasCondition(CONDITION_FIRE))

    def test_getcondition(self):
        condition = Condition(CONDITION_FIRE, length=10, damage=1)
        self.player.condition(condition)

        self.assertEqual(self.player.getCondition(CONDITION_FIRE), condition)

    def test_copycondition(self):
        condition = Condition(CONDITION_FIRE, length=10, damage=1)

        condition2 = condition.copy()

        self.assertEqual(condition.type, condition2.type)

    def test_boost(self):
        boost = Boost("speed", 1000, 0.2)
        
        originalSpeed = self.player.speed
        
        self.player.condition(boost)
        
        self.assertEqual(self.player.speed, originalSpeed + 1000)
        
        def revert():
            self.assertEqual(self.player.speed, originalSpeed)
            
        return callLater(0.3, revert)
        
    def test_multiboost(self):
        boost = Boost(["health", "healthmax"], [1000, 1000], 0.2)
        
        originalHealth = self.player.data["health"]
        originalHealthMax = self.player.data["healthmax"]
        
        self.player.condition(boost)
        
        self.assertEqual(self.player.data["health"], originalHealth + 1000)
        self.assertEqual(self.player.data["healthmax"], originalHealthMax + 1000)
        
        def revert():
            self.assertEqual(self.player.data["health"], originalHealth)
            self.assertEqual(self.player.data["healthmax"], originalHealthMax)
            
        return callLater(0.3, revert)
        
    def test_boostskill(self):
        boost = Boost(SKILL_SWORD, 10, 0.2)
        
        originalSkill = self.player.getActiveSkill(SKILL_SWORD)
        
        self.player.condition(boost)
        
        self.assertEqual(self.player.getActiveSkill(SKILL_SWORD), originalSkill + 10)
        
        def revert():
            self.assertEqual(self.player.getActiveSkill(SKILL_SWORD), originalSkill)
            
        return callLater(0.3, revert)