from flask import Flask, render_template, redirect, url_for, jsonify
import os
import glob
import json
import random
from datetime import datetime
from constants import QUOTES
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from core.auth import get_user, register_user
from core.user_profile import UserProfile, compute_streak
from core.models import db, GoalCompletion, User
from core.xp_engine import XPEngine

# Global quote cache
SESSION_QUOTE = random.choice(QUOTES)

# Init Flask and Login Manager
app = Flask(__name__)
app.secret_key = 'super-secret-key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

def get_user_profile():
    return UserProfile(current_user.username)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    user_profile = UserProfile(current_user)
    spec_files = glob.glob(os.path.join("specializations", "*_goals.json"))
    spec_names = [os.path.basename(f).replace("_goals.json", "") for f in spec_files]

    specs = []
    for name in spec_names:
        spec = user_profile.get_specialization(name)
        xp = spec.xp
        level = spec.level

        # XP progress calculations
        xp_required_to_level = lambda l: sum(int(100 * (1.1 ** (i - 1))) for i in range(1, l))
        xp_start = xp_required_to_level(level)
        xp_end = xp_required_to_level(level + 1)
        xp_progress = xp - xp_start

        # Load goal tiers from JSON
        with open(f"specializations/{name.lower()}_goals.json") as f:
            goal_data = json.load(f)

        # Fetch completed goals for this user/spec
        completions = GoalCompletion.query.filter_by(specialization_id=spec.id).all()
        completed_lookup = {}
        for c in completions:
            completed_lookup.setdefault(c.goal_name, []).append(c.completed_date.strftime("%Y-%m-%d"))

        # Process goals into tiers
        goals_by_tier = []
        for tier in goal_data["tiers"]:
            tier_goals = []
            for goal in tier["goals"]:
                done_dates = completed_lookup.get(goal["name"], [])
                streak = compute_streak(done_dates)
                multiplier = 1.0 + 0.1 * min(streak["current"], 10)
                adjusted_xp = int(goal["xp"] * multiplier)

                tier_goals.append({
                    "name": goal["name"],
                    "xp": goal["xp"],
                    "adjusted_xp": adjusted_xp,
                    "streak": streak,
                    "completed": done_dates
                })

            goals_by_tier.append({
                "tier": tier["tier"],
                "level_range": tier["level_range"],
                "goals": tier_goals
            })

        # Attach all data to spec-like object
        specs.append({
            "name": name,
            "level": level,
            "xp": xp,
            "xp_start": xp_start,
            "xp_end": xp_end,
            "xp_progress": xp_progress,
            "goals_by_tier": goals_by_tier
        })

    today = datetime.utcnow().strftime('%Y-%m-%d')
    return render_template('index.html', specs=specs, quote=SESSION_QUOTE, current_date=today)

@app.route('/complete_goal/<spec_name>/<path:goal_name>', methods=['POST'])
@login_required
def complete_goal(spec_name, goal_name):
    engine = XPEngine(current_user)
    result = engine.complete_goal(spec_name, goal_name)

    if result is None:
        return jsonify({"error": "Goal not found"}), 404

    return jsonify(result)

@app.route('/complete_goal/<spec>/<goal>', methods=['POST'])
@login_required
def complete_goal_handler(spec, goal):  # ✅ Use a different name
    engine = XPEngine(current_user)
    result = engine.complete_goal(spec, goal)
    if result is None:
        return jsonify({'error': 'Invalid goal'}), 400
    return jsonify(result)

@app.route('/stats')
@login_required
def stats():
    user_profile = UserProfile(current_user)
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
    user_profile = UserProfile(current_user)
    user_profile.reset_all_data()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
