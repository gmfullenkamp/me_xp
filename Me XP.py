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

@app.route('/reset')
def reset():
    user_profile.reset_all_data()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
