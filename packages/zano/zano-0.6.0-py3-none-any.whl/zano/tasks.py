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

import os
import copy
import shutil
from heapq import heappush, heappop

# import cProfile
# import pstats

import blessed
from tqdm import tqdm
from microlib import terminal
from microlib import database
from send2trash import send2trash

from zano.errors import MissingPathError
from zano.env import _yb, _bb, _gb, _ob  # , _rb
from zano import shared
from zano.shared import LOGGER, MAIN_LOGGER
from zano.fs_nodes import Node
from zano.bundle import Bundle
from zano.fs_tools import moved_node
from zano.fs_tools import renamed_node
from zano.fs_tools import conflict
from zano.fs_tools import most_recent_modified
from zano.fs_tools import rsync
from zano.fs_tools import scan
from zano.fs_tools import fetch_newer_nodes
from zano.fs_tools import temporarily_rename
from zano.fs_tools import scan_for_presync
from zano.fs_tools import path_startswith
from zano.fs_tools import missing_parents
import zano.fs_tools as fs_tools

PERMISSION_ERRORS_INFO = '\nPlease fix the permission issue and run '\
    'zano again.'


def check_connection(b):
    err_msg = []
    for n in ['1', '2']:
        if not b.synced[f'side{n}']['root'].is_dir():
            msg_missing_path_error = f"{b.synced[f'side{n}']['name']} "\
                f"cannot be found "\
                f"(missing path: {b.synced[f'side{n}']['root']})"
            err_msg.append(msg_missing_path_error)
            MAIN_LOGGER.error(msg_missing_path_error)
    if err_msg:
        raise MissingPathError('\n'.join(err_msg))


def _trigger_output(do_print, r):
    term = blessed.Terminal()
    if not do_print:
        msg_new_nodes_found_on = f'NEW NODES FOUND ON {r}'
        print(term.green(term.bold(msg_new_nodes_found_on)))
        LOGGER.info(msg_new_nodes_found_on)
    return True


def _copy_file(do_print, r, name, msg_label, source, dest):
    if msg_label:
        do_print = _trigger_output(do_print, r)
        print(_gb(f'{name}: {msg_label} ') + f'{dest.relpath}')
        LOGGER.info(f'{name}: {msg_label} {dest.relpath}')
    try:
        shutil.copy2(source.path, dest.path)
    except PermissionError:
        err_msg = f'insufficient permissions to copy {source.name} to {name} '\
            f'(destination: {dest.parent})' + PERMISSION_ERRORS_INFO
        terminal.echo_error(err_msg)


def fetch_replicas_newer_nodes(b):
    connected_replicas = b.connected_replicas()

    for r in connected_replicas:
        do_print = False
        replica_root = connected_replicas[r]['root']
        replica_root = Node(replica_root, mask=replica_root)
        newdocs_path = os.path.join(str(replica_root.abspath),
                                    connected_replicas[r]['newdocs_path'])
        root1 = b.synced['side1']['root']
        root2 = b.synced['side2']['root']

        for relpath in fetch_newer_nodes(replica_root, r,
                                         ts=b.get_timestamp(r),
                                         filters=b.filters):
            source = Node(replica_root / relpath, mask=replica_root)
            if not path_startswith(str(source.abspath), newdocs_path):
                msg_newdoc_out = f'{r}: WARNING: found a changed node '\
                    f'outside of the new documents directory '\
                    f'({newdocs_path}): {str(relpath)}'
                print(_ob(msg_newdoc_out))
                LOGGER.warning(msg_newdoc_out)
                shared.PUSH_TO[r] = False
                continue
            dest1 = Node(root1 / relpath, mask=root1)
            dest2 = Node(root2 / relpath, mask=root2)
            name1 = b.synced['side1']['name']
            name2 = b.synced['side2']['name']
            missing1 = missing_parents(dest1)
            if source.is_dir() and not dest1.exists():
                missing1.append(dest1)
            missing2 = missing_parents(dest2)
            if source.is_dir() and not dest2.exists():
                missing2.append(dest2)

            while missing1:
                do_print = _trigger_output(do_print, r)
                m = missing1.pop(0)
                node1 = Node(root1 / m, mask=root1)
                node2 = Node(root2 / m, mask=root2)
                if m in missing2:
                    missing2.remove(m)
                    print(_gb('NEW ON BOTH SIDES: ') + f'{m}')
                    LOGGER.info(f'NEW ON BOTH SIDES: {m}')
                    node2.mkdir(parents=True, exist_ok=True)
                else:
                    print(_gb(f'{name1}: NEW ') + f'{m}')
                    LOGGER.info(f'{name1}: NEW {m}')
                node1.mkdir(parents=True, exist_ok=True)
                _pair_nodes(b, node1, node2, '1', '2', None)

            while missing2:  # only from missing2 remaining
                do_print = _trigger_output(do_print, r)
                m = missing2.pop(0)
                node1 = Node(root1 / m, mask=root1)
                node2 = Node(root2 / m, mask=root2)
                print(_gb(f'{name2}: NEW ') + f'{m}')
                LOGGER.info(f'{name2}: NEW {m}')
                node2.mkdir(parents=True, exist_ok=True)
                _pair_nodes(b, node1, node2, '1', '2', None)

            if source.is_file():
                if not dest1.exists() and not dest2.exists():
                    do_print = _trigger_output(do_print, r)
                    print(_gb('NEW ON BOTH SIDES: ') + f'{relpath}')
                    LOGGER.info(f'NEW ON BOTH SIDES: {relpath}')
                    _copy_file(do_print, r, name1, '', source, dest1)
                    _copy_file(do_print, r, name2, '', source, dest2)
                else:
                    for i, dest in enumerate([dest1, dest2]):
                        name = b.synced[f'side{i + 1}']['name']
                        do_copy = False
                        if dest.exists():
                            if most_recent_modified(source, dest) == '1':
                                msg_label = 'UPDATE'
                                do_copy = True
                        else:
                            msg_label = 'NEW'
                            do_copy = True
                        if do_copy:
                            _copy_file(do_print, r, name, msg_label,
                                       source, dest)
                _pair_nodes(b, dest1, dest2, '1', '2', None)


def backup(b, when):
    """
    rsync data to both synced backups. Assumes the backup paths are defined.
    """
    print(_bb('BACKING UP EACH SYNCED SIDE'))
    LOGGER.info('BACKING UP EACH SYNCED SIDE')
    err_msg = []
    for s in ['side1', 'side2']:
        if b.synced[s]['backup'] is None:
            err_msg.append(f"--backup-{when} option requires "
                           f"[synced.{s}] to define a backup path "
                           "(backup = /path/to/backup)")
        elif not b.synced[s]['backup'].is_dir():
            n = b.synced[s]['name']
            bp = b.synced[s]['backup']
            err_msg.append(f"Cannot find backup directory for {n}: {bp}")
    if err_msg:
        raise MissingPathError('\n'.join(err_msg))
    for s in ['side1', 'side2']:
        source = b.synced[s]['root']
        dest = b.synced[s]['backup']
        options = '-avzz --progress --delete --delete-excluded '\
            '--delete-before --ignore-errors --force'
        rsync(source, dest, options)
    print('Backup done.')
    LOGGER.info('Backup done.')


def push_changes_to_replicas(b, push):
    connected_replicas = b.connected_replicas()
    for r in connected_replicas:
        if not shared.PUSH_TO.get(r, True):
            newdocs_dir = connected_replicas[r]['newdocs_path']
            print(_ob(f'Changes have been noticed on {r}, outside of '
                      f'{newdocs_dir}, these changes will be discarded if '
                      f'the changes on synced sides are pushed to {r}, so '
                      f'please confirm:'))
        push = push and shared.PUSH_TO.get(r, True)
        if push or terminal.ask_yes_no(f'Push changes to {r}?'):
            filters = connected_replicas[r]['filters']
            source = b.synced['side1']['root']
            dest = connected_replicas[r]['root']
            options = '-rtv --delete --delete-excluded --force '\
                '--modify-window=2'
            rsync(source, dest, options, filters)
            b.set_timestamp(replica=r)


def _presync(b: Bundle) -> tuple[dict[str,
                                      tuple[Node, str]],
                                 list[str],
                                 list[str],
                                 dict[str, dict[str, str | float]]]:
    """
    Perform a full scan of both trees and collect:
    - a mod_map with only non-paired or changed nodes,
    - the full scans of both trees, for later cleanup.

    :param b: the bundle
    :return: (mod_map, scan1, scan2)
    """
    mod_map = {}
    heap = []
    print(_bb('SCANNING'))
    LOGGER.info('SCANNING')

    if shared.git_protection_messages:
        msg_git_warning_presync = '\n'.join(shared.git_protection_messages)
        print(msg_git_warning_presync)
        LOGGER.warning(msg_git_warning_presync)

    cache3 = {}

    # Scan both sides
    # profiler = cProfile.Profile()
    # profiler.enable()
    scan1, map1, cache3 = scan_for_presync(b.root1, '1', b.name1, b,
                                           filters=b.filters, cache3=cache3)
    scan2, map2, cache3 = scan_for_presync(b.root2, '2', b.name2, b,
                                           filters=b.filters, cache3=cache3)
    # profiler.disable()
    # # cumtime = cumulated time
    # stats = pstats.Stats(profiler).sort_stats('cumtime')
    # stats.print_stats(30)  # top 30 most time consuming functions

    print('Scanning done.')
    LOGGER.info('Scanning done.')

    msg = 'Sorting data...'
    LOGGER.info('Sorting data...')

    # Merge both maps into a single mod_map
    combined = map1 + map2
    # Sort by descending depth
    for n in tqdm(combined, desc=msg, total=len(combined), leave=False):
        heappush(heap, (-n[0].reldepth, n))

    LOGGER.info('Processing data...')
    with tqdm(desc='Processing data...', total=len(heap), leave=False) as pbar:
        while heap:
            _, (node, side) = heappop(heap)
            mod_map[node.nid] = (node, side)
            pbar.update(1)

    return mod_map, scan1, scan2, cache3


def _pairable(b):
    """
    Try to pair the two tree structures.

    :param b: the bundle
    :type b: Bundle
    """
    success = True
    b.create_ts_file()
    b.set_timestamp()
    for r in b.replicas:
        b.set_timestamp(r)

    print(_bb('SCANNING'))
    LOGGER.info('SCANNING')
    if shared.git_protection_messages:
        msg_git_warning_pairable = '\n'.join(shared.git_protection_messages)
        print(msg_git_warning_pairable)
        LOGGER.warning(msg_git_warning_pairable)
    # collect nodes from each side...
    rpaths_list1 = scan(b.root1, b.name1, '1', filters=b.filters)
    rpaths_list2 = scan(b.root2, b.name2, '2', filters=b.filters)
    print('Scanning done.')
    LOGGER.info('Scanning done.')

    print(_bb('PAIRING'))
    LOGGER.info('PAIRING')
    msg = f'Processing nodes from {b.name1}...'
    LOGGER.info(f'Processing nodes from {b.name1}...')

    mod_map = {}

    with (database.ContextManager(b.db_path) as cursor,
          tqdm(rpaths_list1, desc=msg, total=len(rpaths_list1), leave=False)
          as pbar):
        b.set_db(cursor)
        for rpath1 in pbar:
            node1 = Node(b.root1 / rpath1, mask=b.root1)
            if rpath1 in rpaths_list2:
                node2 = Node(b.root2 / rpath1, mask=b.root2)
                _update_nodes(b, node1, node2, pbar)
                b.upsert_pair(node1.nid, node2.nid,
                              str(node1.relpath), str(node2.relpath))
                rpaths_list2.remove(rpath1)
            else:
                mod_map[node1.nid] = (node1, '1')
                success = False
                msg_missing_path_pairable = \
                    f'{b.name1}: {rpath1} does not exist in {b.name2}'
                pbar.write(_yb(msg_missing_path_pairable))
                LOGGER.info(msg_missing_path_pairable)

    if rpaths_list2:
        msg_remaining_nodes = f'Processing remaining nodes from {b.name2}...'
        LOGGER.info(msg_remaining_nodes)
        success = False
        pbar = tqdm(rpaths_list2, desc=msg_remaining_nodes,
                    total=len(rpaths_list2), leave=False)
        for rpath2 in pbar:
            node2 = Node(b.root2 / rpath2, mask=b.root2)
            mod_map[node2.nid] = (node2, '2')
            pbar.write(_yb(f'{b.name2}: {rpath2} does not exist in {b.name1}'))
            LOGGER.info(f'{b.name2}: {rpath2} does not exist in {b.name1}')

    print('Done.')
    LOGGER.info('Done.')

    return success, mod_map


def _update_node_children(b, dest_node, side):
    """
    Update the paths of dest_node and its children in the db and mod_map.

    This update happens after the root node has been moved/renamed.

    :param b: the bundle to get informations from
    :type b: Bundle
    :param dest_node: the node AFTER it has been moved/renamed
    :type dest_node: Node
    :param side: the side of the moved/renamed node ('1' or '2')
    :type side: str
    """
    sideroot = str(getattr(b, f'root{side}'))
    if dest_node.nid in b.mod_map:
        b.mod_map[dest_node.nid] = (Node(dest_node, mask=sideroot), side)
    b.update_nid_relpath(f'nid{side}', dest_node.nid, str(dest_node.relpath))
    if dest_node.is_dir():
        children = scan(dest_node, dest_node.relpath, side, filters=b.filters)
        for child in children:
            # child is a path relative to dest_node.path
            n = Node(os.path.join(dest_node.path, child), mask=sideroot)
            nid = n.nid
            if nid in b.mod_map:
                b.mod_map[nid] = (n, side)
            b.update_nid_relpath(f'nid{side}', nid, str(n.relpath))


def _delete_node(b, node, side, pbar):
    """
    Delete the provided node from the file system.
    Remove it from the provided dict.

    :param b: the bundle to get informations from
    :type b: Bundle
    :param node: the node to delete
    :type node: Node
    :param side: the side of the to-be-deleted node ('1' or '2')
    :type side: str
    :param pbar: the progress bar
    :type pbar: tqdm.tqdm
    """
    nid = node.nid
    del b.mod_map[nid]
    abspath = str(getattr(b, f'root{side}') / node.relpath)
    sidename = getattr(b, f'name{side}')
    pbar.write(_ob(f'{sidename}: DELETE ') + f'{node.relpath}')
    LOGGER.info(f'{sidename}: DELETE {node.relpath}')
    shared.no_change_msg = ''
    try:
        send2trash(abspath)
    except PermissionError:
        delete_permission_error_log = f'insufficient permissions to move '\
            f'{abspath} to trash{PERMISSION_ERRORS_INFO}'
        LOGGER.error(delete_permission_error_log)
        terminal.echo_error(delete_permission_error_log)
    b.remove_nid(f'nid{side}', nid)


def _update_nodes(b, node1, node2, pbar):
    if node1.is_file() and node2.is_file():
        choice = most_recent_modified(node1, node2)
        if conflict(node1, node2, b.get_timestamp()):
            if choice in ['1', '2']:
                name = b.synced[f'side{choice}']['name']
                most_recent = f' (most recently modified on {name})'

                def check_answer(s):
                    return s in {b.name1, b.name2}

                if pbar:
                    with pbar.external_write_mode():
                        question_both_mod = f'{node1.relpath} has been '\
                            f'modified on both sides{most_recent}. Do you '\
                            f'want to keep the version of {b.name1} or '\
                            f'{b.name2}?'
                        LOGGER.info(question_both_mod)
                        choice = terminal.ask_user(question_both_mod,
                                                   allowed=check_answer)
                        choice = {b.name1: '1', b.name2: '2'}[choice]
                        LOGGER.info(f'User answer: {choice = }')
                        shared.no_change_msg = ''

        if choice == '1':
            name = b.name2
            relpath = node2.relpath
            path1 = node1.path
            path2 = node2.path
        elif choice == '2':
            name = b.name1
            relpath = node1.relpath
            path1 = node2.path
            path2 = node1.path

        if choice != '0':
            if pbar:
                pbar.write(_yb(f'{name}: UPDATE ') + f'{relpath}')
            LOGGER.info(f'{name}: UPDATE {relpath}')
            try:
                shutil.copy2(path1, path2)
                shared.no_change_msg = ''
            except PermissionError:
                update_permission_warning_log = f'insufficient permissions '\
                    f'to update {relpath} on {name}.'
                LOGGER.warning(update_permission_warning_log)
                terminal.echo_warning(update_permission_warning_log)


def _pair_nodes(b, node1, node2, side1, side2, pbar):
    """
    Pair the two existing provided nodes.

    :param b: the bundle to get informations from (e.g. the databases)
    :type b: Bundle
    :param node1: one of the to be paired nodes
    :type node1: Node
    :param node2: the other node
    :type node2: Node
    :param side1: the side of node1 ('1' or '2')
    :type side1: str
    :param side2: the side of node2 ('1' or '2')
    :type side2: str
    :param pbar: the progress bar
    :type pbar: tqdm.tqdm

    """
    nid1 = node1.nid
    nid2 = node2.nid
    if side1 == '2' and side2 == '1':
        node1, node2 = node2, node1
        side1, side2 = side2, side1

    _update_nodes(b, node1, node2, pbar)
    b.upsert_pair(node1.nid, node2.nid, str(node1.relpath), str(node2.relpath))
    # if nothing changed, status must be manually
    # updated from 'unprocessed' to 'paired'
    if node1.relpath == node2.relpath:
        b.set_paired('nid1', node1.nid)
    if nid1 in b.mod_map:
        del b.mod_map[nid1]
    if nid2 in b.mod_map:
        del b.mod_map[nid2]
    if pbar:
        pbar.update(2)


def _move_alike(b, n1, n2, side, cache3, pbar):
    # move n2 to the same parent as n1
    source_side = {'1': '2', '2': '1'}[side]
    dest = Node(n1.parent / n2.name, mask=n1.mask)
    dest_path = _hook_up(b, dest, Node(n2.mask), source_side, side, pbar)
    dest2 = Node(dest_path / n2.name, mask=n2.mask)
    sidename = getattr(b, f'name{side}')
    if str(n2.abspath) not in cache3:
        cache3.update(fs_tools.get_stats_bulk(str(n2.parent.abspath)))
    cache3.update({str(dest2.abspath): cache3[str(n2.abspath)]})
    # it may happen that useless moves are detected; just do not do them
    if n2.relpath != dest2.relpath:
        if dest2.exists():
            dest2_renamed = Node(dest2, mask=n2.mask)
            dest2_renamed_nid = dest2_renamed.nid
            while dest2_renamed.exists():
                dest2_renamed = temporarily_rename(dest2)
            msg = _yb(f'{sidename}: RENAME ') + f'{dest2.relpath} ' \
                + _yb('AS') + f' {dest2_renamed.relpath}'
            pbar.write(msg)
            LOGGER.info(f'{sidename}: RENAME {dest2.relpath} '
                        f'AS {dest2_renamed.relpath}')
            try:
                shutil.move(str(dest2.path), str(dest2_renamed))
            except PermissionError:
                rename_insufficient_permissions_msg = f'insufficient '\
                    f'permissions to rename {str(dest2.path)} '\
                    f'as {str(dest2_renamed)} on {sidename}' \
                    + PERMISSION_ERRORS_INFO
                LOGGER.error(rename_insufficient_permissions_msg)
                terminal.echo_error(rename_insufficient_permissions_msg)
            b.mod_map[dest2_renamed_nid] = (Node(dest2_renamed,
                                                 mask=n2.mask), side)
        msg = _yb(f'{sidename}: MOVE ') + f'{n2.relpath} ' \
            + _yb('TO') + f' {dest2.relpath}'
        pbar.write(msg)
        LOGGER.info(f'{sidename}: MOVE {n2.relpath} TO {dest2.relpath}')
        shared.no_change_msg = ''
        try:
            shutil.move(str(n2.path), str(dest2.path))
        except PermissionError:
            move_insufficient_permissions_msg = f'insufficient permissions '\
                f'to move {str(n2.relpath)} to '\
                f'{str(dest2.relpath)} on {sidename}' + PERMISSION_ERRORS_INFO
            LOGGER.error(move_insufficient_permissions_msg)
            terminal.echo_error(move_insufficient_permissions_msg)
        dest2 = Node(dest2, mask=n2.mask)
    dest2 = Node(dest2, mask=n2.mask)
    _update_node_children(b, dest2, side)
    return dest2


def _do_rename(b, node1, node2, side, cache3, pbar):
    sidename = getattr(b, f'name{side}')
    old = str(node2.path)
    new = str(node2.parent / node1.name)
    old_rel = str(node2.relpath)
    new_rel = str(node2.relparent / node1.name)
    if old not in cache3:
        cache3.update(fs_tools.get_stats_bulk(str(Node(old).parent)))
    cache3.update({new: cache3[old]})
    msg = _yb(f'{sidename}: RENAME ') + f'{old_rel} ' + _yb('AS') \
        + f' {new_rel}'
    pbar.write(msg)
    LOGGER.info(f'{sidename}: RENAME {old_rel} AS {new_rel}')
    shared.no_change_msg = ''
    try:
        shutil.move(old, new)
    except PermissionError:
        rename_insufficient_permissions_msg2 = f'insufficient permissions '\
            f'to rename {old} as {new} on {sidename}' + PERMISSION_ERRORS_INFO
        LOGGER.error(rename_insufficient_permissions_msg2)
        terminal.echo_error(rename_insufficient_permissions_msg2)
    node = Node(node2.parent / node1.name, mask=node2.mask)
    _update_node_children(b, node, side)
    return node


def _hook_up(b, source_node, dest_root, source_side, dest_side, pbar):
    """
    Hook up source_node to the closest existing parent on dest_root.

    All missing parents will be created.

    To be used anytime a node from one side must be copied to the other side
    (e.g. _sync_nodes() and _new_node()).
    """
    dest_name = getattr(b, f'name{dest_side}')
    common_path = copy.deepcopy(source_node)
    missing = []
    common_path = Node(common_path.parent, mask=source_node.mask)
    dest_relpath = None
    while b.get_current_paired_relpath(f'nid{source_side}',
                                       common_path.nid) is None:
        if (str(common_path) == source_node.mask or common_path.reldepth == 0):
            # We've reached this side's root
            dest_relpath = ''
            break
        missing.append(common_path.name)
        common_path = common_path.parent

    if dest_relpath != '':
        # now, dest_nid does exist
        dest_relpath = b.get_current_paired_relpath(
            f'nid{source_side}', common_path.nid)

    # case of dest_path being None? (the matching parent has been deleted
    # OR is the root, which is not in the db)

    dest_path = Node(dest_root / dest_relpath, mask=str(dest_root))
    source_path = Node(common_path, mask=source_node.mask)
    for folder in reversed(missing):
        dest_path = Node(dest_path / folder, mask=dest_path.mask)
        source_path = Node(source_path / folder, mask=source_node.mask)
        while dest_path.exists():
            dest_path = temporarily_rename(dest_path)
        pbar.write(_gb(f'{dest_name}: NEW ') + f'{dest_path.relpath}')
        LOGGER.info(f'{dest_name}: NEW {dest_path.relpath}')
        shared.no_change_msg = ''
        dest_path.mkdir()
        b.mod_map[dest_path.nid] = (dest_path, dest_side)
        # remove source_path.nid from paired db, if it is here,
        # it may have been deleted
        paired_dest_nid = b.get_twin_nid(f'nid{source_side}', source_path.nid)
        if paired_dest_nid:
            existing_dest_relpath = b.get_relpath_matching_current(
                f'nid{dest_side}', paired_dest_nid)
            if existing_dest_relpath is None:
                b.remove_nid(f'nid{dest_side}', paired_dest_nid)
        nid1 = source_path.nid
        nid2 = dest_path.nid
        relpath1 = str(source_path.relpath)
        if source_side == '2':
            nid1, nid2 = nid2, nid1
            relpath1 = str(dest_path.relpath)
        b.upsert_pair(nid1, nid2, relpath1, relpath1)
    return dest_path


def _sync_nodes(b, node1, node2, side1, side2, cache3, pbar):
    """
    Synchronize two existing nodes. Hence, move and or rename each one, as
    necessary; update one if necessary; finally pair them.

    :param b: the bundle to get informations from (e.g. the databases)
    :type b: Bundle
    :param node1: one of the to be paired nodes
    :type node1: Node
    :param node2: the other node
    :type node2: Node
    :param side1: the side of node1 ('1' or '2')
    :type side1: str
    :param side2: the side of node2 ('1' or '2')
    :type side2: str
    :param pbar: the progress bar
    :type pbar: tqdm.tqdm
    """
    moved = moved_node(node1, node2, cache3)
    if moved == 1:
        node2 = _move_alike(b, node1, node2, side2, cache3, pbar)
    elif moved == 2:
        node1 = _move_alike(b, node2, node1, side1, cache3, pbar)

    renamed = renamed_node(node1, node2, cache3)
    if renamed == 1:
        node2 = _do_rename(b, node1, node2, side2, cache3, pbar)
    elif renamed == 2:
        node1 = _do_rename(b, node2, node1, side1, cache3, pbar)

    _pair_nodes(b, node1, node2, side1, side2, pbar)


def _new_node(b, node, cache3, pbar):
    """
    Duplicate the provided node, that is new and supposed to not yet exist
    on the other side.

    :param b: the bundle to get informations from
    :type b: Bundle
    :param node: the new node to duplicate
    :type node: Node
    :param pbar: the progress bar
    :type pbar: tqdm.tqdm
    """
    source_side = b.mod_map[node.nid][1]
    dest_side = {'1': '2', '2': '1'}[source_side]
    dest_mask = getattr(b, f'root{dest_side}')
    dest_path = _hook_up(b, node, Node(dest_mask), source_side, dest_side,
                         pbar)
    dest_node = Node(dest_path / node.name, mask=dest_mask)
    dest_name = getattr(b, f'name{dest_side}')
    if not dest_node.path.exists():
        pbar.write(_gb(f'{dest_name}: NEW ') + f'{dest_node.relpath}')
        LOGGER.info(f'{dest_name}: NEW {dest_node.relpath}')
        if node.is_dir():
            copy_fct = shutil.copytree
        else:
            copy_fct = shutil.copy2
        try:
            copy_fct(node.path, dest_node.path)
        except PermissionError:
            copy_insufficient_permissions_msg = f'insufficient permissions '\
                f'to create {dest_node.path}' + PERMISSION_ERRORS_INFO
            LOGGER.error(copy_insufficient_permissions_msg)
            terminal.echo_error(copy_insufficient_permissions_msg)
        shared.no_change_msg = ''
    else:
        if str(dest_node.path) in cache3:
            dest_nid = cache3[str(dest_node.path)]['nid']
            dest_twin_nid = b.get_twin_nid(f'nid{dest_side}', dest_nid)
            if not dest_twin_nid:
                pbar.write(_gb('NEW ON BOTH SIDES: ') + f'{dest_node.relpath}')
                LOGGER.info(f'NEW ON BOTH SIDES: {dest_node.relpath}')
    _pair_nodes(b, node, dest_node, source_side, dest_side, pbar)
