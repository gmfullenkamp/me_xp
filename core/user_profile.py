import json
import os
import shutil

from core.specialization import Specialization

class UserProfile:
    def __init__(self, path=os.path.join(os.getcwd(), "data", "user_progress.json")):
        self.path = path
        self._load()

    def _load(self):
        if not os.path.exists(self.path):
            # If progress file doesn't exist, copy from init_progress
            shutil.copyfile(os.path.join(os.getcwd(), "data", "init_progress.json"), self.path)
        with open(self.path, 'r') as f:
            self.data = json.load(f)

    def get_specialization(self, name):
        goal_path = os.path.join(os.getcwd(), "specializations", f"{name.lower()}", "goals.json")
        return Specialization(name, goal_path, self.data["specializations"])

    def save_specialization(self, specialization):
        self.data["specializations"][specialization.name] = specialization.progress
        self._save()

    def _save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2)
