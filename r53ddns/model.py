# r53ddns -- dynamic dns server for Route53
# Copyright (C) 2015 Lars Kellogg-Stedman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime
from pony.orm import *

__all__ = [
    'db',
    'Account',
    'Credentials',
    'Host',
    'setup_database',
    'db_session',
    'get',
    'select'
]

db = Database()


class Account(db.Entity):
    '''A user account for accessing this web service.'''

    id = PrimaryKey(int, auto=True)
    created = Required(datetime,
                       default=datetime.utcnow)
    name = Required(str, unique=True)
    password = Required(str)
    is_admin = Required(bool, default=False)
    credentials = Set("Credentials")


class Credentials(db.Entity):
    '''A set of credentials for accessing AWS services (in particular,
    Route53).'''

    id = PrimaryKey(int, auto=True)
    owner = Required(Account)
    name = Optional(str)
    accesskey = Required(str)
    secretkey = Required(str)
    hosts = Set("Host",
                cascade_delete=False)
    created = Required(datetime,
                       default=datetime.utcnow)

    composite_key(owner, accesskey, secretkey)
    composite_key(owner, name)


class Host(db.Entity):
    '''Associates a hostname with the set of credentials that should be
    used for updates.'''

    id = PrimaryKey(int, auto=True)
    credentials = Required(Credentials)
    zone = Required(str)
    name = Required(str)
    created = Required(datetime,
                       default=datetime.utcnow)
    last_update = Required(datetime,
                           default=datetime.utcnow)
    last_address = Optional(str)

    composite_key(credentials, zone, name)


def setup_database(path):
    '''Bind the database to a particular driver.'''
    db.bind('sqlite', path, create_db=True)
    db.generate_mapping(create_tables=True)


get.__doc__ = '''A Pony ORM method for obtaining a single result from the
database.'''

select.__doc__ = '''A Pony ORM method for obtaining multiple results from
the database.'''
