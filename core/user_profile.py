from core.models import Specialization, GoalCompletion, db
from datetime import datetime

class UserProfile:
    def __init__(self, user):
        self.user = user

    def get_specialization(self, name):
        spec = Specialization.query.filter_by(user_id=self.user.id, name=name).first()
        if not spec:
            spec = Specialization(name=name, user_id=self.user.id, xp=0, level=1)
            db.session.add(spec)
            db.session.commit()
        return spec

    def save_goal_completion(self, spec_name, goal_name):
        spec = self.get_specialization(spec_name)
        today = datetime.utcnow().date()
        exists = GoalCompletion.query.filter_by(specialization_id=spec.id, goal_name=goal_name, completed_date=today).first()
        if not exists:
            db.session.add(GoalCompletion(goal_name=goal_name, specialization_id=spec.id, completed_date=today))
            db.session.commit()

    def reset_all_data(self):
        specs = Specialization.query.filter_by(user_id=self.user.id).all()
        for spec in specs:
            spec.xp = 0
            spec.level = 1
            GoalCompletion.query.filter_by(specialization_id=spec.id).delete()
        db.session.commit()


def compute_streak(completion_dates):
    if not completion_dates:
        return {"current": 0, "best": 0}

    dates = sorted(set(datetime.strptime(d, "%Y-%m-%d").date() for d in completion_dates))
    today = datetime.utcnow().date()

    # Current streak
    streak = 0
    for i in range(len(dates) - 1, -1, -1):
        if (today - dates[i]).days == streak:
            streak += 1
        else:
            break

    # Best streak
    best = 1
    run = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            run += 1
            best = max(best, run)
        else:
            run = 1

    return {"current": streak, "best": best}
