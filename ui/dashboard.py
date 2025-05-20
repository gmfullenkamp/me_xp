import os
import sys
import random
import pygame
from glob import glob
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, QCheckBox,
    QTabWidget, QHBoxLayout, QToolBox, QPushButton,
    QMessageBox, QDialog, QLineEdit
)
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QSoundEffect
from core.user_profile import UserProfile
from ui.character_stats import DnDCharacterSheet

TIER_EMOJIS = {
    1: "🌱", 2: "🏃", 3: "🔥", 4: "💪", 5: "🚀",
    6: "⚡", 7: "🏆", 8: "🧠", 9: "👑", 10: "🐉"
}

pygame.mixer.init()

def get_streak_emoji(streak):
    return "🔥" if streak >= 3 else ""

def get_multiplier(streak):
    return 1.0 + 0.1 * min(streak, 10)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    return os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), relative_path)

def play_random_sound(folder_name):
    sound_dir = resource_path(os.path.join("assets", folder_name))
    sound_files = glob(os.path.join(sound_dir, "*.wav"))
    if not sound_files:
        return

    sound_path = random.choice(sound_files)
    try:
        pygame.mixer.Sound(sound_path).play()
    except pygame.error as e:
        print(f"Sound playback error: {e}")

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
        if awarded > 0:
            play_random_sound("good_sounds")
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
        self.setWindowTitle("Me XP")
        self.setWindowIcon(QIcon(resource_path("assets/icon.ico")))
        layout = QVBoxLayout()

        self.dnd_sheet = DnDCharacterSheet(self.user_profile)
        layout.addWidget(self.dnd_sheet)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { background: #444; color: white; padding: 10px; } QTabBar::tab:selected { background: #666; }")

        for filename in glob(os.path.join(resource_path("specializations"), "*_goals.json")):
            spec_name = os.path.basename(filename.split("_goals.json")[0])
            spec = self.user_profile.get_specialization(spec_name)
            tab = SpecializationTab(spec, self.user_profile)
            self.tabs.addTab(tab, spec_name)

        layout.addWidget(self.tabs)

        top_bar = QHBoxLayout()

                # Add motivational welcome message
        messages = [
            "Welcome back, young hero. How are the adventures going?",
            "Life is the ultimate RPG—don’t forget to hydrate and grind!",
            "Every XP counts. Even brushing your teeth. Probably.",
            "Ah, a brave soul returns! Time to slay some... habits.",
            "You don’t just play the hero—you become them. Now go become!",
            "Respawn complete. Daily quests await, champion.",
            "May your coffee be strong and your goals plentiful.",
            "Don't forget to equip your shoes before running. Again.",
            "Remember: Even side quests give XP. Let’s do this!",
            "The kingdom missed you. Mostly. Some of it.",
            "Quest log updated. Objective: absolutely crush it.",
            "Grinding IRL. Hard mode unlocked.",
            "What doesn’t kill you gives you XP.",
            "Check your inventory. You’ve got motivation now.",
            "Welcome back, adventurer. The laundry dragon still awaits.",
            "You slept. You leveled up (mentally).",
            "Today’s mini-boss: your to-do list.",
            "The hero returns! Did you bring snacks?",
            "Skill issue? More like skill leveling.",
            "Another day, another few XP. Let’s make it epic.",
            "Remember: procrastination is just a stealth mission gone wrong.",
            "Auto-saving your progress... just kidding. But we do track XP.",
            "IRL fast travel not available. Go walk, hero.",
            "You've entered: Productivity Plains. Wild tasks appear!",
            "Welcome to Day X+1 of your saga. You’re crushing it.",
            "You are the chosen one. No pressure.",
            "Time to train your ultimate move: consistency.",
            "New quest available: Survive Monday. Reward: Glory (and coffee)."
        ]
        messages += [
            "Villagers are talking... they say you're on a streak.",
            "Welcome back, XP warrior. The grind never sleeps.",
            "You logged in. Your goals flinched.",
            "RNG tip: 100% of effort guarantees XP.",
            "Daily log-in bonus: +1 swagger, +5 confidence.",
            "Mind sharp? Muscles prepped? Let’s slay the day.",
            "The enemies today? Laziness, snacks, and doubt. Fight!",
            "Mana low? Coffee. Always coffee.",
            "Your journey is legendary. Even the loading screen says so.",
            "You’ve unlocked a new location: Focus Forest.",
            "Today's forecast: 70% chance of productivity.",
            "New ability unlocked: Waking up on time!",
            "Your mentor is proud. Your past self is impressed.",
            "This is not a drill. This is a daily quest.",
            "Even the boss battles take breaks. But not you. You're here.",
            "Mount Motivation awaits. Pack your lunch.",
            "You’ve got this. Like, actually. Statistically proven.",
            "Streak bonus activated. Time to go full anime montage.",
            "XP multiplier: +1.2 for good vibes.",
            "Tap into your inner protagonist.",
            "The treasure was in you all along (and maybe some in the fridge).",
            "Another chapter begins. Write a good one today.",
            "That goal you’ve been avoiding? It’s blinking red now.",
            "Side quests welcome. Just don’t forget the main quest.",
            "Even your shadow leveled up waiting for you.",
            "You've been summoned. Accept the call.",
            "Epic loot awaits: discipline, progress, and self-respect.",
            "Pro tip: Every step counts. Especially toward snacks AND goals.",
            "The world didn’t level cap you. Keep going.",
            "Equip mindset: Legendary",
            "Stamina regenerates over time. So does motivation.",
            "You've entered beast mode. Proceed with purpose."
        ]

        welcome_label = QLabel(random.choice(messages))
        welcome_label.setStyleSheet("font-size: 16px; font-style: italic; font-weight: bold; margin-right: 20px;")
    
        reset_button = QPushButton("Reset XP")
        reset_button.setStyleSheet("background-color: red; color: white; font-weight: bold; padding: 10px;")
        reset_button.clicked.connect(self.confirm_reset_xp)

        top_bar.addWidget(welcome_label)
        top_bar.addStretch()
        top_bar.addWidget(reset_button)

        layout.insertLayout(0, top_bar)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #2e2e2e; color: white;")

    def confirm_reset_xp(self):
        self.reset_warnings = [
            "This will wipe your journey. Like Thanos, but with less flair.",
            "All your XP will be gone. Like your gym gains after Thanksgiving.",
            "You sure you want to throw it all away like a soggy taco?",
            "Even your best streak? Poof. Gone.",
            "Imagine deleting your life's save file. That's what you're doing.",
            "Once upon a time, you were a hero. Now? A potato.",
            "Warning: Resetting XP may cause existential dread.",
            "This is your 8th warning. Nobody goes this far accidentally.",
            "Your XP called. It doesn’t want to go.",
            "Final warning: You’re about to nuke everything. Type 'YES'."
        ]
        self.current_warning_index = 0
        self.show_next_reset_dialog()

    def show_next_reset_dialog(self):
        if self.current_warning_index >= len(self.reset_warnings):
            self.user_profile.reset_all_data()
            QMessageBox.information(self, "XP Reset", "All XP and progress has been obliterated. Good luck, hero.")
            # Reinitialize the UI by reloading the profile and tabs
            self.user_profile = UserProfile()  # Reloads data (now empty)
            self.tabs.clear()  # Remove old tabs
            for filename in os.listdir(resource_path("specializations")):
                if os.path.isdir(os.path.join(resource_path("specializations"), filename)):
                    spec_name = filename.capitalize()
                    spec = self.user_profile.get_specialization(spec_name)
                    tab = SpecializationTab(spec, self.user_profile)
                    self.tabs.addTab(tab, spec_name)
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Confirmation {self.current_warning_index + 1}/10")

        layout = QVBoxLayout()
        label = QLabel(self.reset_warnings[self.current_warning_index])
        input_box = QLineEdit()
        input_box.setPlaceholderText("Type YES to confirm")
        ok_button = QPushButton("Confirm")

        layout.addWidget(label)
        layout.addWidget(input_box)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)

        def handle_confirm():
            if input_box.text().strip().upper() == "YES":
                self.current_warning_index += 1
                dialog.accept()
                self.show_next_reset_dialog()
            else:
                QMessageBox.warning(self, "Cancelled", "Reset aborted. XP remains intact.")
                dialog.reject()

        ok_button.clicked.connect(handle_confirm)
        play_random_sound("bad_sounds")
        dialog.exec_()


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