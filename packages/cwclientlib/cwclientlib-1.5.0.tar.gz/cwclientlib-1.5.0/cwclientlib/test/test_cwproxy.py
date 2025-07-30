# copyright 2014-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
# along with cwclientlib. If not, see <https://www.gnu.org/licenses/>.

from io import BytesIO
import json
from datetime import date, datetime, timedelta

import pytz

import unittest

from cwclientlib.cwproxy import (
    CWRqlControllerProxy,
    CWApiProxy,
    SignedRequestAuth,
    NoResultError,
    NoUniqueEntity,
)

from cubicweb.devtools.httptest import CubicWebServerTC
from cubicweb_web.devtools.testlib import PyramidWebCWTC


class CWProxyClientTC(CubicWebServerTC, PyramidWebCWTC):
    """Basic tests for CWProxy"""

    proxy_cls = CWRqlControllerProxy

    def setup_database(self):
        with self.admin_access.client_cnx() as cnx:
            token = cnx.create_entity(
                "AuthToken",
                id="testing",
                enabled=True,
                token_for_user=cnx.user.eid,
                expiration_date=datetime.now(pytz.timezone("Europe/Paris"))
                + timedelta(days=1),
            )
            self.admineid = cnx.user.eid
            self.token_id = token.id
            self.token_secret = token.token
            cnx.commit()

    def _addUser(self, login: str, password: str, group_name: str = "users"):
        queries = [
            (
                "INSERT CWUser U: U login %(login)s, U upassword %(pw)s, "
                "U in_group G WHERE G name %(group_name)s",
                {"login": login, "pw": password, "group_name": group_name},
            )
        ]
        results = self.client.rqlio(queries).json()
        self.assertTrue(results)
        eid = results[0][0][0]
        return eid

    @property
    def client(self):
        auth = SignedRequestAuth(token_id=self.token_id, secret=self.token_secret)
        base_url = self.config["base-url"]
        return self.proxy_cls(base_url=base_url, auth=auth)

    def test_rql(self):
        self.assertEqual(
            [["admin"], ["anon"]], self.client.rql("Any L WHERE U login L").json()
        )

        self.assertEqual(
            [[self.admineid]], self.client.rql('Any U WHERE U login "admin"').json()
        )

    def test_execute(self):
        self.assertEqual(
            [[self.admineid]],
            self.client.execute("Any U WHERE U login %(l)s", {"l": "admin"}),
        )

    def test_rql_vid(self):
        admin = self.client.rql(
            'Any U WHERE U login "admin"', vid="ejsonexport"
        ).json()[0]
        self.assertIn("login", admin.keys())

    def test_rql_path(self):
        result = self.client.rql(
            'Any U WHERE U login "admin"', path="test-controller"
        ).text
        self.assertEqual("coucou", result)

    def test_bad_rql_path(self):
        result = self.client.rql('CWGroup U WHERE U login "admin"')
        self.assertEqual(result.status_code, 500)

    def test_rqlio(self):
        queries = [
            (
                "INSERT CWUser U: U login %(login)s, U upassword %(pw)s",
                {"login": "babar", "pw": "cubicweb rulez & 42"},
            ),
            ("INSERT CWGroup G: G name %(name)s", {"name": "pachyderms"}),
            (
                "SET U in_group G WHERE G eid %(g)s, U eid %(u)s",
                {"u": "__r0", "g": "__r1"},
            ),
        ]

        results = self.client.rqlio(queries).json()
        self.assertEqual(3, len(results))
        babar = results[0][0][0]
        pach = results[1][0][0]

        with self.admin_access.client_cnx() as cnx:
            users = cnx.find("CWUser", eid=babar)
            self.assertEqual(1, len(users))
            self.assertEqual("babar", users.one().login)

            groups = cnx.find("CWGroup", eid=pach)
            self.assertEqual(1, len(groups))
            self.assertEqual("pachyderms", groups.one().name)

        self.assertEqual([babar, pach], results[2][0])

    def test_rqlio_no_kwargs(self):
        queries = [
            (
                'INSERT CWUser U: U login "babar", '
                'U upassword "cubicweb rulez & 42", '
                'U in_group G WHERE G name "users"',
                None,
            ),
        ]
        results = self.client.rqlio(queries).json()
        self.assertEqual(1, len(results))
        babar = results[0][0][0]
        with self.admin_access.client_cnx() as cnx:
            users = cnx.find("CWUser", eid=babar)
            self.assertEqual(1, len(users))
            self.assertEqual("babar", users.one().login)

    def test_rqlio_multiple_binary_arguments(self):
        queries = [
            (
                'INSERT User X: X name "babar",'
                " X picture %(picture)s, X ssh_pubkey %(ssh_pubkey)s",
                {"picture": BytesIO(b"nice photo"), "ssh_pubkey": BytesIO(b"12345")},
            ),
        ]

        eid = self.client.rqlio(queries).json()[0][0][0]
        with self.admin_access.client_cnx() as cnx:
            user = cnx.entity_from_eid(eid)
            self.assertEqual(user.picture.getvalue(), b"nice photo")
            self.assertEqual(user.ssh_pubkey.getvalue(), b"12345")

    def test_rqlio_datetime(self):
        md = datetime.now(pytz.timezone("Europe/Paris")) - timedelta(days=1)
        queries = [
            (
                'INSERT CWUser U: U login "babar", '
                "U creation_date %(cd)s, "
                "U modification_date %(md)s, "
                'U upassword "cubicweb rulez & 42", '
                'U in_group G WHERE G name "users"',
                {"cd": md, "md": md},
            ),
        ]

        eid = self.client.rqlio(queries).json()[0][0][0]
        with self.admin_access.client_cnx() as cnx:
            user = cnx.entity_from_eid(eid)
            self.assertEqual(md, user.creation_date)
            self.assertEqual(md, user.modification_date)

        # actually only check date type is handled, we can't expect a
        # given number of entities as it depends on the database cache
        # creation time
        res = self.client.execute(
            "CWUser X WHERE X creation_date < %(today)s", {"today": date.today()}
        )
        self.assertTrue(res)

    def test_use_rql_then_rqlio(self):
        response = self.client.rql("Any X LIMIT 1 WHERE X is CWEType")
        self.assertTrue(response.ok)
        response = self.client.rqlio([("Any X LIMIT 1 WHERE X is CWEType", None)])

    def test_use_rqlio_then_rql(self):
        response = self.client.rqlio([("Any X LIMIT 1 WHERE X is CWEType", None)])
        self.assertTrue(response.ok)
        response = self.client.rql("Any X LIMIT 1 WHERE X is CWEType")
        self.assertTrue(response.ok)

    def test_exist(self):
        eid = self._addUser("babar", "cubicweb rulez & 42")

        self.assertTrue(self.client.exist("CWUser"))
        self.assertTrue(self.client.exist("CWUser", login="babar"))
        self.assertTrue(self.client.exist("CWUser", eid=eid))
        self.assertTrue(self.client.exist("CWUser", eid=eid, login="babar"))
        self.assertFalse(self.client.exist("CWNothing"))
        self.assertFalse(
            self.client.exist("CWUser", login="Sauron", upassword="DOMINATION")
        )

    def test_count(self):
        nb = self.client.count("CWUser")
        self._addUser("Richard Stallman", "GNU")
        self.assertEqual(self.client.count("CWUser"), nb + 1)
        self._addUser("Jimmy Wales", "Wikipédia")
        self.assertEqual(self.client.count("CWUser"), nb + 2)
        self.assertEqual(self.client.count("CWUser", login="Richard Stallman"), 1)

    def test_find(self):
        eid_babar = self._addUser("babar", "cubicweb rulez & 42")
        eid_sacha = self._addUser("sacha", "catch them all!")

        results = self.client.find("CWUser")
        self.assertTrue(results)
        self.assertIn(eid_babar, (row for row in results))
        self.assertIn(eid_sacha, (row for row in results))

        results = self.client.find("CWUser", login="babar")
        self.assertTrue(results)
        self.assertEqual(results[0], eid_babar)

        results = self.client.find("CWUser", eid=eid_babar, login="babar")
        self.assertTrue(results)
        self.assertEqual(results[0], eid_babar)

        self.assertFalse(self.client.find("CWUser", login="Bill Gates"))

    def test_find_one(self):
        eid_rms = self._addUser("Richard Stallman", "GNU")
        eid_jim = self._addUser("Jimmy Wales", "Wikipédia")

        self.assertEqual(
            self.client.find_one("CWUser", login="Richard Stallman"), eid_rms
        )
        self.assertEqual(self.client.find_one("CWUser", login="Jimmy Wales"), eid_jim)

        with self.assertRaises(NoResultError):
            self.client.find_one("CWUser", login="Bill Gates")

        with self.assertRaises(NoUniqueEntity):
            self.client.find_one("CWUser")

    def test_find_last_created(self):
        eid = self._addUser("Hurd", "GNU")
        self.assertEqual(self.client.find_last_created("CWUser"), eid)

        eid = self._addUser("Linux", "Linus")
        self.assertEqual(self.client.find_last_created("CWUser"), eid)

    def test_get_state(self):
        eid = self._addUser("Hurd", "GNU")
        self.assertEqual(self.client.get_state(eid), "activated")

    def test_wait_for_status(self):
        eid = self._addUser("Hurd", "GNU")
        self.client.wait_for_status(eid, "activated")

        with self.assertRaises(TimeoutError):
            self.client.wait_for_status(eid, "wfs_failed", 0, 0)

    def test_wait_for_finish(self):
        eid = self._addUser("Hurd", "GNU")
        with self.assertRaises(TimeoutError):
            self.client.wait_for_finish(eid, 0, 0)

    def test_handle_request(self):
        with self.admin_access.cnx() as cnx:
            eid = cnx.find("CWUser", login="admin")[0][0]
        response = self.client.handle_request(
            "GET",
            f"cwuser/{eid}",
            headers={"Accept": "application/custom+json"},
        )
        # XXX getting 403 (as in test_get/test_view), don't know why.
        # self.assertEqual(response.status_code, 200)
        request = response.request
        self.assertEqual(request.method, "GET")
        self.assertEqual(
            request.url, "{}cwuser/{}".format(self.config["base-url"], eid)
        )
        headers = request.headers
        self.assertEqual(headers["Accept"], "application/custom+json")
        self.assertIn("Date", headers)
        self.assertIn("Authorization", headers)
        self.assertIn("Content-SHA512", headers)
        self.assertIn("Cubicweb testing:", headers["Authorization"])

    def test_handle_request_bad_parameter(self):
        with self.assertRaisesRegex(TypeError, "got unexpected keyword argument 'url'"):
            self.client.handle_request("GET", 1, url="x")

    @unittest.skip("to be completed and make pass")
    def test_get(self):
        with self.admin_access.client_cnx() as cnx:
            eid = cnx.find("CWEType", name="CWUser")[0][0]
        response = self.client.get(f"/cwetype/{eid}")
        self.assertEqual(response.status_code, 200)

    @unittest.skip("to be completed and make pass")
    def test_view(self):
        vid = "jsonexport"
        with self.admin_access.web_request() as req:
            rset = req.find("CWEType", name="CWUser")
            json_view = req.view(vid, rset=rset)
        response = self.client.view(vid, eid=rset[0][0])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), json_view[0])

    def test_post(self):
        files = [("myfile", BytesIO(b"some content"))]
        data = dict(a="hello", files=files)
        response = self.client.post("/foo/bar", **data)
        self.assertEqual(response.status_code, 404)
        request = response.request
        self.assertEqual(request.method, "POST")
        headers = request.headers
        content_type, _ = headers["Content-Type"].split("; ", 1)
        self.assertEqual(content_type, "multipart/form-data")
        bodylines = request.body.splitlines()
        self.assertIn(b'Content-Disposition: form-data; name="a"', bodylines)
        self.assertIn(b"hello", bodylines)
        self.assertIn(
            b'Content-Disposition: form-data; name="myfile"; ' b'filename="myfile"',
            bodylines,
        )
        self.assertIn(b"some content", bodylines)

    def test_post_json(self):
        data = {"foo": 1}
        response = self.client.post_json("/foo/bar", data)
        self.assertEqual(response.status_code, 404)
        request = response.request
        self.assertEqual(request.method, "POST")
        headers = request.headers
        content_type = headers["Content-Type"]
        self.assertEqual(content_type, "application/json")
        body = request.body
        self.assertEqual(json.loads(body.decode("utf-8")), data)

    def test_insert(self):
        self.assertFalse(self.client.find("EmailAddress", alias="CSE"))
        self.client.insert("EmailAddress", alias="CSE", address="dp@logilab.fr")
        self.assertTrue(self.client.find("EmailAddress", alias="CSE"))

    def test_insert_if_not_exist(self):
        self.assertFalse(self.client.find("EmailAddress", alias="CSE"))
        self.client.insert_if_not_exist(
            "EmailAddress", alias="CSE", address="dp@logilab.fr"
        )
        self.assertEqual(self.client.count("EmailAddress", alias="CSE"), 1)
        self.client.insert_if_not_exist(
            "EmailAddress", alias="CSE", address="dp@logilab.fr"
        )
        self.assertEqual(self.client.count("EmailAddress", alias="CSE"), 1)

    def test_update_by_eid(self):
        self.assertFalse(self.client.find("EmailAddress", alias="juliette"))
        result = self.client.insert(
            "EmailAddress", alias="juliette", address="juliette@romance.org"
        )
        eid = result[0]
        self.assertTrue(self.client.find("EmailAddress", alias="juliette"))
        self.client.update_by_eid(eid, alias="romeo")
        self.assertTrue(self.client.find("EmailAddress", alias="romeo"))

    def test_update_batch_by_eid(self):
        self.assertFalse(self.client.find("EmailAddress", alias="juliette"))
        self.assertFalse(self.client.find("EmailAddress", alias="romeo"))
        result = self.client.insert(
            "EmailAddress", alias="juliette", address="juliette@romance.org"
        )
        juliette_eid = result[0]
        result = self.client.insert(
            "EmailAddress", alias="romeo", address="romeo@romance.org"
        )
        romeo_eid = result[0]
        self.assertTrue(self.client.find("EmailAddress", alias="juliette"))
        self.assertTrue(self.client.find("EmailAddress", alias="romeo"))
        self.client.update_batch_by_eid(
            [
                {"eid": juliette_eid, "alias": "morte"},
                {"eid": romeo_eid, "alias": "vivant"},
            ]
        )
        self.assertTrue(
            self.client.find(
                "EmailAddress", alias="morte", address="juliette@romance.org"
            )
        )
        self.assertTrue(
            self.client.find(
                "EmailAddress", alias="vivant", address="romeo@romance.org"
            )
        )

    def test_update_by_restrictions(self):
        self.client.insert(
            "EmailAddress", alias="juliette", address="juliette@romance.org"
        )
        self.assertTrue(self.client.find("EmailAddress", alias="juliette"))
        self.client.update_by_restrictions(
            {"address": "juliette@romance.org"}, alias="morte"
        )
        self.assertTrue(
            self.client.find(
                "EmailAddress", alias="morte", address="juliette@romance.org"
            )
        )

    def test_delete(self):
        self.client.insert(
            "EmailAddress", alias="juliette", address="juliette@romance.org"
        )
        self.assertTrue(self.client.find("EmailAddress", alias="juliette"))
        self.client.delete(
            "EmailAddress", alias="juliette", address="juliette@romance.org"
        )
        self.assertFalse(self.client.find("EmailAddress", alias="juliette"))

    def test_base_url_slash_normalization(self):
        """test '/' can't appear twice in base_url

        e.g. we don't want ``http://www.logilab.org//``
        nor ``http://www.logilab.org//basepath``
        """
        proxy = self.proxy_cls(base_url="http://www.logilab.org")
        self.assertEqual(proxy.base_url, ("http", "www.logilab.org"))
        proxy = self.proxy_cls(base_url="http://www.logilab.org/")
        self.assertEqual(proxy.base_url, ("http", "www.logilab.org"))
        proxy = self.proxy_cls(base_url="http://www.logilab.org/basepath")
        self.assertEqual(proxy.base_url, ("http", "www.logilab.org/basepath"))
        proxy = self.proxy_cls(base_url="http://www.logilab.org/basepath/")
        self.assertEqual(proxy.base_url, ("http", "www.logilab.org/basepath"))

    def test_base_url_absolute_url(self):
        """test CWProxy.build_url parsing of absolute URLs"""
        proxy = self.proxy_cls(base_url="http://www.logilab.org")
        for url in (
            "http://www.logilab.org",
            "http://www.logilab.org/path/to",
            "http://www.logilab.org/path/to/",
        ):
            self.assertEqual(url, proxy.build_url(url))

        proxy = self.proxy_cls(base_url="http://www.logilab.org/with/path/")
        for url in (
            "http://www.logilab.org/with/path",
            "http://www.logilab.org/with/path/to/something",
            "http://www.logilab.org/with/path/to/something/",
        ):
            self.assertEqual(url, proxy.build_url(url))


class CWApiProxyClientTC(CWProxyClientTC):
    proxy_cls = CWApiProxy

    def test_bad_rql_path(self):
        result = self.client.rql('CWGroup U WHERE U login "admin"')
        self.assertEqual(result.status_code, 400)

    def test_rql_path(self):
        pass  # feature not provided by cube API

    def test_rql_vid(self):
        pass  # feature not provided by cube API


if __name__ == "__main__":
    from unittest import main

    main()
