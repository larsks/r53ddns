from datetime import datetime
from pony.orm import *

__all__ = [
    'db', 'Account', 'Credentials',
    'Host', 'lookup_user', 
    'setup_database', 'db_session',
    'get', 'select'
]

db = Database()


class Account(db.Entity):
    id = PrimaryKey(int, auto=True)
    created = Required(datetime,
                       default=datetime.now)
    name = Required(str, unique=True)
    password = Required(str)
    is_admin = Required(bool, default=False)
    credentials = Set("Credentials")


class Credentials(db.Entity):
    id = PrimaryKey(int, auto=True)
    owner = Required(Account)
    name = Optional(str)
    accesskey = Required(str)
    secretkey = Required(str)
    hosts = Set("Host")

    composite_key(owner, accesskey, secretkey)
    composite_key(owner, name)


class Host(db.Entity):
    id = PrimaryKey(int, auto=True)
    credentials = Required(Credentials)
    zone = Required(str)
    name = Required(str)

    composite_key(credentials, zone, name)


def setup_database(path):
    db.bind('sqlite', path, create_db=True)
    db.generate_mapping(create_tables=True)


def lookup_user(name_or_id):
    if name_or_id.isdigit():
        return Account[int(name_or_id)]
    else:
        return get(acc for acc in Account
                      if acc.name == name_or_id)


if __name__ == '__main__':
    import sys

    try:
        filename = sys.argv[1]
    except IndexError:
        filename = ':memory:'

    setup_database(filename)
