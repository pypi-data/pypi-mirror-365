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
import re
import glob
import stat
import random
import subprocess
from pathlib import Path
from typing import TypedDict

from tqdm import tqdm

from zano import shared
from zano.env import _rb, _ob
from zano.shared import LOGGER
from zano.fs_nodes import Node
from zano.bundle import Bundle

GIT_REPOS = set()
ROOT_PATHS = set()

TEMPNAME = r".*__TEMPNAME__\d{1,10}$"


class StatEntry(TypedDict):
    nid: str
    st_mtime: int
    st_ctime: int
    is_file: bool


FS_Cache = dict[str, StatEntry]


def path_startswith(path, prefix):
    try:
        path = Path(path).resolve()
        prefix = Path(prefix).resolve()
        return path.is_relative_to(prefix)
    except (OSError, ValueError):
        return False


def missing_parents(path: Path) -> list[Node]:
    ancestor = Node(path.parent, mask=path.mask)
    missing = []
    while not ancestor.is_dir():
        missing.append(str(ancestor.relpath))
        ancestor = Node(ancestor.parent, mask=ancestor.mask)
    return missing[::-1]


def temporarily_renamed(f):
    """f is the file name, maybe as Path or Node"""
    s = str(f)
    if re.fullmatch(r".*__TEMPNAME__\d{1,10}$", s) is None:
        return False
    else:
        return True


def temporarily_rename(f):
    randid = str(random.randint(1, 1000000000))
    tempname = f'{f.name}__TEMPNAME__{randid}'
    return Node(f.parent / tempname, mask=f.mask)


def _check_consistency(n1, n2):
    n1_type = {n1.is_file(): 'file', n1.is_dir(): 'directory'}[True]
    n2_type = {n2.is_file(): 'file', n2.is_dir(): 'directory'}[True]
    if n1_type == n2_type:
        return True
    raise TypeError(f'Arguments should both be a file or both a directory; got'
                    f' a {n1_type} and a {n2_type} instead.')


def get_relpath(abspath, mask):
    """
    Calculates the relpath of a file/directory from its abspath and mask
    (root).
    """
    if abspath == mask:
        return '.'
    elif abspath.startswith(mask + os.sep):
        return abspath[len(mask) + 1:]
    else:
        try:
            return str(Path(abspath).relative_to(mask))
        except ValueError:
            raise ValueError(f'{abspath} is not under root {mask}')


def is_accepted(n: str, mask: str, filters: list[re.Pattern]) -> bool:
    """Return True if Node n does not match any of the filters."""
    if in_git_repo(n, mask):
        return False
    elif not os.path.exists(n):  # n is neither a file or a dir
        print(_rb(f'IGNORING {n} (neither a directory nor a file).'))
        LOGGER.warning(f'IGNORING {n} (neither a directory nor a file).')
        return False
    return not any(f.match(n) for f in filters)


def most_recent_modified(n1, n2):
    """Return '0' is mtimes of n1 are equals, or '1' or '2' """
    choice = '0'  # same mtime
    if n1.st_mtime > n2.st_mtime:
        choice = '1'
    elif n2.st_mtime > n1.st_mtime:
        choice = '2'
    return choice


def conflict(n1, n2, ts):
    """
    True if both nodes have been modified after provided timestamp.

    But if both mtimes are equal, we ignore the conflict: nodes may have been
    updated (or be both new) and it is very unlikely that two different
    modifications on two sides happened at the very same time.
    """
    if n1.st_mtime == n2.st_mtime:
        return False
    return n1.st_mtime > ts and n2.st_mtime > ts


def renamed_node(n1, n2, cache3):
    """
    Tell which node, among n1 and n2, has been renamed.

    This function is intended to be used when the nids' pairs are known.

    Return values:
    0 means n1 and n2 are not a renamed version of the other
    1 means n1 is a renamed version of n2
    2 means n2 is a renamed version of n1
    """
    _check_consistency(n1, n2)
    if temporarily_renamed(n1):
        return 2
    elif temporarily_renamed(n2):
        return 1

    renamed = (n1.name != n2.name)
    if renamed:
        info_n1 = cache3.get(str(n1.abspath), {})
        info_n2 = cache3.get(str(n2.abspath), {})
        c1 = info_n1.get('st_ctime', n1.st_ctime)
        c2 = info_n2.get('st_ctime', n2.st_ctime)
        return 1 if c1 > c2 else 2
    else:
        return 0


def moved_node(n1, n2, cache3):
    """
    Tell which node, among n1 and n2, has been moved.

    This function is intended to be used when the nids' pairs are known.

    Return values:
    0 means n1 and n2 are not a moved version of the other (same parent)
    1 means n1 is a moved version of n2
    2 means n2 is a moved version of n1
    """
    _check_consistency(n1, n2)
    moved = (n1.relparent != n2.relparent)
    if moved:
        info_n1 = cache3.get(str(n1.abspath), {})
        info_n2 = cache3.get(str(n2.abspath), {})
        c1 = info_n1.get('st_ctime', n1.st_ctime)
        c2 = info_n2.get('st_ctime', n2.st_ctime)
        return 1 if c1 > c2 else 2
    else:
        return 0


def get_git_repos(root_path, name=None):
    """
    Get the set of git repositories existing under root_path.

    :param root_path: Root path to search from
    :return: Set of relative paths for Git repositories
    """
    result = set()

    for git_dir in glob.iglob(str(Node(root_path) / '**/.git'),
                              recursive=True):
        result.add(str(Node(git_dir, mask=root_path).relparent))

    if result:
        if name is None:
            name = root_path
        msg = _ob(f'{name}: there should not be git repositories included '
                  f'in the tree structures you want to synchronize, but found '
                  f'these ones: {result}; Zano should ignore them.')
        shared.git_protection_messages.append(msg)
    return result


def protect_git_repos(b):
    """
    Find all git repositories and add their paths to GIT_REPOS.

    :param b: the Bundle containing names and root paths
    :type b: Bundle
    """
    global GIT_REPOS
    global ROOT_PATHS

    places = [(b.name1, b.root1), (b.name2, b.root2)]
    for r in b.replicas:
        places.append((r, b.replicas[r]['root']))

    for name, root_path in places:
        GIT_REPOS |= get_git_repos(root_path, name)
        ROOT_PATHS |= {str(root_path)}


def in_git_repo(n: str, root_path: str, name: str = None):
    global GIT_REPOS

    if name is None:
        name = root_path

    for repo in GIT_REPOS:
        r = str(Node(root_path) / repo)
        if (n.startswith(r)
           and (len(n) == len(r) or n[len(r)] == os.path.sep)):
            return True

    return False


def parse_stat_line(line):
    hex_mode_str, inode_str, crtime_str, mtime_str, ctime_str, path \
        = line.strip().split('\t')
    mode = int(hex_mode_str, 16)
    is_file = stat.S_ISREG(mode)

    return is_file, int(inode_str), crtime_str, mtime_str, ctime_str, path


def get_stats_bulk(directory: str) -> dict[str, dict[str, str | float]]:
    """
    Perform a bulk stat on all entries in the given directory.

    :param directory: absolute path to the directory
    :return: {abspath: {'nid': ..., 'st_mtime': ..., 'is_file': True/False}}
    """
    result = {}

    try:
        # -c '%f\t%i\t%W\t%Y\t%n' => type, inode, crtime, mtime, ctime, name
        output = subprocess.check_output(
            ['stat', '-c', '%f\t%i\t%W\t%Y\t%Z\t%n', *os.listdir(directory)],
            cwd=directory,
            stderr=subprocess.DEVNULL,
            text=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return result

    for line in output.splitlines():
        try:
            ntype, st_ino, st_crtime, st_mtime, st_ctime, name \
                = parse_stat_line(line)
            abspath = os.path.join(directory, name)
            result[abspath] = {
                'nid': f'{st_ino}:{int(st_crtime)}',
                'st_mtime': int(st_mtime),
                'st_ctime': int(st_ctime),
                'is_file': ntype
            }
        except ValueError:
            continue

    return result


def changed(n_abspath: str, n_relpath: str, twin_root: str, ts: float,
            side: str,
            cache1: dict[str, tuple[str, str]],
            cache2: dict[str, tuple[str, str]],
            cache3: FS_Cache) -> bool:
    """
    Determine whether the given node has changed since the last sync.

    :param n_abspath: the node's abspath
    :param n_relpath: the node's relative path
    :param twin_root: the root of the twin side
    :param ts: the timestamp of last synchronization
    :param side: '1' or '2'
    :param cache1: a dict {nid1: (relpath, nid2)}
    :param cache2: a dict {nid2: (relpath, nid1)}
    :param cache3: FS_Cache
    :return: True if the node is new, moved, modified, or has been deleted from
             the other side, or updated on the other side; False otherwise
    """
    cache = cache1 if side == '1' else cache2

    if n_abspath not in cache3:
        cache3.update(get_stats_bulk(os.path.dirname(n_abspath)))
    info_n = cache3.get(n_abspath)
    if info_n is None:
        return True  # just in case, because should be impossible

    try:
        stored_relpath, stored_twin_nid = cache[info_n['nid']]
    except KeyError:
        return True  # new node

    if stored_relpath != n_relpath:
        return True

    if info_n['is_file'] and info_n['st_mtime'] > ts:
        return True

    twin_abspath = os.path.join(twin_root, n_relpath)

    if twin_abspath not in cache3:
        twin_dir = os.path.dirname(twin_abspath)
        cache3.update(get_stats_bulk(twin_dir))

    twin_info = cache3.get(twin_abspath)
    if twin_info is None:
        return True  # twin doesn't exist anymore

    if twin_info['is_file'] and twin_info['st_mtime'] > ts:
        return True

    if stored_twin_nid != twin_info['nid']:
        return True

    return False


def scan_for_presync(root: Path, side: str, name: str, b: Bundle,
                     filters=None, cache3: FS_Cache = None
                     ) -> tuple[set[str], list[tuple[Node, str]], FS_Cache]:
    """
    Perform a full scan of the tree rooted at `root`, collecting:
    - all valid relative paths (for cleaning),
    - nodes needing synchronization (non-paired or changed).

    :param root: the root directory to scan
    :param side: '1' or '2'
    :param name: name of the side (for display)
    :param b: the bundle
    :param filters: list of filters to apply
    :param cache3: a shared cache of {abspath: {nid, st_mtime, ...}} updated
    across both scans
    :return: (full_scan, partial_mod_map, cache3)
    """
    if filters is None:
        filters = []
    if cache3 is None:
        cache3 = {}

    full_scan = set()
    mod_nodes = []

    cache1, cache2 = b.preload_nodes_data()

    timestamp = b.get_timestamp()
    the_other_side = '2' if side == '1' else '1'
    twin_root = getattr(b, f'root{the_other_side}')

    for dirpath, dirnames, filenames in tqdm(os.walk(root),
                                             desc=f'Scanning {name}',
                                             leave=False):
        for fname in dirnames + filenames:
            abspath = str(os.path.join(dirpath, fname))

            if in_git_repo(abspath, root, name=name):
                continue
            if not is_accepted(abspath, str(root), filters):
                continue

            n_relpath = get_relpath(abspath, str(root))
            full_scan.add(n_relpath)
            if changed(str(abspath), n_relpath, twin_root, timestamp, side,
                       cache1, cache2, cache3):
                n = Node(os.path.abspath(abspath), mask=str(root))
                mod_nodes.append((n, side))
                b.set_unprocessed(f'nid{side}', n.nid)

    return full_scan, mod_nodes, cache3


def _scan(root, action, name=None, filters=None, **action_args):
    """
    Scan all accepted nodes and collect info from each node.

    :param root: the root Node
    :type root: Node yet pathlib.Path should be OK
    :param action: the function that will collect info from the Node
    :type action: a function returning either None or data (e.g. a tuple)
    :param name: how to refer to the scanned files tree.
    :type name: str
    :param filters: the filters to apply
    :type filters: iterable (that will be converted to a list)
    :param action_args: additional parameters to be provided to action
    :type actions_args: dict
    """
    if filters is None:
        filters = []
    if name is None:
        name = root

    paths = glob.iglob(f'{root}/**', recursive=True, include_hidden=True)

    result = []
    # Then collect information excluding git repos
    for p in tqdm(paths, desc=f'Scanning {name}', leave=False):
        if Path(str(p)) != Path(str(root)):
            n = Node(os.path.abspath(p), mask=str(root))
            if (not in_git_repo(str(n), root, name=name)
               and is_accepted(str(n), str(root), filters)):
                info = action(n, **action_args)
                if info is not None:
                    result.append(info)

    return result


def scan(root, name, side_nb, filters=None):
    """
    Build a list of all relpaths under provided root.
    """
    def collect(node, side_nb):
        return str(node.relpath)

    return _scan(root, collect, name=name, filters=filters, side_nb=side_nb)


def fetch_newer_nodes(root, name, ts, filters=None):
    """
    Build a list of relpaths newer than ts, reversed sorted by reldepth.
    """
    def select(node, ts):
        if node.st_mtime > ts:
            return (Node(node.path, mask=root.mask).relpath,
                    Node(node.path, mask=root.mask).reldepth)
        else:
            return None

    result = sorted(_scan(root, select, name, filters, ts=ts),
                    reverse=True, key=lambda x: x[1])
    return [r[0] for r in result]


def rsync(source, dest, options='', filters=None):
    if filters is None:
        filters = []
    options = options.split()
    filters = [('--filter', f'- {i}') for i in filters]
    filters = [val for pair in filters for val in pair]  # flatten filters
    subprocess.run(['rsync', *options, *filters, str(source) + '/', str(dest)])
