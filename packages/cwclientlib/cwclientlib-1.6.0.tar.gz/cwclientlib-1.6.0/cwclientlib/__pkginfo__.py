# pylint: disable=W0622
# copyright 2014-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
# You should have received a copy of the GNU Lesser General Public
# License along with cwclientlib. If not, see <https://www.gnu.org/licenses/>.

"""cwclientlib application packaging information"""

import sys

modname = "cwclientlib"
distname = "cwclientlib"

numversion = (1, 6, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "A Python library to easily build CubicWeb clients"
web = "https://forge.extranet.logilab.fr/cubicweb/%s" % distname

cliversion = ""
if sys.version_info[0] > 2:
    cliversion = "3"
console_scripts = [
    f"cwrql{cliversion}=cwclientlib.cwrql:main",
    f"cwget{cliversion}=cwclientlib.cwget:main",
    f"cwshell{cliversion}=cwclientlib.cwshell:main",
    f"cwupdate{cliversion}=cwclientlib.cwupdate:main",
]

install_requires = [
    "requests >= 2",
    "logilab.common >= 2",
    "babel >= 2.17, < 3.0",
]
extras_require = {
    "yaml": ["PyYAML"],
}
test_suite = "cwclientlib.test"
tests_require = [
    "cubicweb >= 5, < 6.0",
    "cubicweb-signedrequest",
    "cubicweb-rqlcontroller",
    "cubicweb-file",
    "cubicweb-api >= 0.17.1",
    "cubicweb-web",
    "twisted",
    "pyramid",
    "PyYAML",
    "requests",
    "logilab.common",
]

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
]
