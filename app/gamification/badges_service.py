# app/gamification/badges_service.py
from sqlalchemy.orm import Session

from app.gamification.badges_models import Badge, UserBadge
from app.certificates.models import Certificate


BADGE_DEFINITIONS = [
    {"name": "SILVER", "threshold_hours": 25},
    {"name": "GOLD", "threshold_hours": 50},
    {"name": "PLATINUM", "threshold_hours": 100},
]


def ensure_badges_seeded(db: Session) -> None:
    existing = {b.name: b for b in db.query(Badge).all()}
    changed = False
    for definition in BADGE_DEFINITIONS:
        if definition["name"] not in existing:
            badge = Badge(
                name=definition["name"],
                threshold_hours=definition["threshold_hours"],
            )
            db.add(badge)
            changed = True
    if changed:
        db.commit()


def award_badges_if_eligible(db: Session, user_id: int, total_hours_current_year: int) -> None:
    ensure_badges_seeded(db)

    badges = db.query(Badge).all()
    existing_user_badges = {
        ub.badge_id: ub
        for ub in db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
    }

    for badge in badges:
        if total_hours_current_year >= badge.threshold_hours and badge.id not in existing_user_badges:
            user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
            db.add(user_badge)
            db.flush()

            cert = Certificate(
                user_id=user_id,
                badge_id=badge.id,
                template_type=badge.name,  # SILVER/GOLD/PLATINUM
                meta=f"Certificate for {badge.name} badge",
            )
            db.add(cert)

    db.commit()
