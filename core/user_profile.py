import json
import os
import sys
import shutil

from core.specialization import Specialization

def resource_path(relative_path):
    return os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), relative_path)

def get_appdata_path():
    """Return a writable folder path for user progress (e.g., AppData/MeXP)"""
    base = os.getenv('APPDATA') or os.path.expanduser("~")
    path = os.path.join(base, "MeXP")
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, "user_progress.json")

class UserProfile:
    def __init__(self):
        self.path = get_appdata_path()
        self.data = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.path):
            shutil.copyfile(resource_path("data/init_progress.json"), self.path)
        with open(self.path, 'r') as f:
            self.data = json.load(f)

    def get_specialization(self, name):
        goal_path = resource_path(f"specializations/{name.lower()}/goals.json")
        return Specialization(name, goal_path, self.data["specializations"])

    def save_specialization(self, specialization):
        self.data["specializations"][specialization.name] = specialization.progress
        self._save()

    def _save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def reset_all_data(self):
        self.data = {}
        self.data["specializations"] = {}
        self._save()
