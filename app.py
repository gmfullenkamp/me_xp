import glob
import json
import os
import random
from datetime import datetime

from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)

from constants import QUOTES
from core.auth import get_user, register_user
from core.models import GoalCompletion, Specialization, User, db
from core.user_profile import UserProfile, compute_streak
from core.xp_engine import XPEngine

# Global quote cache
SESSION_QUOTE = random.choice(QUOTES)

# Init Flask and Login Manager
app = Flask(__name__)
app.secret_key = "super-secret-key"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    os.environ.get("DATABASE_URL") or "sqlite:///dev.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = register_user(username, password)
        if user:
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Username already exists")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = get_user(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
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
        xp_required_to_level = lambda l: sum(
            int(100 * (1.1 ** (i - 1))) for i in range(1, l)
        )
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
            completed_lookup.setdefault(c.goal_name, []).append(
                c.completed_date.strftime("%Y-%m-%d")
            )

        # Process goals into tiers
        goals_by_tier = []
        for tier in goal_data["tiers"]:
            tier_goals = []
            for goal in tier["goals"]:
                done_dates = completed_lookup.get(goal["name"], [])
                streak = compute_streak(done_dates)
                multiplier = 1.0 + 0.1 * min(streak["current"], 10)
                adjusted_xp = int(goal["xp"] * multiplier)

                tier_goals.append(
                    {
                        "name": goal["name"],
                        "xp": goal["xp"],
                        "adjusted_xp": adjusted_xp,
                        "streak": streak,
                        "completed": done_dates,
                    }
                )

            goals_by_tier.append(
                {
                    "tier": tier["tier"],
                    "level_range": tier["level_range"],
                    "goals": tier_goals,
                }
            )

        # Attach all data to spec-like object
        specs.append(
            {
                "name": name,
                "level": level,
                "xp": xp,
                "xp_start": xp_start,
                "xp_end": xp_end,
                "xp_progress": xp_progress,
                "goals_by_tier": goals_by_tier,
            }
        )

    today = datetime.utcnow().strftime("%Y-%m-%d")
    return render_template(
        "index.html", specs=specs, quote=SESSION_QUOTE, current_date=today
    )


@app.route("/complete_goal/<spec_name>/<path:goal_name>", methods=["POST"])
@login_required
def complete_goal(spec_name, goal_name):
    engine = XPEngine(current_user)
    result = engine.complete_goal(spec_name, goal_name)

    if result is None:
        return jsonify({"error": "Goal not found"}), 404

    return jsonify(result)


@app.route("/complete_goal/<spec>/<goal>", methods=["POST"])
@login_required
def complete_goal_handler(spec, goal):  # ✅ Use a different name
    engine = XPEngine(current_user)
    result = engine.complete_goal(spec, goal)
    if result is None:
        return jsonify({"error": "Invalid goal"}), 400
    return jsonify(result)


@app.route("/stats")
@login_required
def stats():
    specializations = Specialization.query.filter_by(user_id=current_user.id).all()

    stats_data = {
        "overall": {
            "first_completed": None,
            "total_completed": 0,
            "most_done_goal": None,
            "most_done_count": 0,
        },
        "specializations": {},
    }

    goal_counts = {}

    for spec in specializations:
        completions = GoalCompletion.query.filter_by(specialization_id=spec.id).all()
        dates = [c.completed_date for c in completions]
        goal_names = [c.goal_name for c in completions]

        if dates:
            first = min(dates).strftime("%Y-%m-%d")
        else:
            first = "N/A"

        spec_goal_counts = {}
        for name in goal_names:
            spec_goal_counts[name] = spec_goal_counts.get(name, 0) + 1
            goal_counts[name] = goal_counts.get(name, 0) + 1

        if spec_goal_counts:
            most_done = max(spec_goal_counts, key=spec_goal_counts.get)
            most_count = spec_goal_counts[most_done]
        else:
            most_done, most_count = "N/A", 0

        best_streak = 0
        best_streak_goal = "N/A"
        for name in set(goal_names):
            dates = [
                c.completed_date.strftime("%Y-%m-%d")
                for c in completions
                if c.goal_name == name
            ]
            streak = compute_streak(dates)
            if streak["best"] > best_streak:
                best_streak = streak["best"]
                best_streak_goal = name

        stats_data["specializations"][spec.name] = {
            "first_completed": first,
            "total_completed": len(completions),
            "most_done_goal": most_done,
            "most_done_count": most_count,
            "best_streak_goal": best_streak_goal,
            "best_streak_count": best_streak,
        }

    if goal_counts:
        overall_most_done = max(goal_counts, key=goal_counts.get)
        overall_most_count = goal_counts[overall_most_done]
    else:
        overall_most_done, overall_most_count = "N/A", 0

    first_dates = [
        c.completed_date
        for spec in specializations
        for c in GoalCompletion.query.filter_by(specialization_id=spec.id)
    ]
    stats_data["overall"]["first_completed"] = (
        min(first_dates).strftime("%Y-%m-%d") if first_dates else "N/A"
    )
    stats_data["overall"]["total_completed"] = sum(goal_counts.values())
    stats_data["overall"]["most_done_goal"] = overall_most_done
    stats_data["overall"]["most_done_count"] = overall_most_count

    return jsonify(stats_data)


@app.route("/reset")
@login_required
def reset():
    user_profile = UserProfile(current_user)
    user_profile.reset_all_data()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
