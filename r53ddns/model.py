from datetime import datetime
from pony.orm import *

__all__ = [
    'db', 'Account', 'Credentials',
    'Host', 'lookup_user',
    'lookup_credentials_for',
    'lookup_host_for',
    'setup_database', 'db_session',
    'get', 'select'
]

db = Database()


class Account(db.Entity):
    id = PrimaryKey(int, auto=True)
    created = Required(datetime,
                       default=datetime.utcnow)
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
    created = Required(datetime,
                           default=datetime.utcnow)

    composite_key(owner, accesskey, secretkey)
    composite_key(owner, name)


class Host(db.Entity):
    id = PrimaryKey(int, auto=True)
    credentials = Required(Credentials)
    zone = Required(str)
    name = Required(str)
    created = Required(datetime,
                           default=datetime.utcnow)
    last_update = Required(datetime,
                           default=datetime.utcnow)

    composite_key(credentials, zone, name)


def setup_database(path):
    db.bind('sqlite', path, create_db=True)
    db.generate_mapping(create_tables=True)


def lookup_user(name_or_id):
    if name_or_id.isdigit():
        return Account[int(name_or_id)]
    else:
        return get(obj for obj in Account
                   if obj.name == name_or_id)


def lookup_credentials_for(account, name_or_id):
    if name_or_id.isdigit():
        return get(c for c in Credentials
                   if c.owner.id == account.id and
                   c.id == name_or_id)
    else:
        return get(c for c in Credentials
                   if c.owner.id == account.id and
                   c.name == name_or_id)


def lookup_host_for(account, name_or_id):
    if name_or_id.isdigit():
        return get(h for h in Host
                   if h.credentials.owner.id == account.id and
                   h.id == name_or_id)
    else:
        return get(h for h in Host
                   if h.credentials.owner.id == account.id and
                   h.name == name_or_id)

if __name__ == '__main__':
    import sys

    try:
        filename = sys.argv[1]
    except IndexError:
        filename = ':memory:'

    setup_database(filename)
