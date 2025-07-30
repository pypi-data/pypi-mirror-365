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
'''C code generator for Asynchronous management protocols.
'''
# JHU/APL
# Description: Entrypoint into the camp program. Calls generators to
# create various files (i.e., C code for NASA ION) from the YANG representation
# of different ADMs for use by protocols in DTN
#
#   YYYY/MM/DD	    AUTHOR	   DESCRIPTION
#   ----------	  ------------	 ---------------------------------------------
#   2017-08-10	  David		 First implementation
#   2017-08-15	  Evana		 Clean up
#   2017-08-17	  David		 fixed mid converter
#   2017-08-23	  David		 Started convertion to command line tool
#   2017-11-01	  Sarah		 Documentation and minor fixups
#####################################################################

import argparse
import logging
import os
import sys
import tempfile
import traceback
import ace
# Import all generators
from camp.generators import (
    create_impl_h,
    create_impl_c,
    create_sql,
)

LOGGER = logging.getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    ''' Construct the argument parser. '''
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--log-level', choices=('debug', 'info', 'warning', 'error'),
                   default='info',
                   help='The minimum log severity.')
    p.add_argument('-o', '--out',
                   help="The output directory",
                   default="./")
    p.add_argument('-s', '--scrape',
                   help="Previously generated H and C file to be scraped",
                   action='store_true', default=False)
    p.add_argument('admfile',
                   help="ADM module file to use for file generation")
    p.add_argument('--only-sql',
                   help="Set this flag to only produce the SQL files",
                   action='store_true', default=False)
    p.add_argument('--only-ch',
                   help="Set this flag to only produce the .c and .h files",
                   action='store_true', default=False)
    return p


#
# Makes the output directory if it doesn't already exist
# d_name is the path to the output directory
#
def set_up_outputdir(d_name):
    if(not os.path.isdir(d_name)):
        try:
            os.makedirs(d_name)
        except OSError as e:
            LOGGER.error("[ Error ] Failed to make output directory")
            raise


#
# Main function of this tool.
#
# Calls helper functions to initialize settings, read command line arguments,
# parse the input ADM module file, and generate files\
#
def run(args: argparse.Namespace):
    try:
        only_args = [args.only_sql, args.only_ch]
        only_cnt = sum(only_args)
        if only_cnt > 1:
            raise RuntimeError("Cannot have multiple --only-* option. No files will be generated.")

        if not os.path.exists(args.admfile):
            raise RuntimeError("Passed ADM module file does not exist ({})".format(args.admfile))

        set_up_outputdir(args.out)
    except Exception as e:
        LOGGER.error("Config error: %s", e)
        return 1

    try:
        admset = ace.AdmSet()
        admset.load_default_dirs()
        # Treat the parent dir as part of the search path
        admset.load_from_dirs([os.path.dirname(args.admfile)])
        LOGGER.info("Loading %s ... ", args.admfile)
        adm = admset.load_from_file(args.admfile)
        LOGGER.info("Finished loading ADM %s", adm.norm_name)
    except Exception as e:
        LOGGER.error("Loading error: %s", e)
        return 2

    # Call each generator to generate files for the ADM module
    LOGGER.info("Generating files under %s", args.out)
    generators = []
    if not args.only_sql:
        generators += [
            create_impl_h.Writer(admset, adm, args.out, args.scrape),
            create_impl_c.Writer(admset, adm, args.out, args.scrape),
        ]

    if not args.only_ch:
        generators += [
            create_sql.Writer(admset, adm, args.out, args.scrape, dialect='pgsql')
        ]

    failures = 0
    for gen in generators:
        file_path = gen.file_path()
        dir_path, file_name = os.path.split(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # Double-buffer write into temporary file and then replace after success
        tmp = tempfile.NamedTemporaryFile(dir=dir_path, prefix=file_name, delete=False)

        try:
            LOGGER.info('Generating %s ...', os.path.relpath(file_path, args.out))
            with open(tmp.name, "w") as outfile:
                try:
                    gen.write(outfile)
                except Exception as err:
                    LOGGER.error("Failed to generate %s file: %s", file_path, err)
                    LOGGER.debug('%s', traceback.format_exc())
                    os.unlink(tmp.name)
                    failures += 1
                    continue
            os.rename(tmp.name, file_path)
            LOGGER.info('done.')
        except IOError as err:
            LOGGER.error("Failed to open %s for writing: %s", file_path, err)
            os.unlink(tmp.name)
            failures += 1
            continue

    LOGGER.debug('Resulted in %d failures out of %d files', failures, len(generators))
    return 2 if failures else 0


def main():
    ''' Script entrypoint. '''
    parser = get_parser()
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper())
    if LOGGER.isEnabledFor(logging.DEBUG):
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    return run(args)


if __name__ == '__main__':
    sys.exit(main())
