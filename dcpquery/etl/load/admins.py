import uuid

from dcpquery.db.models.admin import User

# todo pull in all relevant info
def get_or_create_user(data):
    return User.get_or_create(uuid=uuid.uuid4(), name=data.get('name'))
