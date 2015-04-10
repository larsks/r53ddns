## About r53ddns

This is simple web service that will update addresses in Amazon's
Route53 DNS service.  It supports multiple users, multiple sets of AWS
credentials per use, and multiple managed hostnames per user.

## Usage

`r53ddns.app.app` is a standard Python WSGI application.  This
repository can be deployed as is onto [OpenShift][], or you can run it
locally using, for example, [gunicorn][]:

    gunicorn r53ddns.app:app

[openshift]: https://www.openshift.com/
[gunicorn]: http://gunicorn.org/

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

- `credname` -- a label that can be used to refer to these credentials

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
