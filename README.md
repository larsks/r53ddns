## About r53ddns

This is simple web service that will update addresses in Amazon's
Route53 DNS service.  It supports multiple users, multiple sets of AWS
credentials per use, and multiple managed hostnames per user.

**NB** r53dns needs a version of [pony][] that includes 
[commit c579cba][], which at the time of this writing is only
available when installing from git.

[commit c579cba]: https://github.com/ponyorm/pony/commit/c579cba754a7d8764d91bc5f1bbcfd74c6d24a1b

## Usage

`r53ddns.app.app` is a standard Python WSGI application.  This
repository can be deployed as is onto [OpenShift][], or you can run it
locally using, for example, [gunicorn][]:

    gunicorn r53ddns.app:app

[openshift]: https://www.openshift.com/
[gunicorn]: http://gunicorn.org/

## Security

This application uses HTTP basic authentication.  You should only
access this application over an SSL encrypted connection with
certificate verification.

Passwords are hashed and salted on the server using the [passlib][]
module's default configuration (which, on 64 bit systems, is 6 rounds
of SHA512-Crypt).

## API

### POST /user/

Create a new user account.

Required values:

- `username`
- `password`

Optional values:

- `is_admin` -- set this to `1` if you want the user to be an
  administrator.

### POST /user/`<username>`/credentials/

Add a new set of AWS credentials to the user account.

Required values:

- `accesskey`
- `secretkey`

Option values:

- `label` -- a label that can be used to refer to these credentials

### POST /user/`<username>`/host/

Add a new host record to the user account.

Required values:

- `credentials` -- credentials id or label that should be used when
  updating this host in Route53.
- `hostname`

Optional values:

- `zone` -- if this is not specified, the zone name is everything
  after the first dot-delimited component of the hostname (e.g., for
  "my.host.example.com", the zone would be "host.example.com" unless
  provided explicitly).

### GET /user/`<username>`/host/`<hostname>`/update

Update the corresponding record set in Route53 with the address of the
client (or the specified address).

Optional values:

- `address` -- Provide an address explicitly, rather than using the
  address of the connecting client.

## Diagnostic Endpoints

- `/ip` -- returns the ip address of the client (like
  <http://icanhazip.com/>).  This is useful for checking what address
  will be set when you send an update request.

- `/debug` -- **[admin]** Returns a JSON dump of the WSGI environment.

## Configuration

r53ddns will load settings from a file named `settings.py` located in
either your current working directory or in `OPENSHIFT_DATA_DIR`.

Available configuration options:

- `DATABASE` -- path to (SQLite) database file
- `ADMIN_NAME` -- name of admin user
- `ADMIN_PASSWORD` -- password of admin user

## Example

- Create a new user account.

        $ curl https://r53ddns.example.com/user/ \
          -d username=lars -d password=macaroni \
          -u admin:secret
        {
          "status": "created", 
          "data": {
            "password": "macaroni", 
            "is_admin": false, 
            "id": 1, 
            "name": "lars", 
            "created": "2015-04-09 15:30:51.209231"
          }
        }

- Add a set of AWS credentials:

        $ curl https://r53ddns.example.com/user/lars/credentials/ \
          -d accesskey=123456 \
          -d secretkey=abcdef \
          -d label=default \
          -u lars:macaroni
        {
          "status": "created", 
          "data": {
            "owner": 1, 
            "secretkey": "abcdef", 
            "accesskey": "123456", 
            "id": 1, 
            "name": "default"
          }
        }

- Add a host record:

        $ curl https://r53ddns.example.com/user/lars/host/ \
          -d hostname=r53-test.oddbit.com \
          -d credentials=default \
          -u lars:macaroni
        {
          "status": "created", 
          "data": {
            "credentials": 1, 
            "id": 1, 
            "zone": "oddbit.com", 
            "name": "r53-test.oddbit.com"
          }
        }

- Update the address in AWS Route53:

        $ curl https://r53ddns.example.com/user/lars/host/r53-test.oddbit.com/update \
          -u lars:macaroni
        {
          "status": "updated", 
          "data": {
            "address": "10.0.0.97"
          }
        }

## Bugs

Please report bugs using the GitHub issue tracker at
<https://github.com/larsks/r53ddns/issues>.

## License

r53ddns -- dynamic dns server for Route53
Copyright (C) 2015 Lars Kellogg-Stedman

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
