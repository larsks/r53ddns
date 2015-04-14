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

from fresco import Response
from fresco.exceptions import *


class Conflict (ResponseException):

    '''The request could not be completed due to a conflict with the
    current state of the resource. This code is only allowed in situations
    where it is expected that the user might be able to resolve the
    conflict and resubmit the request.'''

    response = Response(['Conflict'],
                        status=409)
