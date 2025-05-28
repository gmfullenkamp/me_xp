from flask import Flask, render_template, redirect, url_for, jsonify
from core.user_profile import UserProfile
import os
import glob
import random
from datetime import datetime
from constants import QUOTES

from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from core.auth import get_user, register_user, users

# Global quote cache
SESSION_QUOTE = random.choice(QUOTES)

# Init Flask and Login Manager
app = Flask(__name__)
app.secret_key = 'super-secret-key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def get_user_profile():
    return UserProfile(current_user.username)

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if str(user.id) == user_id:
            return user
    return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = register_user(username, password)
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Username already exists")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    user_profile = get_user_profile()
    spec_files = glob.glob(os.path.join("specializations", "*_goals.json"))
    spec_names = [os.path.basename(f).replace("_goals.json", "") for f in spec_files]
    specs = [user_profile.get_specialization(name) for name in spec_names]

    # Compute XP info for each specialization
    for spec in specs:
        level = spec.progress["level"]
        xp = spec.progress["xp"]
        xp_required_to_level = lambda l: sum(int(100 * (1.1 ** (i - 1))) for i in range(1, l))

        spec.progress["xp_start"] = xp_required_to_level(level)
        spec.progress["xp_end"] = xp_required_to_level(level + 1)
        spec.progress["xp_progress"] = xp - spec.progress["xp_start"]

    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('index.html', specs=specs, quote=SESSION_QUOTE, current_date=today)

@app.route('/complete_goal/<spec_name>/<goal_name>', methods=['POST'])
@login_required
def complete_goal(spec_name, goal_name):
    user_profile = get_user_profile()
    spec = user_profile.get_specialization(spec_name)
    awarded = spec.complete_goal(goal_name)
    user_profile.save_specialization(spec)

    streak = spec.get_streak(goal_name)
    level = spec.progress["level"]
    xp = spec.progress["xp"]

    # Calculate XP needed to reach current level
    def xp_required_to_level(lvl):
        return sum(int(100 * (1.1 ** (i - 1))) for i in range(1, lvl))

    xp_for_current_level = xp_required_to_level(level)
    xp_for_next_level = xp_required_to_level(level + 1)

    current = xp - xp_for_current_level
    target = xp_for_next_level - xp_for_current_level

    multiplier = round(1.0 + 0.1 * min(streak["current"], 10), 1)

    return jsonify({
        "awarded": awarded,
        "xp": xp,
        "level": level,
        "current": current,
        "target": target,
        "streak": streak,
        "multiplier": multiplier,
        "goal": goal_name
    })

@app.route('/stats')
@login_required
def stats():
    user_profile = get_user_profile()
    stats_summary = {}
    overall_completed = {}
    all_dates = []

    for spec_name in user_profile.data["specializations"]:
        spec = user_profile.get_specialization(spec_name)
        completed = spec.progress.get("completed", {})

        # Collect for overall
        for goal, dates in completed.items():
            overall_completed.setdefault(goal, []).extend(dates)
            all_dates.extend(dates)

        total_completed = sum(len(dates) for dates in completed.values())
        most_done_goal = max(completed.items(), key=lambda x: len(x[1]), default=(None, []))
        best_streak = max(((g, spec.get_streak(g)["best"]) for g in completed), key=lambda x: x[1], default=(None, 0))
        first_dates = [datetime.strptime(date, "%Y-%m-%d") for dates in completed.values() for date in dates]
        first_done = min(first_dates).strftime("%Y-%m-%d") if first_dates else "N/A"

        stats_summary[spec_name] = {
            "first_completed": first_done,
            "total_completed": total_completed,
            "most_done_goal": most_done_goal[0],
            "most_done_count": len(most_done_goal[1]),
            "best_streak_goal": best_streak[0],
            "best_streak_count": best_streak[1],
        }

    # Compute overall stats
    overall_first = min((datetime.strptime(d, "%Y-%m-%d") for d in all_dates), default="N/A")
    overall_most_done = max(overall_completed.items(), key=lambda x: len(x[1]), default=(None, []))

    overall_summary = {
        "first_completed": overall_first.strftime("%Y-%m-%d") if overall_first != "N/A" else "N/A",
        "total_completed": sum(len(d) for d in overall_completed.values()),
        "most_done_goal": overall_most_done[0],
        "most_done_count": len(overall_most_done[1]) if overall_most_done[1] else 0
    }

    return jsonify({
        "overall": overall_summary,
        "specializations": stats_summary
    })

@app.route('/reset')
@login_required
def reset():
    user_profile = get_user_profile()
    user_profile.reset_all_data()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
