import os
from core.models import db
from core.user_profile import UserProfile, compute_streak
from core.goal_manager import GoalManager

def xp_required_to_level(level):
    return sum(int(100 * (1.1 ** (i - 1))) for i in range(1, level))

def calculate_level(xp):
    level = 1
    required = 100
    total = 0
    while xp >= total + required:
        total += required
        level += 1
        required = int(required * 1.1)
    return level

def get_streak(spec, goal_name):
    completions = [
        c.completed_date.strftime("%Y-%m-%d")
        for c in spec.goals
        if c.goal_name == goal_name
    ]
    return compute_streak(completions)


class XPEngine:
    def __init__(self, user):
        self.user_profile = UserProfile(user)

    def complete_goal(self, specialization_name, goal_name):
        json_path = os.path.join("specializations", f"{specialization_name.lower()}_goals.json")
        self.goal_manager = GoalManager(json_path)
        spec = self.user_profile.get_specialization(specialization_name)
        base_xp = self.goal_manager.get_xp_for_goal(specialization_name, goal_name)
        if base_xp is None:
            return None

        streak_info = get_streak(spec, goal_name)
        multiplier = 1.0 + 0.1 * min(streak_info["current"], 10)
        awarded_xp = int(base_xp * multiplier)

        # Apply XP and update level
        spec.xp += awarded_xp
        spec.level = calculate_level(spec.xp)

        self.user_profile.save_goal_completion(specialization_name, goal_name)
        db.session.commit()

        return {
            "awarded": awarded_xp,
            "xp": spec.xp,
            "level": spec.level,
            "current": spec.xp - xp_required_to_level(spec.level),
            "target": xp_required_to_level(spec.level + 1) - xp_required_to_level(spec.level),
            "streak": streak_info,
            "multiplier": round(multiplier, 1),
            "goal": goal_name
        }
