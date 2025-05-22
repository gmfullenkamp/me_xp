from flask import Flask, render_template, redirect, url_for, jsonify
from core.user_profile import UserProfile
import os
import glob
import random
from datetime import datetime
from constants import QUOTES

# Global quote cache
SESSION_QUOTE = random.choice(QUOTES)

app = Flask(__name__)
user_profile = UserProfile()

@app.route('/')
def index():
    # Load all specializations from the JSON files
    spec_files = glob.glob(os.path.join("specializations", "*_goals.json"))
    spec_names = [os.path.basename(f).replace("_goals.json", "") for f in spec_files]
    specs = [user_profile.get_specialization(name) for name in spec_names]
    
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('index.html', specs=specs, quote=SESSION_QUOTE, current_date=today)

@app.route('/complete_goal/<spec_name>/<goal_name>', methods=['POST'])
def complete_goal(spec_name, goal_name):
    spec = user_profile.get_specialization(spec_name)
    awarded = spec.complete_goal(goal_name)
    user_profile.save_specialization(spec)

    streak = spec.get_streak(goal_name)
    xp = spec.progress["xp"]
    level = spec.progress["level"]
    current = xp % 100
    target = level * 100
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
def stats():
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
def reset():
    user_profile.reset_all_data()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
