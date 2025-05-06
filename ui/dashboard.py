from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QCheckBox,
    QTabWidget, QScrollArea, QHBoxLayout, QGroupBox, QToolBox
)
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt
from core.user_profile import UserProfile

TIER_EMOJIS = {
    1: "🌱", 2: "🏃", 3: "🔥", 4: "💪", 5: "🚀",
    6: "⚡", 7: "🏆", 8: "🧠", 9: "👑", 10: "🐉"
}

def get_streak_emoji(streak):
    return "🔥" if streak >= 3 else ""

def get_multiplier(streak):
    return 1.0 + 0.1 * min(streak, 10)

class GoalWidget(QWidget):
    def __init__(self, goal, on_complete, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        layout = QHBoxLayout()

        self.goal_name = goal["name"]
        streak = goal["streak"]["current"]
        multiplier = get_multiplier(streak)
        adjusted_xp = round(goal["xp"] * multiplier)

        self.checkbox = QCheckBox(self.goal_name)
        self.xp_label = QLabel(f"✨ XP: {adjusted_xp}")
        streak_emoji = get_streak_emoji(streak)
        self.streak_label = QLabel(f"{streak_emoji} Streak: {streak} | Best: {goal['streak']['best']} (x{multiplier:.1f} streak bonus)")

        layout.addWidget(self.checkbox)
        layout.addWidget(self.xp_label)
        layout.addWidget(self.streak_label)

        self.checkbox.stateChanged.connect(self.on_click)
        self.setLayout(layout)

        # Disable if already completed today
        today = datetime.today().strftime("%Y-%m-%d")
        if today in goal["completed"]:
            self.checkbox.setDisabled(True)
            self.checkbox.setText(f"{self.goal_name} (✔ Done today)")

        self.on_complete = on_complete

    def on_click(self):
        if self.checkbox.isChecked():
            self.on_complete(self.goal_name)
            self.checkbox.setDisabled(True)
            self.checkbox.setText(f"{self.goal_name} (✔ Done today)")
            self.parent_tab.refresh()

class SpecializationTab(QWidget):
    def __init__(self, specialization, user_profile):
        super().__init__()
        self.specialization = specialization
        self.user_profile = user_profile
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.populate_ui(layout)

    def populate_ui(self, layout):
        level = self.specialization.progress["level"]
        xp = self.specialization.progress["xp"]
        xp_to_next = level * 100
        current_level_xp = xp % 100
        percent = (current_level_xp / 100) * 100

        layout.addWidget(QLabel(f"⭐ Level {level}"))

        self.xp_bar = QProgressBar()
        self.xp_bar.setMaximum(100)
        self.xp_bar.setValue(current_level_xp)
        self.xp_bar.setFormat(f"{xp}/{xp_to_next} XP ({percent:.1f}%)")
        layout.addWidget(self.xp_bar)

        toolbox = QToolBox()

        for tier in self.specialization.get_goals():
            min_level = tier['level_range'][0]
            tier_widget = QWidget()
            tier_layout = QVBoxLayout()

            if level < min_level:
                tier_layout.addWidget(QLabel(f"🔒 Locked — Reach level {min_level} to unlock these goals"))
            else:
                for goal in tier["goals"]:
                    goal_widget = GoalWidget(goal, self.complete_goal, self)
                    tier_layout.addWidget(goal_widget)

            tier_widget.setLayout(tier_layout)
            emoji = TIER_EMOJIS.get(tier['tier'], "🎯")
            toolbox.addItem(tier_widget, f"{emoji} Tier {tier['tier']}")

        layout.addWidget(toolbox)
        self.setStyleSheet("background-color: #2e2e2e; color: white;")

    def complete_goal(self, goal_name):
        today = datetime.today().strftime("%Y-%m-%d")
        completed_today = self.specialization.progress["completed"].get(goal_name, [])
        if today in completed_today:
            return  # Already completed today, ignore
        awarded = self.specialization.complete_goal(goal_name)
        self.user_profile.save_specialization(self.specialization)
        self.refresh()  # Refresh UI
    
    def refresh(self):
        layout = self.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.populate_ui(layout)

class MeXPApp(QWidget):
    def __init__(self):
        super().__init__()
        self.user_profile = UserProfile()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🌌 Me XP Tracker")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { background: #444; color: white; padding: 10px; } QTabBar::tab:selected { background: #666; }")

        import os

        for filename in os.listdir("specializations"):
            if os.path.isdir(os.path.join("specializations", filename)):
                spec_name = filename.capitalize()
                spec = self.user_profile.get_specialization(spec_name)
                tab = SpecializationTab(spec, self.user_profile)
                self.tabs.addTab(tab, spec_name)

        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.setStyleSheet("background-color: #2e2e2e; color: white;")

def set_dark_mode(app):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)