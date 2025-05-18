from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox
from PyQt5.QtCore import Qt

STAT_NAME_TO_EMOJI = {
    "Strength": "💪",
    "Dexterity": "🤹",
    "Constitution": "🫀",
    "Intelligence": "🧠",
    "Wisdom": "🦉",
    "Charisma": "😎"
}

class DnDCharacterSheet(QWidget):
    def __init__(self, user_profile):
        super().__init__()
        self.user_profile = user_profile
        self.stats_labels = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.stats_box = QGroupBox("🧙 Character Stats")
        from PyQt5.QtWidgets import QGridLayout
        self.stats_layout = QGridLayout()

        stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        for i, stat in enumerate(stat_names):
            label = QLabel(f"{STAT_NAME_TO_EMOJI[stat]} {stat}: 0.00 / 20.00 (-5 Modifier)")
            label.setStyleSheet("font-family: monospace; padding: 4px; font-size: 14px;")
            self.stats_labels[stat] = label
            row = i // 2
            col = i % 2
            self.stats_layout.addWidget(label, row, col)

        self.stats_box.setLayout(self.stats_layout)
        layout.addWidget(self.stats_box)
        self.setLayout(layout)

        self.update_stats()

    def update_stats(self):
        stats = {
            "Strength": 0.0,
            "Dexterity": 0.0,
            "Constitution": 0.0,
            "Intelligence": 0.0,
            "Wisdom": 0.0,
            "Charisma": 0.0
        }

        spec_to_stat = {
            "running": [("Dexterity", 0.2), ("Constitution", 0.1)],
            "coding": [("Intelligence", 0.25), ("Wisdom", 0.1)],
            "calisthenicing": [("Strength", 0.3), ("Constitution", 0.2)],
            "pianoing": [("Charisma", 0.2), ("Dexterity", 0.1)],
            "healthing": [("Wisdom", 0.2), ("Intelligence", 0.1)]
        }

        for spec_name, modifiers in spec_to_stat.items():
            try:
                spec = self.user_profile.get_specialization(spec_name)
                level = min(spec.progress["level"], 100)
                for stat, scale in modifiers:
                    stats[stat] += level * scale
            except Exception:
                pass

        for stat, value in stats.items():
            capped = min(value, 20.0)
            sign = ""
            if capped > 10:
                sign = "+"
            elif capped < 10:
                sign = "-"
            self.stats_labels[stat].setText(f"{STAT_NAME_TO_EMOJI[stat]} {stat}: {capped:.2f} / 20.00 ({sign}{abs(capped-10)/2:.2f} Modifier)")
