#!/usr/bin/python
#
# copyright 2014-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
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
# along with cwclientlib. If not, see <http://www.gnu.org/licenses/>.

import sys
import csv

from requests import HTTPError

from cwclientlib import cwproxy_for, get_config
from cwclientlib.cwproxy import CWProxy

import argparse

try:
    import argcomplete
except ImportError:
    argcomplete = None

csv.register_dialect("semicolon", delimiter=";")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "endpoint", nargs=1, choices=sorted(get_config()), help="endpoint"
    )
    parser.add_argument("path", nargs=1, help="path to csv file")
    parser.add_argument(
        "-n",
        "--dry-run",
        dest="dry_run",
        default=False,
        action="store_true",
        help="Print queries without executing them",
    )
    parser.add_argument(
        "-d",
        dest="csv_dialect",
        default="unix",
        help=f"csv dialect to use when reading data: {csv.list_dialects()}",
    )

    if argcomplete is not None:
        argcomplete.autocomplete(parser)
    args = parser.parse_args()

    url = args.endpoint[0]
    filepath = args.path[0]

    # create client
    try:
        client = cwproxy_for(url)
    except ValueError:
        if url.startswith(("http://", "https://")):
            client = CWProxy(url)
        else:
            raise

    # read data
    with open(filepath) as fobj:
        reader = csv.DictReader(fobj, dialect=args.csv_dialect)
        update_list = list(reader)

    # run
    if args.dry_run:
        print(update_list)
    else:
        try:
            client.update_batch_by_eid(update_list)
        except HTTPError as exc:
            print(
                f"** Request failed: {exc}",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
