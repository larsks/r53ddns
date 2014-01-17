#!/usr/bin/env python

import bottle
import os
import route53
import sys
import yaml


app = bottle.app()
data_dir = os.environ.get('OPENSHIFT_DATA_DIR', '.')
cfgpath = os.path.join(data_dir, 'config.yml')
with open(cfgpath) as fd:
    cfg = yaml.load(fd)


def find_registration(hostname):
    if not hostname in cfg['registrations']:
        raise KeyError(hostname)

    host = cfg['registrations'][hostname]
    host['hostname'] = hostname
    return host


def check_access(host):
    return bottle.request.params['secret'] == host['secret']


def find_recordset(host):
    user = cfg['users'][host['user']]
    conn = route53.connect(user['aws_access_key_id'],
                           user['aws_secret_access_key'])

    try:
        zone = conn.get_hosted_zone_by_id(host['zone_id'])
    except TypeError:
        raise KeyError('zone id %(zone_id)s' % host)

    for rs in zone.record_sets:
        print rs.name, rs.rrset_type
        if not rs.name == host['hostname'] + '.':
            continue
        if not rs.rrset_type == 'A':
            continue
        if not len(rs.records) <= 1:
            continue

        break
    else:
        raise KeyError('recordset %(hostname)s' % host)

    return rs


@app.route('/update/:hostname', method='post')
def update(hostname):
    try:
        host = find_registration(hostname)

        if not check_access(host):
            raise bottle.HTTPError(403)

        rs = find_recordset(host)

        old_addr = rs.records[0]
        rs.records = [bottle.request.remote_addr]
        rs.ttl = 60
        rs.save()

        return old_addr, bottle.request.remote_addr
    except KeyError as detail:
        raise bottle.HTTPError(404, str(detail))


@app.route('/status/:hostname')
def status(hostname):
    try:
        host = find_registration(hostname)

        if not check_access(host):
            raise bottle.HTTPError(403)

        rs = find_recordset(host)
        return rs.records[0]
    except KeyError as detail:
        raise bottle.HTTPError(404, str(detail))


@app.route('/check')
def check():
    return bottle.request.remote_addr

