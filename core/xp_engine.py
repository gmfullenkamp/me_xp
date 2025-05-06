import json

class XPEngine:
    def __init__(self, user_profile, goal_manager):
        self.user_profile = user_profile
        self.goal_manager = goal_manager

    def complete_goal(self, specialization, goal_name):
        xp = self.goal_manager.get_xp_for_goal(specialization, goal_name)
        if xp:
            self.user_profile.add_xp(specialization, xp)
            print(f"✅ Earned {xp} XP for: {goal_name}")
        else:
            print("❌ Goal not found.")
