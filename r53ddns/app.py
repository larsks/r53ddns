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

from fresco import FrescoApp
import logging

import r53ddns.views as views
import r53ddns.model as model
import r53ddns.utils as utils

LOG = logging.getLogger(__name__)

config = {
    'DATABASE': 'sample.db',
    'ADMIN_NAME': 'admin',
}


class R53DDNS (FrescoApp):
    def __init__(self, config_file='settings.py'):
        super(R53DDNS, self).__init__()

        self.config_file = config_file

        self.setup_config()
        self.setup_routes()
        self.setup_request()
        self.setup_database()

    def setup_database(self):
        model.setup_database(self.options.DATABASE)

    def setup_request(self):
        self.process_request(utils.extract_auth_info)

    def setup_config(self):
        self.options.update(config)
        self.options.update_from_file(
            self.config_file)

    def setup_routes(self):
        self.include('/user/<username:str>/credentials',
                     views.CredentialManager())
        self.include('/user/<username:str>/host',
                     views.HostManager())
        self.include('/user',
                     views.UserManager())
        self.include('/',
                     views.RootManager())
