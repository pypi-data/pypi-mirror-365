# copyright 2014-2021 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact https://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of cwclientlib.
#
# cwclientlib is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# cwclientlib is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with cwclientlib. If not, see <https://www.gnu.org/licenses/>.


class RemoteValidationError(Exception):
    pass


class NoResultError(Exception):
    "CWProxy.find*() called but result set is empty"


class NoUniqueEntity(Exception):
    "CWProxy.find_one() called but result set contains more than one entity"


class TaskFailedError(Exception):
    pass


class FailedToGrabCSRFTokenError(Exception):
    pass
