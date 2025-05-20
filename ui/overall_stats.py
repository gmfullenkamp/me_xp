import os
import sys
from glob import glob
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog, QScrollArea, QWidget, QTabWidget

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    return os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), relative_path)

class StatsDialog(QDialog):
    def __init__(self, user_profile, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📊 Specialization Stats")
        self.setMinimumSize(600, 500)

        tab_widget = QTabWidget(self)
        tab_widget.setStyleSheet("QTabBar::tab { background: #444; color: white; padding: 8px; } QTabBar::tab:selected { background: #666; }")

        for filename in glob(os.path.join(resource_path("specializations"), "*_goals.json")):
            spec_name = os.path.basename(filename).split("_goals.json")[0]
            spec = user_profile.get_specialization(spec_name)
            level = spec.progress["level"]
            xp = spec.progress["xp"]
            total_goals = sum(len(dates) for dates in spec.progress["completed"].values())

            # Create a scrollable stats page per specialization
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("background-color: #2e2e2e; color: white;")

            content = QWidget()
            layout = QVBoxLayout(content)

            header = QLabel(f"🔹 {spec_name.capitalize()} — Level {level} ({xp} XP) | Total Goals Completed: {total_goals}")
            header.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
            layout.addWidget(header)

            for tier in spec.get_goals():
                min_level = tier["level_range"][0]
                if level < min_level:
                    continue  # Skip locked tiers

                for g in tier["goals"]:
                    streak = g["streak"]
                    goal_label = QLabel(f"    - {g['name']}: ✅ {len(g['completed'])} times | 🔥 Current: {streak['current']} | 🏆 Best: {streak['best']}")
                    layout.addWidget(goal_label)

            content.setLayout(layout)
            scroll.setWidget(content)

            tab_widget.addTab(scroll, spec_name.capitalize())

        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget)
        self.setLayout(main_layout)
