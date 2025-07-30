#
# Copyright (c) 2020-2025 The Johns Hopkins University Applied Physics
# Laboratory LLC.
#
# This file is part of the C code generator for AMP (CAMP) under the
# DTN Management Architecture (DTNMA) reference implementaton set from APL.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Portions of this work were performed for the Jet Propulsion Laboratory,
# California Institute of Technology, sponsored by the United States Government
# under the prime contract 80NM0018D0004 between the Caltech and NASA under
# subcontract 1658085.
#
''' Verify behavior of the "camp" command tool.
'''
import argparse
import datetime
import io
import logging
import os
import sys
import unittest
import jinja2
from ace import AdmSet, Checker
from camp.generators.lib.campch_roundtrip import H_Scraper, C_Scraper
from camp.generators import (
    create_sql,
    create_impl_h,
    create_impl_c,
)
from .util import TmpDir

LOGGER = logging.getLogger(__name__)
''' Logger for this module '''
SELFDIR = os.path.dirname(__file__)
''' Directory containing this file '''


class BaseTest(unittest.TestCase):
    ''' Abstract base for generators
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tmpl_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.join(SELFDIR, 'data')),
            keep_trailing_newline=True
        )

    def setUp(self):
        self.maxDiff = None
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        self._dir = TmpDir()
        LOGGER.info('Working in %s', self._dir)
        self._admset = AdmSet()

    def tearDown(self):
        del self._dir

    def _get_adm(self, file_name):
        ''' Read an ADM file from the 'tests/data' directory.
        '''
        admfile = os.path.join(SELFDIR, 'data', file_name)
        LOGGER.info("Loading %s ... ", admfile)
        adm = self._admset.load_from_file(admfile)
        errs = Checker(self._admset.db_session()).check(adm)
        self.assertEqual([], errs)
        return adm

    def _today_datestamp(self):
        ''' Get a datestamp for files created today.
        '''
        return datetime.date.today().strftime('%Y-%m-%d')


class TestCreateSql(BaseTest):

    @unittest.expectedFailure
    def test_create_sql(self):
        adm = self._get_adm('example-test.yang')
        outdir = os.path.join(os.environ['XDG_DATA_HOME'], 'out')

        writer = create_sql.Writer(self._admset, adm, outdir, dialect='pgsql')
        self.assertEqual(
            os.path.join(outdir, 'amp-sql', 'Agent_Scripts', 'adm_test_adm.sql'),
            writer.file_path()
        )

        buf = io.StringIO()
        writer.write(buf)

        tmpl = self._tmpl_env.get_template('test_adm.pgsql.sql.jinja')
        content = tmpl.render(datestamp=self._today_datestamp())
        self.assertEqual(content, buf.getvalue())


class TestCreateCH(BaseTest):

    def test_create_impl_h_noscrape(self):
        adm = self._get_adm('example-test.yang')
        outdir = os.path.join(os.environ['XDG_DATA_HOME'], 'out')
        LOGGER.info('Writing to %s', outdir)

        writer = create_impl_h.Writer(self._admset, adm, outdir, H_Scraper(None))
        self.assertEqual(
            os.path.join(outdir, 'example_test.h'),
            writer.file_path()
        )

        buf = io.StringIO()
        writer.write(buf)

        tmpl = self._tmpl_env.get_template('gen_ch/example_test.h.jinja')
        content = tmpl.render(datestamp=self._today_datestamp())
        self.assertEqual(content, buf.getvalue())

    def test_create_impl_c_noscrape(self):
        adm = self._get_adm('example-test.yang')
        outdir = os.path.join(os.environ['XDG_DATA_HOME'], 'out')

        writer = create_impl_c.Writer(self._admset, adm, outdir, C_Scraper(None))
        self.assertEqual(
            os.path.join(outdir, 'example_test.c'),
            writer.file_path()
        )

        buf = io.StringIO()
        writer.write(buf)

        tmpl = self._tmpl_env.get_template('gen_ch/example_test.c.jinja')
        content = tmpl.render(datestamp=self._today_datestamp())
        self.assertEqual(content, buf.getvalue())
