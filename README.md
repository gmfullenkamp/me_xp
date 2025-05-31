# 🧠 Me XP – Level Up Your Life

"Life is the ultimate RPG. You don’t just play the hero—you become them." -Grant Fullenkamp

**Me XP** is a gamified life progression tracker where real-world actions grant experience (XP) in personal specializations like *Running*, *Coding*, *Strength Training*, and more. Inspired by RPG mechanics and games like *Melvor Idle*, it turns habits into progress and goals into achievements.

---

## 🚀 What Is Me XP?

In *Me XP*, every completed task earns XP within a **specialization**. As you gain XP, you level up and unlock more advanced challenges. 

Each specialization includes:
- 🧱 **Tiered goals**, unlocked as you level up (10 tiers for levels 1–100)
- ✨ **XP rewards** scaled to task difficulty
- 🔥 **Streak multipliers** that reward consistency
- 📈 **Leveling curve** with exponential XP requirements
- 📊 **Dashboard** to view progress and stats

---

## 🏃 Specialization Example: Running

XP is awarded based on structured tiers with increasing intensity:

| **Tier** | **Level Range** | **Example Goals**                                    | **XP**      |
|----------|------------------|------------------------------------------------------|-------------|
| 1        | 0–9              | Walk 1 mile, Jog 5 min                               | 5–12 XP     |
| 2        | 10–19            | Run 1 mile, Dynamic warm-up                          | 10–20 XP    |
| 3        | 20–29            | Run 2 miles, 20-min run                              | 10–35 XP    |
| 4        | 30–39            | 5 hill sprints, Trail run                            | 20–50 XP    |
| 5        | 40–49            | 3 miles, Interval training                           | 25–65 XP    |
| 6        | 50–59            | 4 miles, Zone 2 heart rate maintenance               | 30–85 XP    |
| 7        | 60–69            | 5 miles, Form drills                                 | 50–110 XP   |
| 8        | 70–79            | 6 miles, Tempo run                                   | 100–140 XP  |
| 9        | 80–89            | 7 miles, 6x800m intervals                            | 90–170 XP   |
| 10       | 90–100           | 10 miles, Threshold run                              | 180–220 XP  |

> Streaks add bonus XP: +10% per day streak up to 100%. Completing a goal daily boosts rewards significantly.

---

## ⚙️ How It Works

- 🧠 **XP Engine**: Calculates level-ups and streak bonuses dynamically
- 📁 **Goal Manager**: Loads tiered goal JSON data per specialization
- 🔐 **User Auth**: Login/registration with Flask and Flask-Login
- 📊 **Dashboard**: Real-time level, XP, and goal completion tracking
- 🏆 **Stats Modal**: View all-time stats, best streaks, and most-completed goals
- 🔄 **Goal Completion**: Mark goals done to earn XP and progress levels

---

## 📦 Planned Features

- 🧠 Multiple Specializations (Coding, Strength, Creativity, etc.)
- 🎯 Smart Goal Suggestions based on progress
- 📆 Daily Logging and Offline Mode
- ⏳ Time-based Bonuses (early AM, streak days, hard weather)
- 🧪 Integration with wearables or APIs (future)

---

## 🛠️ Getting Started

```bash
git clone https://github.com/your-username/me-xp.git
cd me-xp
python app.py
