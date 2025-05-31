import json
from datetime import datetime


class Specialization:
    def __init__(self, name, goals_path, progress):
        self.name = name
        self.goals_path = goals_path
        self.progress = progress.get(name, {"xp": 0, "level": 1, "completed": {}})
        self.goals_data = self._load_goals()

    def _load_goals(self):
        with open(self.goals_path, "r") as f:
            return json.load(f)["tiers"]

    def get_streak(self, goal_name):
        dates = self.progress["completed"].get(goal_name, [])
        dates = sorted(datetime.strptime(d, "%Y-%m-%d") for d in dates)
        streak = 0
        best = 0
        today = datetime.today().date()

        for i in range(len(dates) - 1, -1, -1):
            if (today - dates[i].date()).days == streak:
                streak += 1
            else:
                break
        best = self._longest_streak(dates)
        return {"current": streak, "best": best}

    def _longest_streak(self, dates):
        if not dates:
            return 0
        longest = current = 1
        for i in range(1, len(dates)):
            if (dates[i].date() - dates[i - 1].date()).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        return longest
