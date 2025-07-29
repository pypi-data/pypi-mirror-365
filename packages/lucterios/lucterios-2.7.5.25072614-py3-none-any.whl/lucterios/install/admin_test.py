# -*- coding: utf-8 -*-
'''
Unit test classes to admin and migration tools

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

import unittest

from shutil import rmtree
from os import makedirs
from unittest.suite import TestSuite
from unittest.loader import TestLoader
from os.path import join, dirname, isfile, isdir
import os
from lucterios.install.lucterios_admin import LucteriosGlobal, LucteriosInstance, setup_from_none, delete_path, get_package_list
from lucterios.framework.juxd import JUXDTestRunner


class BaseTest(unittest.TestCase):

    def setUp(self):
        print('>>> %s.%s >>>' % (self.__class__.__name__, self._testMethodName))
        os.environ['LANG'] = "en_EN.UTF-8"
        self.path_dir = join(dirname(dirname(dirname(__file__))), "test")
        rmtree(self.path_dir, True)
        makedirs(self.path_dir)
        self.luct_glo = LucteriosGlobal(self.path_dir)
        self.waiting_table = ['CORE_label', 'CORE_parameter', 'CORE_preference', 'CORE_printmodel', 'CORE_savedcriteria', 'CORE_shortcut',
                              'auth_group', 'auth_group_permissions', 'auth_permission', 'auth_user', 'auth_user_groups', 'auth_user_user_permissions',
                              'django_admin_log', 'django_content_type', 'django_migrations', 'django_session',
                              'framework_lucterioslogentry']
        self.waiting_table.sort()

    def tearDown(self):
        rmtree(self.path_dir, True)
        print('<<< %s.%s <<<' % (self.__class__.__name__, self._testMethodName))


class TestGlobal(BaseTest):

    def setUp(self):
        BaseTest.setUp(self)
        os.environ['extra_url'] = "https://pypi.lucterios.org/simple/"
        delete_path(join(self.path_dir, 'extra_url'))
        self.maxDiff = 2500

    def test_package_list(self):
        pack_list = get_package_list()
        self.assertEqual(['lucterios', 'lucterios-contacts', 'lucterios-documents', 'lucterios-standard'], sorted(list(pack_list.keys())))
        self.assertEqual(4, len(pack_list['lucterios']))
        self.assertEqual('2.7.', pack_list['lucterios'][0][:4])
        self.assertEqual([], pack_list['lucterios'][1])
        self.assertEqual(1, len(pack_list['lucterios'][2]))
        self.assertEqual(3, len(pack_list['lucterios'][2][0]))
        self.assertEqual('lucterios.CORE', pack_list['lucterios'][2][0][0])
        self.assertEqual('2.7.', pack_list['lucterios'][2][0][1][:4])
        self.assertEqual([], pack_list['lucterios'][2][0][2])
        self.assertEqual(17, len(pack_list['lucterios'][3]), pack_list['lucterios'])

    def test_installed(self):
        val = self.luct_glo.installed()
        self.assertEqual(3, len(val))
        self.assertEqual(2, len(val[0]))
        self.assertEqual('lucterios', val[0][0])
        self.assertEqual('2.7.', val[0][1][:4])
        self.assertEqual(1, len(val[1]))
        self.assertEqual(3, len(val[1][0]))
        self.assertEqual('lucterios.standard', val[1][0][0])
        self.assertEqual('2.7.', val[1][0][1][:4])
        self.assertEqual(['lucterios.contacts', 'lucterios.documents', 'lucterios.mailing'], sorted(val[1][0][2]))
        self.assertEqual(3, len(val[2]))
        self.assertEqual([3, 3, 3], [len(item) for item in val[2]])
        self.assertEqual(['lucterios.contacts', 'lucterios.documents', 'lucterios.mailing'], sorted([item[0] for item in val[2]]))
        self.assertEqual(['2.7.', '2.7.', '2.7.'], [item[1][:4] for item in val[2]])
        all_libs = []
        for items in val[2]:
            all_libs.extend(items[2])
        self.assertEqual(['lucterios.contacts', 'lucterios.documents'], all_libs)

    def test_check(self):
        val = self.luct_glo.check()
        self.assertEqual(2, len(val))
        self.assertEqual(['lucterios', 'lucterios-contacts', 'lucterios-documents', 'lucterios-standard'], sorted(list(val[0].keys())))
        self.assertEqual(3, len(val[0]['lucterios']))
        self.assertEqual('2.7.', val[0]['lucterios'][0][:4])
        self.assertEqual('2.7.', val[0]['lucterios'][1][:4])
        self.assertEqual(bool, type(val[0]['lucterios'][2]))
        self.assertEqual(bool, type(val[1]))

    def test_refresh_all(self):
        self.assertEqual([], self.luct_glo.refreshall())

    def write_extraurl_file(self, values):
        with open(join(self.path_dir, 'extra_url'), mode='w') as file:
            for val in values:
                file.write(val + '\n')

    def test_check_pypi(self):
        try:
            old_http_proxy = os.environ['http_proxy']
            del os.environ['http_proxy']
        except KeyError:
            old_http_proxy = None
        try:
            self.assertEqual(
                ['--quiet', '--extra-index-url', 'https://pypi.lucterios.org/simple/'], self.luct_glo.get_default_args_([]))
            del os.environ['extra_url']
            self.assertEqual(['--quiet'], self.luct_glo.get_default_args_([]))
            self.write_extraurl_file([])
            self.assertEqual(['--quiet'], self.luct_glo.get_default_args_([]))
            self.write_extraurl_file(
                ['# pypi server list', 'https://pypi.diacamma.org/simple', 'https://pypi.supersecure.net/simple', 'http://192.168.0.206/simple', ''])
            self.assertEqual(
                ['--quiet', '--extra-index-url', 'https://pypi.diacamma.org/simple', '--extra-index-url', 'https://pypi.supersecure.net/simple',
                 '--extra-index-url', 'http://192.168.0.206/simple', '--trusted-host', '192.168.0.206'], self.luct_glo.get_default_args_([]))
            self.write_extraurl_file([])
            os.environ['http_proxy'] = 'http://myproxy.truc.com:8000'
            self.write_extraurl_file([])
            self.assertEqual(
                ['--quiet', '--proxy=http://myproxy.truc.com:8000'], self.luct_glo.get_default_args_([]))
        finally:
            if old_http_proxy is not None:
                os.environ['http_proxy'] = old_http_proxy


class TestAdminSQLite(BaseTest):

    def run_sqlite_cmd(self, instancename, cmd):
        dbpath = join(self.path_dir, instancename, "db.sqlite3")
        sqliteres = join(self.path_dir, 'out.txt')
        complete_cmd = 'sqlite3 %s "%s" > %s' % (dbpath, cmd, sqliteres)
        os.system(complete_cmd)
        with open(sqliteres, 'r') as res_file:
            for line in res_file.readlines():
                yield line.strip()

    def test_add_read(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.add()
        self.assertEqual(["inst_a"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.read()
        self.assertEqual(("sqlite", {}), inst.database)
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual((), inst.modules)

        table_list = list(self.run_sqlite_cmd(
            "inst_a", "SELECT name FROM sqlite_master WHERE type='table';"))
        if "sqlite_sequence" in table_list:
            table_list.remove("sqlite_sequence")
        table_list.sort()
        self.assertEqual(self.waiting_table, table_list)

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.clear()

        table_list = list(self.run_sqlite_cmd(
            "inst_a", "SELECT name FROM sqlite_master WHERE type='table';"))
        if "sqlite_sequence" in table_list:
            table_list.remove("sqlite_sequence")
        table_list.sort()
        self.assertEqual([], table_list)

        self.assertEqual(["inst_a"], self.luct_glo.listing())

    def test_add_modif(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_b", self.path_dir)
        inst.add()
        self.assertEqual(["inst_b"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_b", self.path_dir)
        inst.set_database("sqlite")
        inst.appli_name = "lucterios.standard"
        inst.modules = ('lucterios.dummy',)
        inst.modif()

        inst = LucteriosInstance("inst_b", self.path_dir)
        inst.read()
        self.assertEqual(("sqlite", {}), inst.database)
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual(('lucterios.dummy',), inst.modules)

        inst = LucteriosInstance("inst_b", self.path_dir)
        inst.refresh()

    def test_add_del(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_c", self.path_dir)
        inst.add()
        self.assertEqual(["inst_c"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_d", self.path_dir)
        inst.add()
        list_res = self.luct_glo.listing()
        list_res.sort()
        self.assertEqual(["inst_c", "inst_d"], list_res)

        inst = LucteriosInstance("inst_c", self.path_dir)
        inst.delete()
        self.assertEqual(["inst_d"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_d", self.path_dir)
        inst.delete()
        self.assertEqual([], self.luct_glo.listing())

    def test_extra(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_e", self.path_dir)
        inst.set_extra("DEBUG=True,ALLOWED_HOSTS=[localhost;127.0.0.1],DEFAULT_PAGE=cms/,NBMAX=5,PIVALUE=3.1415")
        inst.add()
        self.assertEqual(["inst_e"], self.luct_glo.listing())

        # print(open(self.path_dir + '/inst_a/settings.py', 'r').readlines())

        inst = LucteriosInstance("inst_e", self.path_dir)
        inst.read()
        self.assertEqual({'DEBUG': True, '': {'mode': (0, 'Connection always needed')},
                          'ALLOWED_HOSTS': ['localhost', '127.0.0.1'], 'DEFAULT_PAGE': 'cms/',
                          "NBMAX": 5, 'PIVALUE': 3.1415}, inst.extra)
        inst.modif()

        inst = LucteriosInstance("inst_e", self.path_dir)
        inst.read()

    def test_archive(self):
        self.assertEqual([], self.luct_glo.listing())
        inst = LucteriosInstance("inst_e", self.path_dir)
        inst.add()
        path_usr = join(self.path_dir, 'inst_e', 'usr', 'foo')
        makedirs(path_usr)
        with open(join(path_usr, 'myfile'), mode='w+') as myfile:
            myfile.write('boooo!!')

        inst.filename = join(self.path_dir, "inst_e.arc")
        self.assertEqual(True, inst.archive())

        import tarfile
        list_file = []
        with tarfile.open(inst.filename, "r:gz") as tar:
            for tarinfo in tar:
                list_file.append(tarinfo.name)
        list_file.sort()
        self.assertEqual(
            ['dump.json', 'target', 'usr', 'usr/foo', 'usr/foo/myfile'], list_file)

        inst = LucteriosInstance("inst_f", self.path_dir)
        inst.add()
        inst.filename = join(self.path_dir, "inst_e.arc")
        self.assertEqual(True, inst.restore())
        self.assertEqual(True, isdir(join(self.path_dir, 'inst_f', 'usr')))
        self.assertEqual(
            True, isdir(join(self.path_dir, 'inst_f', 'usr', 'foo')))
        self.assertEqual(
            True, isfile(join(self.path_dir, 'inst_f', 'usr', 'foo', 'myfile')))

    def test_security(self):
        from django.contrib.auth import authenticate
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_g", self.path_dir)
        inst.add()
        self.assertEqual(["inst_g"], self.luct_glo.listing())

        self.assertEqual(["0"], list(self.run_sqlite_cmd(
            "inst_g", "SELECT value FROM CORE_parameter WHERE name='CORE-connectmode';")))
        self.assertEqual(authenticate(username='admin', password='admin').username, 'admin')

        inst = LucteriosInstance("inst_g", self.path_dir)
        inst.set_extra("PASSWORD=abc123,MODE=2")
        inst.security()

        self.assertEqual(["Admin password change in 'inst_g'.",
                          "Security mode change in 'inst_g'."], inst.msg_list)
        self.assertEqual(["2"], list(self.run_sqlite_cmd(
            "inst_g", "SELECT value FROM CORE_parameter WHERE name='CORE-connectmode';")))
        self.assertEqual(
            authenticate(username='admin', password='admin'), None)
        self.assertEqual(
            authenticate(username='admin', password='abc123').username, 'admin')

        inst = LucteriosInstance("inst_g", self.path_dir)
        inst.set_extra("MODE=1,PASSWORD=abc,123;ABC=789,3333")
        inst.security()
        self.assertEqual(
            authenticate(username='admin', password='admin'), None)
        self.assertEqual(
            authenticate(username='admin', password='abc123'), None)
        self.assertEqual(authenticate(
            username='admin', password='abc,123;ABC=789,3333').username, 'admin')

        inst = LucteriosInstance("inst_g", self.path_dir)
        inst.set_extra("PASSWORD=ppooi=jjhg,fdd,MODE=0")
        inst.security()
        self.assertEqual(
            authenticate(username='admin', password='ppooi=jjhg,fdd').username, 'admin')


class TestAdminMySQL(BaseTest):

    mysql_options = '-pabc123'

    def setUp(self):
        BaseTest.setUp(self)
        self.data = {'dbname': 'testv2', 'username': 'myuser',
                     'passwd': '123456', 'server': 'localhost', 'options': self.mysql_options}
        for cmd in ("CREATE DATABASE %(dbname)s CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci",
                    "GRANT all ON %(dbname)s.* TO %(username)s@'%(server)s' IDENTIFIED BY '%(passwd)s'",
                    "GRANT all ON %(dbname)s.* TO %(username)s@'127.0.0.1' IDENTIFIED BY '%(passwd)s'"):
            complete_cmd = 'echo "%s;" | mysql -u root %s' % (cmd % self.data, self.mysql_options)
            os.system(complete_cmd)

    def tearDown(self):
        os.system('echo "DROP DATABASE %(dbname)s;" | mysql -u root %(options)s' % self.data)
        BaseTest.tearDown(self)

    def run_mysql_cmd(self, cmd):
        mysqlres = join(self.path_dir, 'out.txt')
        complete_cmd = 'echo "%s;" | mysql -u root %s > %s' % (cmd % self.data, self.mysql_options, mysqlres)
        os.system(complete_cmd)
        with open(mysqlres, 'r') as res_file:
            for line in res_file.readlines():
                yield line.strip()

    def test_add_read(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_mysql", self.path_dir)
        inst.set_database("mysql:name=testv2,user=myuser,password=123456,host=localhost")
        inst.add()
        self.assertEqual(["inst_mysql"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_mysql", self.path_dir)
        inst.read()
        self.assertEqual("mysql", inst.database[0])
        self.assertEqual("localhost", inst.database[1]['host'])
        self.assertEqual("testv2", inst.database[1]['name'])
        self.assertEqual("123456", inst.database[1]['password'])
        self.assertEqual("myuser", inst.database[1]['user'])
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual((), inst.modules)

        table_list = list(self.run_mysql_cmd("use testv2;show tables;"))
        if "Tables_in_testv2" in table_list:
            table_list.remove("Tables_in_testv2")
        table_list.sort()
        self.assertEqual(self.waiting_table, table_list)

        inst = LucteriosInstance("inst_mysql", self.path_dir)
        inst.clear()
        table_list = list(self.run_mysql_cmd("use testv2;show tables;"))
        self.assertEqual([], table_list)

        inst = LucteriosInstance("inst_mysql", self.path_dir)
        inst.delete()
        self.assertEqual([], self.luct_glo.listing())

    def test_archive(self):
        self.assertEqual([], self.luct_glo.listing())
        inst = LucteriosInstance("inst_g", self.path_dir)
        inst.add()
        inst.filename = join(self.path_dir, "inst_g.arc")
        self.assertEqual(True, inst.archive())

        inst = LucteriosInstance("inst_mysql", self.path_dir)
        inst.set_database("mysql:name=testv2,user=myuser,password=123456,host=localhost")
        inst.add()
        inst.filename = join(self.path_dir, "inst_g.arc")
        self.assertEqual(True, inst.restore())


class TestAdminPostGreSQL(BaseTest):

    def setUp(self):
        BaseTest.setUp(self)
        self.data = {'dbname': self._testMethodName, 'username': 'puser',
                     'passwd': '123456', 'server': 'localhost'}
        for cmd in ("DROP DATABASE %(dbname)s;", "DROP USER %(username)s;",
                    "CREATE USER %(username)s;",
                    "CREATE DATABASE %(dbname)s OWNER %(username)s;",
                    "ALTER USER %(username)s WITH ENCRYPTED PASSWORD '%(passwd)s';"):
            complete_cmd = 'sudo -u postgres psql -c "%s"' % (cmd % self.data)
            os.system(complete_cmd)

    def tearDown(self):
        from django import db
        db.close_old_connections()
        for cmd in ("DROP DATABASE %(dbname)s;", "DROP USER %(username)s;"):
            complete_cmd = 'sudo -u postgres psql -c "%s"' % (cmd % self.data)
            os.system(complete_cmd)
        BaseTest.tearDown(self)

    def run_psql_cmd(self, cmd):
        psqlres = join(self.path_dir, 'out.txt')
        complete_cmd = 'sudo -u postgres psql -d "%s" -c "%s" > %s' % (
            self.data['dbname'], cmd, psqlres)
        os.system(complete_cmd)
        with open(psqlres, 'r') as res_file:
            for line in res_file.readlines():
                yield line.strip()

    def test_add_read(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_psql", self.path_dir)
        inst.set_database(
            "postgresql:name=" + self.data['dbname'] + ",user=puser,password=123456,host=localhost")
        inst.add()
        self.assertEqual(["inst_psql"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_psql", self.path_dir)
        inst.read()
        self.assertEqual("postgresql", inst.database[0])
        self.assertEqual("localhost", inst.database[1]['host'])
        self.assertEqual(self._testMethodName, inst.database[1]['name'])
        self.assertEqual("123456", inst.database[1]['password'])
        self.assertEqual("puser", inst.database[1]['user'])
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual((), inst.modules)

        table_list = list(self.run_psql_cmd(
            "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public'"))
        table_list = table_list[2:-2]
        table_list.sort()
        self.assertEqual(self.waiting_table, table_list)

        inst = LucteriosInstance("inst_psql", self.path_dir)
        inst.clear()
        table_list = list(self.run_psql_cmd(
            "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public'"))
        table_list = table_list[2:-2]
        self.assertEqual([], table_list)

        inst = LucteriosInstance("inst_psql", self.path_dir)
        inst.delete()
        self.assertEqual([], self.luct_glo.listing())

    def test_archive(self):
        self.assertEqual([], self.luct_glo.listing())
        inst = LucteriosInstance("inst_h", self.path_dir)
        inst.add()
        inst.filename = join(self.path_dir, "inst_h.arc")
        self.assertEqual(True, inst.archive())

        inst = LucteriosInstance("inst_psql", self.path_dir)
        inst.set_database(
            "postgresql:name=" + self.data['dbname'] + ",user=puser,password=123456,host=localhost")
        inst.add()
        inst.filename = join(self.path_dir, "inst_h.arc")
        self.assertEqual(True, inst.restore())


if __name__ == "__main__":
    suite = TestSuite()
    loader = TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(TestAdminSQLite))
    # suite.addTest(loader.loadTestsFromTestCase(TestAdminMySQL))
    # suite.addTest(loader.loadTestsFromTestCase(TestAdminPostGreSQL))
    suite.addTest(loader.loadTestsFromTestCase(TestGlobal))
    JUXDTestRunner(verbosity=1).run(suite)
else:
    setup_from_none()
