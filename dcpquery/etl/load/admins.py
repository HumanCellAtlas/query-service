from dcpquery.db.models.admin import User

# todo pull in all relevant info
def get_or_create_user(data):
    return User(name=data.get('name'))
