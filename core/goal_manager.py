import json
import os

class GoalManager:
    def __init__(self, path=os.path.join(os.getcwd(), "specializations", "running", "goals.json")):
        with open(path, 'r') as f:
            self.goals_data = json.load(f)

    def get_xp_for_goal(self, specialization, goal_name):
        for tier in self.goals_data["tiers"]:
            for goal in tier["goals"]:
                if goal["name"].lower() == goal_name.lower():
                    return goal["xp"]
        return None
