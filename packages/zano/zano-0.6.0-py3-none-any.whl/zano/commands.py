# -*- coding: utf-8 -*-

# Zano is a bidirectional synchronization helper.
# Copyright 2021-2025 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Zano.

# Zano is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Zano is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Zano; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys

from tqdm import tqdm
from microlib import database
from microlib import terminal

from zano.env import _bb, _gb, _rb, DEFAULT_CONFIG
from zano import shared
from zano.shared import LOGGER
from zano.bundle import Bundle
from zano.tasks import backup
from zano.tasks import _presync
from zano.tasks import _pairable
from zano.tasks import _new_node
from zano.tasks import _sync_nodes
from zano.tasks import _delete_node
from zano.tasks import fetch_replicas_newer_nodes
from zano.tasks import push_changes_to_replicas
from zano.tasks import check_connection
from zano.fs_tools import protect_git_repos


def _do_pair(bundle_name):
    """Build the nids' db of two synced tree structures."""
    b = Bundle(bundle_name)

    protect_git_repos(b)

    # paired db is supposed to not exist yet
    b.init_db()

    success, b.mod_map = _pairable(b)

    if success:
        # set the timestamps
        b.create_ts_file()
        b.set_timestamp()
        for r in b.replicas:
            b.set_timestamp(r)
        LOGGER.info('Successful pairing finished!')
        print(_gb('Successful pairing finished!'))
    else:
        msg = 'Some files have been found missing on either sides. It is '\
            'possible to copy each missing file to the other side to '\
            'complete pairing. Do you want to do this?'
        if terminal.ask_yes_no(msg):
            missing = [v for v in b.mod_map.values()]
            with (database.ContextManager(b.db_path,
                                          autocommit=False) as cursor,
                  tqdm(missing, desc='Copying missing nodes...',
                       total=len(missing), leave=False) as pbar):
                b.set_db(cursor)
                for (node, side) in pbar:
                    _new_node(b, node, {}, pbar)
            LOGGER.info('Successful pairing finished!')
            print(_gb('Successful pairing finished!'))
        else:
            b.db_path.unlink()
            msg = 'OK, pairing canceled. You can try again later.'
            LOGGER.info(msg)
            print(_gb(msg))


def _do_sync(bundle_name, autocommit=DEFAULT_CONFIG['autocommit'],
             backup_before=False, backup_after=False, push=False):
    b = Bundle(bundle_name)

    protect_git_repos(b)

    # run backup before
    if backup_before:
        backup(b, 'before')

    # the paired db is assumed to exist

    try:
        with (database.ContextManager(b.db_path, integrity_check=True,
                                      autocommit=autocommit) as cursor):
            b.set_db(cursor)

            fetch_replicas_newer_nodes(b)

            b.mod_map, scan1, scan2, cache3 = _presync(b)
            length = len(b.mod_map)

            print(_bb('SYNCING'))
            LOGGER.info('SYNCING')
            shared.no_change_msg = 'No change'

            msg = 'Syncing...'

            with (tqdm(b.mod_map, total=length, desc=msg, leave=False)
                  as pbar):

                LOGGER.info('Cleaning up stale database entries...')
                b.remove_stale_nodes(scan1, scan2)

                while (b.mod_map):
                    source_node_nid = list(b.mod_map.keys())[0]
                    source_node, source_side = b.mod_map[source_node_nid]
                    dest_node_nid = b.get_twin_nid(f'nid{source_side}',
                                                   source_node.nid)
                    if dest_node_nid:
                        if dest_node_nid in b.mod_map:
                            dest_node, dest_side = b.mod_map[dest_node_nid]
                            _sync_nodes(b, source_node, dest_node, source_side,
                                        dest_side, cache3, pbar)
                        else:
                            _delete_node(b, source_node, source_side, pbar)
                    else:
                        _new_node(b, source_node, cache3, pbar)
    except RuntimeError as e:
        if str(e).startswith('Integrity check failed:'):
            LOGGER.error(f'Integrity check failed on {b.db_path}')
            print(_rb(f'The database is corrupted, so zano will not '
                      f'synchronise. You should delete it ({b.db_path}) '
                      f'and perform a first sync again to start on sane '
                      f'data.'))
            sys.exit(1)
        else:
            raise

    if shared.no_change_msg:
        print(shared.no_change_msg)
        LOGGER.info('No change')

    b.set_timestamp()

    # PUSH the changes to the connected replicas
    # (and update replicas' timestamps)
    push_changes_to_replicas(b, push)

    # run backup after
    if backup_after and terminal.ask_yes_no('Backup changes?'):
        backup(b, 'after')


def sync(bundle_name, backup_before=False, backup_after=False, push=False,
         autocommit=DEFAULT_CONFIG['autocommit']):
    b = Bundle(bundle_name)

    # check both synced sides are connected
    check_connection(b)

    # check if the paired db exists or not
    if b.db_path.exists():
        LOGGER.info(f'{bundle_name} is paired, run _do_sync()')
        _do_sync(bundle_name, backup_before=backup_before,
                 backup_after=backup_after, push=push, autocommit=autocommit)

    else:
        print(f'{b.name1} and {b.name2} have never been paired yet, so, '
              f'trying to pair them now.')
        LOGGER.info(f'{bundle_name} is not paired yet, run _do_pair()')
        _do_pair(bundle_name)
