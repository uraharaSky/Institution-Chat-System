from models import db
from models import Notification


def create_notification(user_id, title, message, type="general", ref_id=None, ref_type=None):
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        reference_id=ref_id,
        reference_type=ref_type
    )
    db.session.add(notif)