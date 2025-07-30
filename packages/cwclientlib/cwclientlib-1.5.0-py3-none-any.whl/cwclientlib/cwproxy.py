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
# You should have received a copy of the GNU Lesser General Public License
# along with cwclientlib. If not, see <https://www.gnu.org/licenses/>.

"""A CWProxy class wraps a CubicWeb repository.

>>> import cwproxy
>>> p = cwproxy.CWProxy('https://www.cubicweb.org')
>>> a = p.rql('Any X,T WHERE X is Project, X title T')
>>> print(a.json())
"""

import sys
import json
import warnings
import requests
from requests.cookies import CookieConflictError
import hmac
import hashlib
from time import time, sleep
from datetime import datetime, date
from urllib import parse as urlparse
from logilab.common import deprecation
import ssl

from .builders import build_trinfo
from .exceptions import (
    RemoteValidationError,
    NoResultError,
    NoUniqueEntity,
    TaskFailedError,
    FailedToGrabCSRFTokenError,
)

if not getattr(ssl, "HAS_SNI", False):
    try:
        import urllib3.contrib.pyopenssl

        urllib3.contrib.pyopenssl.inject_into_urllib3()
    except ImportError:
        pass

RQLIO_API = "1.0"


class SignedRequestAuth(requests.auth.AuthBase):
    """Auth implementation for CubicWeb with cube signedrequest"""

    hash_algorithm = "SHA512"

    def __init__(self, token_id, secret):
        self.token_id = token_id
        self.secret = secret

    def get_headers_to_sign(self):
        return ("Content-%s" % self.hash_algorithm.upper(), "Content-Type", "Date")

    def __call__(self, req):
        content = b""
        if req.body:
            content = req.body
        if isinstance(content, str):
            content = content.encode("utf-8")
        new_header_name = "Content-%s" % self.hash_algorithm.upper()
        hasher = getattr(hashlib, self.hash_algorithm.lower())
        new_header_value = hasher(content).hexdigest()
        req.headers[new_header_name] = new_header_value
        content_to_sign = (
            req.method
            + req.url
            + "".join(
                req.headers.get(field, "") for field in self.get_headers_to_sign()
            )
        )
        content_signed = hmac.new(
            self.secret.encode("utf-8"),
            content_to_sign.encode("utf-8"),
            digestmod=self.hash_algorithm.lower(),
        ).hexdigest()
        req.headers["Authorization"] = "Cubicweb {}:{}".format(
            self.token_id,
            content_signed,
        )
        return req


class MD5SignedRequestAuth(SignedRequestAuth):
    """
    Like SignedRequestAuth except it signed its requests with MD5

    This is INSECURE, DON'T USED IT except for compatibility reasons
    """

    hash_algorithm = "MD5"

    def __init__(self, token_id, secret):
        super().__init__(token_id, secret)
        warning_message = (
            "WARNING: you are using an INSECURE SIGNING HASH algorithm (md5), please move to "
            "sha512 by using the SignedRequestAuth instead of the MD5SignedRequestAuth. The "
            "MD5SignedRequestAuth class will be removed in the future"
        )
        sys.stderr.write(warning_message + "\n")
        warnings.warn(warning_message, DeprecationWarning)


def date_header_value() -> str:
    return datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")


class CWRqlControllerProxy:
    """CWProxy: A simple helper class to ease building CubicWeb_
        clients. It allows to:

        * execute RQL_ queries remotely (using rqlcontroller_),
        * access instances that requires authentication (using signedrequest_).

    .. _CubicWeb: http://www.cubicweb.org/
    .. _RQL: http://docs.cubicweb.org/annexes/rql/language
    .. _rqlcontroller: http://www.cubicweb.org/project/cubicweb-rqlcontroller/
    .. _signedrequest: http://www.cubicweb.org/project/cubicweb-signedrequest/
    """

    CSRF_TOKEN_COOKIE_NAME = "csrf_token"
    CSRF_TOKEN_COOKIE_POSSIBLE_PATHS = ("/", "/rqlio")

    def __init__(self, base_url: str, auth=None, verify=None, timeout=None):
        """Create a CWProxy connection object to the :base_url: cubicweb app.

        :param auth: can be provided to handle authentication. For a
          cubicweb application providing the signedrequest_ feature,
          one can use the SignedRequestAuth authentifier.

        :param verify: can be False to disable server certificate
          checking, or the path to a CA bundle file.

        """
        purl = urlparse.urlparse(base_url)
        # we do **not** want urls to be built with a double /, (e.g.
        # http://host// or http://host//basepath)
        path = purl.path.strip("/")
        if path:
            path = f"{purl.netloc:s}/{path:s}"
        else:
            path = purl.netloc
        self.base_url = (purl.scheme, path)
        self.auth = auth
        self.timeout = timeout
        self._ssl_verify = verify
        self._default_vid = "jsonexport"  # OR 'ejsonexport'?
        self._session = requests.Session()
        self._base_url = urlparse.urlunparse(self.base_url + ("", None, None, None))
        self._domain = urlparse.urlparse(self._base_url).netloc

    def _get_csrf_token_domained_with_possible_paths(self):
        for path in self.CSRF_TOKEN_COOKIE_POSSIBLE_PATHS:
            value = self._session.cookies.get(
                self.CSRF_TOKEN_COOKIE_NAME, domain=self._domain, path=path
            )
            if value:
                value = value.strip()
                if value:
                    return value

    def _get_csrf_token_from_session(self):
        try:
            # get cookie from session
            return self._session.cookies.get(self.CSRF_TOKEN_COOKIE_NAME)
        except CookieConflictError:
            try:
                # more than one cookie... try to restrict to current domain
                return self._session.cookies.get(
                    self.CSRF_TOKEN_COOKIE_NAME, domain=self._domain
                )
            except CookieConflictError as originalError:
                # more than one cookie... try to restrict to current path
                value = self._get_csrf_token_domained_with_possible_paths()
                if value:
                    return value
                # failure... abandon and raise exception
                error_message = str(originalError)
                multicookies = []
                for cookie in self._session.cookies:
                    if cookie.name == self.CSRF_TOKEN_COOKIE_NAME:
                        multicookies.append(
                            f"domain={cookie.domain} | "
                            f"port={cookie.port} | "
                            f"path={cookie.path}"
                        )
                if multicookies:
                    error_message += (
                        "\nThere are multiples cookies for CSRF token:\n"
                        + "\n".join(multicookies)
                    )
                raise CookieConflictError(error_message)

    def get_csrf_token(self):
        # look for cookie in session
        value = self._get_csrf_token_from_session()
        if value:
            return value
        # no cookie found, make a query to get one
        self._session.get(self._base_url, allow_redirects=False)
        value = self._get_csrf_token_from_session()
        if value:
            return value
        # failure
        raise FailedToGrabCSRFTokenError(
            f"Couldn't grab a CSRF token on website {self._base_url}, this"
            " CubicWeb instance is probably using an insecure version of CubicWeb,"
            " ensure that it is running CubicWeb 3.32.9, 3.33.7 or higher."
        )

    def login(self):
        self._grab_csrf_token()

    def logout(self):
        self._cookies.clear()

    def handle_request(self, method: str, path: str, **kwargs):
        """Construct a requests.Request and send it through this proxy.

        Arguments are that of requests.request() except for `path` which will
        be used to build a full URL using the base URL bound to this proxy.
        """

        msg = "handle_request() got unexpected keyword argument '{}'"
        for unexpected in ("url", "auth"):
            if unexpected in kwargs:
                raise TypeError(msg.format(unexpected))

        default_headers = {
            "Date": date_header_value(),
            "Origin": self._base_url,
        }
        if method != "GET":
            default_headers["X-CSRF-Token"] = self.get_csrf_token()

        kwargs["auth"] = self.auth
        kwargs.setdefault("headers", {}).update(default_headers)
        kwargs.setdefault("verify", self._ssl_verify)
        kwargs.setdefault("timeout", self.timeout)

        url = self.build_url(path)
        return self._session.request(method, url, **kwargs)

    def build_url(self, path: str, query=None):
        """Build the URL to query from self.base_url and the given path

        :param path: can be a string or an iterable of strings; if it
            is a string, it can be a simple path, in which case the
            URL will be built from self.base_url + path, or it can be
            an "absolute URL", in which case it will be queried as is
            (the query argument is then ignored)

        :param query: can be a sequence of two-elements **tuples** or
            a dictionary (ignored if path is an absolute URL)

        """
        if query:
            query = urlparse.urlencode(query, doseq=True)
        if isinstance(path, (list, tuple)):
            path = "/".join(path)
        if path.startswith(self._base_url):
            assert query is None
            return path
        return urlparse.urlunparse(self.base_url + (path, None, query, None))

    def get(self, path: str, query=None):
        """Perform a GET on the cubicweb instance

        :param path: the path part of the URL that will be GET
        :param query: can be a sequence of two-element tuples or a doctionnary
        """
        headers = {"Accept": "application/json"}
        return self.handle_request("GET", path, params=query, headers=headers)

    def post(self, path: str, **data):
        """Perform a POST on the cubicweb instance

        :param path: the path part of the URL that will be GET
        :param **data: will be passed as the 'data' of the request
        """
        kwargs = {
            "headers": {"Accept": "application/json"},
            "data": data,
        }
        if "files" in data:
            kwargs["files"] = data.pop("files")
        return self.handle_request("POST", path, **kwargs)

    def post_json(self, path: str, payload):
        """Perform a POST on the cubicweb instance with application/json
        Content-Type.

        :param path: the path part of the URL that will be GET
        :param payload: native data to be sent as JSON (not encoded)
        """
        kwargs = {
            "headers": {"Accept": "application/json"},
            "json": payload,
        }
        return self.handle_request("POST", path, **kwargs)

    def view(self, vid: str, **args):
        """Perform a GET on <base_url>/view with <vid> and <args>

        :param vid: the vid of the page to retrieve
        :param **args: will be used to build the query string of the URL
        """
        args["vid"] = vid
        return self.get("/view", args)

    def execute(self, rql: str, args=None):
        """CW connection's like execute method.

        :param rql: should be a unicode string or a plain ascii string
        :param args: are the optional parameters used in the query (dict)
        """
        assert isinstance(rql, str), type(rql)
        result = self.rqlio([(rql, args or {})])
        try:
            jsondata = result.json()
        except json.decoder.JSONDecodeError as e:
            raise Exception(
                "Failed to code response as json. Response "
                "(code %s) content:\n> %s\n\nException: %s"
                % (result.status_code, result.content, e)
            )
        # we expect a JSON array on success
        # On failure the JSON is an object with the following shape:
        # {
        #     "data": null,
        #     "title": "ValidationError",
        #     "message": "Missing query argument"
        # }
        if "data" in jsondata and jsondata["data"] is None:
            if result.status_code == 200:
                raise Exception(
                    "Unreadable json. Response "
                    "(code %s) content:\n> %s" % (result.status_code, result.content)
                )
            else:
                raise Exception(
                    f"{result.status_code} {jsondata['title']} {jsondata['message']}"
                )
        return jsondata[0]

    @deprecation.callable_deprecated(
        reason=(
            "client.rql function is deprecated, use client.execute function instead, "
            "this will also fix CSRF errors you might have"
        ),
        version="1.3.0",
    )
    def rql(self, rql: str, path="view", **data):
        """Perform an urlencoded POST to /<path> with rql=<rql>

        :param rql: should be a unicode string or a plain ascii string
        (warning, no string formating is performed)
        :param path: the path part of the generated URL
        :param **data: the 'data' of the request
        """
        if rql.split(maxsplit=1)[0] in ("INSERT", "SET", "DELETE"):
            raise ValueError(
                "You must use the rqlio() method to make " "write RQL queries"
            )

        if not data.get("vid"):
            data["vid"] = self._default_vid
        if path == "view":
            data.setdefault("fallbackvid", "404")
        if rql:  # XXX may be empty?
            if not rql.lstrip().startswith("rql:"):
                # add the 'rql:' prefix to ensure given rql is considered has
                # plain RQL so CubicWeb won't attempt other interpretation
                # (e.g. eid, 2 or 3 word queries, plain text)
                rql = "rql:" + rql
            data["rql"] = rql

        headers = {
            "Accept": "application/json",
            "Date": date_header_value(),
            "Origin": self._base_url,
            "X-CSRF-Token": self.get_csrf_token(),
        }

        params = {
            "url": self.build_url(path),
            "headers": headers,
            "verify": self._ssl_verify,
            "auth": self.auth,
            "data": data,
        }
        return self._session.post(**params)

    def rqlio(self, queries):
        """Multiple RQL for reading/writing data from/to a CW instance.

        :param queries: list of queries, each query being a couple (rql, args)

        Example::

          queries = [('INSERT CWUser U: U login %(login)s, U upassword %(pw)s',
                      {'login': 'babar', 'pw': 'cubicweb rulez & 42'}),
                     ('INSERT CWGroup G: G name %(name)s',
                      {'name': 'pachyderms'}),
                     ('SET U in_group G WHERE G eid %(g)s, U eid %(u)s',
                      {'u': '__r0', 'g': '__r1'}),
                     ('INSERT File F: F data %(content)s, F data_name %(fn)s',
                      {'content': BytesIO('some binary data'),
                       'fn': 'toto.bin'}),
                    ]
          self.rqlio(queries)

        """
        assert not isinstance(queries, str)
        headers = {
            "Accept": "application/json",
            "Date": date_header_value(),
            "Origin": self._base_url,
            "X-CSRF-Token": self.get_csrf_token(),
        }
        files = self.preprocess_queries(queries)

        params = {
            "url": self.build_url(("rqlio", RQLIO_API)),
            "headers": headers,
            "verify": self._ssl_verify,
            "auth": self.auth,
            "files": files,
        }
        posted = self._session.post(**params)
        if posted.status_code in (400, 500):
            try:
                cause = posted.json()
            except Exception as exc:
                raise RemoteValidationError("%s (%s)", exc, posted.text)
            if "reason" in cause:
                # was a RemoteCallFailed
                raise RemoteValidationError(cause["reason"])
            elif "message" in cause:
                raise Exception(cause["message"])
            else:
                raise Exception(f"error {posted.status_code}")
        return posted

    def preprocess_queries(self, queries):
        """Pre process queries arguments to replace binary content by
        files to be inserted in the multipart HTTP query

        :param queries: list of queries, each query being a couple (rql, args)

        Any value that have a read() method will be threated as
        'binary content'.

        In the RQL query, binary value are replaced by unique '__f<N>'
        references (the ref of the file object in the multipart HTTP
        request).
        """

        files = {}
        for query_idx, (rql, args) in enumerate(queries):
            if args is None:
                continue
            for arg_idx, (k, v) in enumerate(args.items()):
                if hasattr(v, "read") and callable(v.read):
                    # file-like object
                    fid = args[k] = "__f%d-%d" % (query_idx, arg_idx)
                    files[fid] = v
                elif isinstance(v, (date, datetime)):
                    args[k] = v.isoformat()
        files["json"] = ("json", json.dumps(queries), "application/json")
        return files

    def _set_rql_request(self, rql_request: str, kwargs, sep=",") -> str:
        args = [
            "X {property_name:s} %({property_name:s})s".format(
                property_name=property_name
            )
            for property_name in kwargs
        ]
        if args:
            if rql_request:
                rql_request = "{:s}{:s} {:s}".format(rql_request, sep, ", ".join(args))
            else:
                rql_request = ", ".join(args)
        return rql_request

    def _rql_args_query(self, rql_request: str, kwargs, sep=",") -> list:
        rql_request = self._set_rql_request(rql_request, kwargs, sep)
        response = self.rqlio([(rql_request, kwargs)])
        response.raise_for_status()
        results = response.json()
        return [row[0] for row in results[0]]

    def count(self, entity_type: str, **kwargs) -> int:
        """Return number of entities with the given type and
        properties in a CW instance.

        :param entity_type: entity type name
        :param kwargs: list of properties with associated values
        :return: number of entities
        :rtype: int

        Example::

          >>> self.count('CWUser')
          3
          >>> self.count('CWUser', login='rms')
          1

        """
        rql_query = "Any COUNT("
        rql_query += "1" if kwargs else "X"
        rql_query += f") WHERE X is {entity_type:s}"
        return int(self._rql_args_query(rql_query, kwargs)[0])

    def exist(self, entity_type: str, **kwargs) -> bool:
        """Return true if there is at least one entity with the given type and
        properties in a CW instance and false otherwise.

        :param entity_type: entity type name
        :param kwargs: list of properties with associated values
        :return: whether such an entity exists
        :rtype: boolean

        Example::

          >>> self.exist('CWUser', login='toto')
          False

        """
        rql_query = "Any "
        rql_query += "1" if kwargs else "X"
        rql_query += f" LIMIT 1 WHERE X is {entity_type:s}"
        try:
            return bool(self._rql_args_query(rql_query, kwargs))
        except RemoteValidationError as e:
            if f"unknown entity type {entity_type:s}" in str(e):
                return False
            raise e

    def find(self, entity_type: str, **kwargs) -> list[int]:
        """Return eid(s) of entitie(s) with the given type and properties in a
        CW instance.

        :param entity_type: entity type name
        :param kwargs: list of properties with associated values
        :return: list of eid(s)
        :rtype: list

        Example::

          >>> self.find('CWUser')
          [20, 21]
          >>> self.find('CWUser', login='admin')
          [20]
        """
        return self._rql_args_query(f"Any X WHERE X is {entity_type:s}", kwargs)

    def find_one(self, entity_type: str, **kwargs) -> int:
        """Return eid of the unique entity with the given type and properties
        in a CW instance. If there is none or multiple, it throws an exception
        that indicates the problem (NoResultError or NoUniqueEntity).

        :param entity_type: entity type name
        :param kwargs: list of properties with associated values
        :return: eid
        :rtype: integer
        :raises NoResultError: there was no matching entity
        :raises NoUniqueEntity: there was multiple matching entities

        Example::

          >>> self.find_one('CWUser', login='admin')
          20
        """
        eids = self._rql_args_query(f"Any X LIMIT 2 WHERE X is {entity_type:s}", kwargs)
        if len(eids) == 0:
            raise NoResultError(f"No result for {entity_type:s}")
        if len(eids) > 1:
            raise NoUniqueEntity(f"Cannot find unique {entity_type:s}")
        return eids[0]

    def find_last_created(self, entity_type: str, **kwargs) -> int:
        """Return eid of the last created entity with the given type and
        properties in a CW instance. If there is none, it throws an exception
        that indicates the problem (NoResultError).

        :param entity_type: entity type name
        :param kwargs: list of properties with associated values
        :return: eid
        :rtype: integer
        :raises NoResultError: there was no matching entity

        Example::

          >>> self.find_last_created('CWUser')
          20
          >>> self.find_last_created('Blog', title='MyBlog')
          22
        """
        eid = self._rql_args_query(
            "Any X ORDERBY D DESC LIMIT 1 "
            "WHERE X is {:s}, X creation_date D".format(entity_type),
            kwargs,
        )
        if not eid:
            raise NoResultError(f"No result for {entity_type:s}")
        return eid[0]

    def get_state(self, eid: int) -> str:
        """Return name of the state of the entity with the given eid or nothing
        if the eid does not exist or if the entity with the given eid has no
        state.

        :param eid: eid of an entity
        :return: the name of the state (if one)
        :rtype: str

        Example::

          >>> self.get_state(1001)
          'wfs_finished'
        """
        response = self.rqlio(
            [
                (
                    "Any SN LIMIT 1 WHERE E eid %(eid)s, E in_state S, S name SN",
                    {"eid": eid},
                )
            ]
        )
        response.raise_for_status()
        rset = response.json()
        if rset and rset[0] and rset[0][0]:
            return rset[0][0][0]
        return None

    def wait_for_status(self, eid: int, status, timeout=60, timesleep=1) -> None:
        """Wait that the entity with given eid to be in status given. If it is
        not the case after timeout, a related exception is raised. The state is
        fetched and checked, then it sleeps if it is not yet the status given.

        :param eid: eid of an entity with a state
        :param status: status to wait for
        :param timeout: maximum time to wait for given status
        :param timesleep: time between each status fetch
        :raises TaskFailedError: status given was not failed and it failed
        :raises TimeoutError: timeout has expired

        Example::

          >>> self.wait_for_status(30, 'wfs_finished')
        """
        start_time = int(time())
        while True:
            sleep(timesleep)
            current_status = self.get_state(eid)
            if current_status == status:
                break
            if current_status == "wfs_failed":
                raise TaskFailedError(eid)
            if int(time()) - start_time >= timeout:
                raise TimeoutError(eid)

    def wait_for_finish(self, eid: int, *args, **kwargs) -> None:
        """Wait that the entity with given eid to be in status finished. If it
        is not the case after timeout, a related exception is raised. The state
        is fetched and checked, then it sleeps if it is not yet in the status
        finished.

        :param eid: eid of an entity with a state
        :param timeout: maximum time to wait for given status
        :param timesleep: time between each status fetch
        :raises TaskFailedError: the task failed according to state
        :raises TimeoutError: timeout has expired

        Example::

          >>> self.wait_for_finish(30)
        """
        return self.wait_for_status(eid, "wfs_finished", *args, **kwargs)

    def change_state(self, eid: int, status: str):
        """Try to change the state with the one given for the entity that have
        the given eid.

        :param eid: eid of an entity with a state
        :param status: new status to set

        Example::

          >>> self.change_state(30, 'wft_start')
        """
        return self.rqlio([build_trinfo(eid, status)])

    def insert(self, entity_type: str, **kwargs):
        """Insert an entity of the given type with given values of attributes.

        :param entity_type: entity type name
        :param kwargs: list of properties with associated values

        Example::

          >>> self.insert('Project', name='start-up nation', author='Macron')
        """
        return self._rql_args_query(f"INSERT {entity_type:s} X: ", kwargs, "")

    def insert_if_not_exist(self, entity_type, **kwargs):
        """Insert an entity of the given type with given values of attributes
        if it does not already exist.

        :param entity_type: entity type name
        :param kwargs: list of properties with associated values

        Example::

          >>> self.insert_if_not_exist('Project', name='cwclientlib')
        """
        if not self.exist(entity_type, **kwargs):
            return self.insert(entity_type, **kwargs)

    def _args_to_rql(self, prop_names):
        return ", ".join(
            f"X {property_name:s} %({property_name:s})s" for property_name in prop_names
        )

    def update_by_eid(self, eid: int, **kwargs):
        """Update entity targeted by eid with given kwargs.

        :param eid: eid of entity to update
        :param kwargs: dict {attributes: values} to set entity with

        Example::

          >>> self.update_by_eid(11, name='neonime', age=33)
        """
        return self.update_batch_by_eid([{"eid": eid, **kwargs}])

    def update_batch_by_eid(self, rows):
        """Update entities targeted by eid with given kwargs.

        :param rows: list of (eid, {attributes: values}) similar
        to update_by_eid

        Example::

            >>> self.update_batch_by_eid([{'eid': 1, 'age':33}),
                                          {'eid': 2, 'name': 'neo'})])
        """
        requests = []
        for row in rows:
            kwargs = row.copy()
            del kwargs["eid"]
            rql_args = self._args_to_rql(kwargs)
            rql_request = f"SET {rql_args:s} WHERE X eid %(eid)s"
            requests.append((rql_request, row))
        response = self.rqlio(requests)
        response.raise_for_status()

    def update_by_restrictions(self, select, **kwargs):
        """Update all entities that match the select triples (kwargs)
        with given kwargs.

        :param select: dict {attributes: values} to select entities to update
        :param kwargs: dict {attributes: values} to set entities with

        Example::

          >>> self.update_by_restrictions({'eid': 11}, name='neonime', age=33)
        """
        restrictions = self._set_rql_request("", select)
        setv = self._set_rql_request("", kwargs)
        rql_request = "SET {:s} WHERE {:s}" "".format(setv, restrictions)
        args = {**select, **kwargs}
        response = self.rqlio([(rql_request, args)])
        response.raise_for_status()

    def delete(self, entity_type: str, **kwargs):
        """Delete all entities that have the given type
        and with given values of attributes.

        :param entity_type: entity type name
        :param kwargs: list of properties with associated values

        Example::

          >>> self.delete('Project', name='start-up nation', author='Macron')
        """
        return self._rql_args_query(f"DELETE {entity_type:s} X WHERE ", kwargs, "")


# for backward compatibility
CWProxy = CWRqlControllerProxy


class CWApiProxy(CWProxy):
    VERSION = "v1"

    def _convert_api_response_to_legacy(
        self,
        posted: requests.models.Response,
    ) -> requests.models.Response:
        """Returns the same response as the legacy CWProxy"""
        json_data = posted.json()
        if "result_sets" in json_data:
            data_content = [rset["rows"] for rset in json_data["result_sets"]]
            posted._content = json.dumps(data_content).encode()
        return posted

    def _convert_resolve_query_reference(self, query: dict | None) -> dict:
        """Replace the query reference for the cube API"""
        data = {}

        if query is not None:
            for key, value in query.items():
                if isinstance(value, str) and value.startswith("__r"):
                    data[key] = {
                        "type": "query_reference",
                        "queryIndex": int(value.removeprefix("__r")),
                        "row": 0,
                        "column": 0,
                    }

                elif isinstance(value, str) and value.startswith("__f"):
                    data[key] = {
                        "type": "binary_reference",
                        "ref": value,
                    }

                # FIXME: use CWProxy.preprocess_queries instead
                elif isinstance(value, (date, datetime)):
                    data[key] = value.isoformat()

                else:
                    data[key] = value

        return data

    def _get_api_route(self, route: str) -> str:
        return f"{self._base_url}/api/{self.VERSION}/{route}"

    def exist(self, entity_type: str, **kwargs) -> bool:
        """Restore the legacy behavior of the exist method with the cube API

        The response of the cube API when the entry do not exists get a status
        code of 400.
        """
        try:
            return super().exist(entity_type, **kwargs)
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 400:
                return False
            raise

    def rqlio(self, queries):
        route = self._get_api_route("rql")
        headers = {
            "Date": date_header_value(),
            "X-Client-Name": "cwclientlib",
            # CSRF custom header necessary for POST requests
            "X-Requested-With": "XMLHttpRequest",
        }

        files = self.preprocess_queries(queries)
        del files["json"]

        translated_queries = [
            {
                "query": query,
                "params": self._convert_resolve_query_reference(value),
            }
            for (query, value) in queries
        ]
        params = {
            "url": route,
            "headers": headers,
            "verify": self._ssl_verify,
            "auth": self.auth,
        }

        if len(files) > 0:
            params["data"] = {"queries": json.dumps(translated_queries)}
            params["files"] = files
        else:
            headers["Accept"] = "application/json"
            headers["Content-Type"] = "application/json"
            params["json"] = translated_queries

        posted = self._session.post(**params)
        if posted.status_code == 500:
            try:
                cause = posted.json()
            except Exception as exc:
                raise RemoteValidationError("%s (%s)", exc, posted.text)
            else:
                if "reason" in cause:
                    # was a RemoteCallFailed
                    raise RemoteValidationError(cause["reason"])
        return self._convert_api_response_to_legacy(posted)

    def rql(self, rql: str, path: str = "view", **kwargs):
        if rql.split(maxsplit=1)[0] in ("INSERT", "SET", "DELETE"):
            raise ValueError(
                "You must use the rqlio() method to make " "write RQL queries"
            )

        results = self.rqlio([(rql, {})])

        json_data = results.json()
        if "result_sets" in json_data or isinstance(json_data, list):
            json_data = json_data[0]

        results._content = json.dumps(json_data).encode()
        return results
