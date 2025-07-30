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
import errno
import fnmatch
from time import time
from pathlib import Path
from copy import deepcopy

import toml
from microlib import database, terminal

from .env import ZANO_LOCAL_SHARE, ZANO_CONFIG_DIR, _ob
from zano import shared
from zano.shared import LOGGER
from .errors import ConfigFileError
from .errors import NoSuchBundleError


SCHEMA_SQL = """
-- Table for unique relative paths
CREATE TABLE IF NOT EXISTS paths (
    path_id   INTEGER PRIMARY KEY,
    relpath   TEXT    NOT NULL UNIQUE
);

-- Table for paired nodes
CREATE TABLE IF NOT EXISTS nodes (
    node_id   INTEGER PRIMARY KEY,
    nid1      TEXT    NOT NULL,
    nid2      TEXT    NOT NULL,
    path1_id  INTEGER NOT NULL REFERENCES paths(path_id) ON DELETE CASCADE,
    path2_id  INTEGER NOT NULL REFERENCES paths(path_id) ON DELETE CASCADE,
    status    TEXT    NOT NULL
                CHECK(status IN ('unprocessed','paired','pending')),
    UNIQUE(nid1, nid2)
);

-- Index to speed up status lookups
CREATE INDEX IF NOT EXISTS idx_nodes_status ON nodes(status);
-- Indexes to speed up lookups by NID
CREATE INDEX IF NOT EXISTS idx_nodes_nid1   ON nodes(nid1);
CREATE INDEX IF NOT EXISTS idx_nodes_nid2   ON nodes(nid2);

-- Trigger: clean up orphan paths after deleting a node
CREATE TRIGGER IF NOT EXISTS cleanup_orphan_paths_after_delete
AFTER DELETE ON nodes
BEGIN
    DELETE FROM paths
     WHERE path_id NOT IN (
         SELECT path1_id FROM nodes
         UNION
         SELECT path2_id FROM nodes
     );
END;

-- Trigger: clean up orphan paths after updating node paths
CREATE TRIGGER IF NOT EXISTS cleanup_orphan_paths_after_update
AFTER UPDATE OF path1_id, path2_id ON nodes
BEGIN
    DELETE FROM paths
     WHERE path_id NOT IN (
         SELECT path1_id FROM nodes
         UNION
         SELECT path2_id FROM nodes
     );
END;

-- Trigger: enforce correct status on INSERT
CREATE TRIGGER IF NOT EXISTS enforce_status_after_insert
AFTER INSERT ON nodes
BEGIN
    UPDATE nodes
    SET status =
        CASE
            WHEN path1_id = path2_id THEN 'paired'
            ELSE 'pending'
        END
    WHERE node_id = NEW.node_id;
END;

-- Trigger: enforce correct status on UPDATE of paths
CREATE TRIGGER IF NOT EXISTS enforce_status_after_path_change
AFTER UPDATE OF path1_id, path2_id ON nodes
BEGIN
    UPDATE nodes
    SET status =
        CASE
            WHEN path1_id = path2_id THEN 'paired'
            ELSE 'pending'
        END
    WHERE node_id = NEW.node_id;
END;

-- View for convenient inspection of node pairs with readable paths
CREATE VIEW IF NOT EXISTS nodes_view AS
SELECT
    n.node_id,
    n.nid1,
    n.nid2,
    p1.relpath AS relpath1,
    p2.relpath AS relpath2,
    n.status
FROM nodes n
JOIN paths p1 ON n.path1_id = p1.path_id
JOIN paths p2 ON n.path2_id = p2.path_id;

PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
"""


def compile_filters(filters: list[str]) -> list[re.Pattern]:
    return [re.compile(fnmatch.translate(f)) for f in filters]


def _check_config(config, path):
    keys = set(config)
    if 'synced' not in keys:
        raise ConfigFileError(f'Missing [synced] table in config file located '
                              f'at: {path}')
    keys.remove('synced')
    if 'replicas' in keys:
        keys.remove('replicas')
    if keys:
        raise ConfigFileError(f'Extraneous entries: '
                              f'{", ".join([k for k in keys])}, '
                              f'in config file located at: {path}')
    cfg = deepcopy(config)
    cfg['synced'].pop('filters', None)
    if len(cfg['synced']) != 2:
        raise ConfigFileError(f'The [synced] table must define exactly two '
                              f'sides in config file located at: {path}')
    for side in ['side1', 'side2']:
        if side not in cfg['synced']:
            raise ConfigFileError(f'Missing "{side}" in [synced] table in '
                                  f'config file located at: {path}')
        for entry in ['name', 'root']:
            if entry not in cfg['synced'][side]:
                raise ConfigFileError(f'Missing "{entry}" in [synced.{side}] '
                                      f'table in config file located at: '
                                      f'{path}')
        for entry in cfg['synced'][side]:
            if entry not in ['name', 'root', 'backup']:
                raise ConfigFileError(f'Unexpected entry "{entry}" in '
                                      f'[synced.{side}] table in config file '
                                      f'located at: {path}')
    if 'replicas' not in cfg:
        cfg['replicas'] = []
    for r in cfg['replicas']:
        if 'root' not in cfg['replicas'][r].keys():
            raise ConfigFileError(f'Missing \'root\' in replica "{r}" '
                                  f'in config file located at: {path}')


class Bundle(object):

    def __init__(self, name):
        """Record bundle's synced and replicas."""
        local_share_path = Path(ZANO_LOCAL_SHARE) / name
        cfg_path = Path(ZANO_CONFIG_DIR) / f'{name}.toml'
        try:
            with open(cfg_path) as f:
                config = toml.load(f)
        except FileNotFoundError:
            raise NoSuchBundleError(f'Found no bundle named {name} configured '
                                    f'in {ZANO_CONFIG_DIR}.')
        self._db = None
        _check_config(config, cfg_path)
        synced = config['synced']
        self._filters = config['synced'].pop('filters', [])
        self._synced = {}
        for i, s in enumerate(synced):
            backup = synced[s].get('backup', None)
            if backup is not None:
                backup = Path(str(backup))
            self._synced[s] = {'name': str(synced[s]['name']),
                               'root': Path(str(synced[s]['root'])),
                               'backup': backup}
            setattr(self, f'_root{i + 1}', self._synced[s]['root'])
            setattr(self, f'_name{i + 1}', self._synced[s]['name'])

        self._replicas = {}
        if 'replicas' not in config:
            config['replicas'] = []
        for r in config['replicas']:
            rdata = config['replicas'][r]
            self._replicas[r] = {'root': Path(str(rdata['root'])),
                                 'filters': rdata.get('filters', []),
                                 'newdocs_path': rdata.get('newdocs_path',
                                                           'NEW_DOCS')}
        self._paths = {'config': cfg_path,
                       'ts': local_share_path / 'ts.toml',
                       'db': local_share_path / 'paired.sqlite3',
                       'dir': local_share_path}
        self.mod_map = {}

    @property
    def name1(self):
        return self._name1

    @property
    def name2(self):
        return self._name2

    @property
    def root1(self):
        return self._root1

    @property
    def root2(self):
        return self._root2

    @property
    def db_path(self):
        return self.paths['db']

    @property
    def db_exists(self):
        return self.paths['db'].is_file()

    @property
    def synced(self):
        return self._synced

    @property
    def filters(self):
        return compile_filters(self._filters)

    @property
    def replicas(self):
        return self._replicas

    @property
    def paths(self):
        return self._paths

    def set_db(self, cursor):
        """Record the db cursor."""
        self._db = cursor

    @property
    def db(self):
        return self._db

    def init_db(self) -> None:
        """Create the bundle's nids database."""
        if self.db_exists:
            raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST),
                                  str(self.db_path))
        os.makedirs(self.paths['dir'], mode=0o770, exist_ok=True)
        self.db_path.touch(mode=0o777)
        with database.ContextManager(self.db_path) as cur:
            cur.executescript(SCHEMA_SQL)

    def upsert_pair(self, nid1: str, nid2: str, rel1: str, rel2: str) -> None:
        """
        Insert or update a nodes' pair with given NIDs and relative paths.
        - Inserts rel1 and rel2 into paths if needed.
        - Inserts a new row into nodes or updates existing one based on nid1
          and nid2.
        """
        # Ensure both paths exist in paths table
        self.db.execute('INSERT OR IGNORE INTO paths (relpath) VALUES (?)',
                        (rel1,))
        self.db.execute('INSERT OR IGNORE INTO paths (relpath) VALUES (?)',
                        (rel2,))

        # Fetch their path IDs
        self.db.execute('SELECT path_id FROM paths WHERE relpath = ?',
                        (rel1,))
        p1 = self.db.fetchone()[0]
        self.db.execute('SELECT path_id FROM paths WHERE relpath = ?', (rel2,))
        p2 = self.db.fetchone()[0]

        # Upsert into nodes: use nid1 and nid2 as composite key
        # 'unprocessed' is a default value for status. It will be updated
        # automatically by the database triggers.
        self.db.execute("""
            INSERT INTO nodes (nid1, nid2, path1_id, path2_id, status)
            VALUES (?, ?, ?, ?, 'unprocessed')
            ON CONFLICT(nid1, nid2) DO UPDATE SET
                path1_id = excluded.path1_id,
                path2_id = excluded.path2_id;
        """, (nid1, nid2, p1, p2))

    def update_nid_relpath(self, nid_col: str, value: str, rel: str) -> None:
        # Insert relpath if it does not exist yet
        self.db.execute('INSERT OR IGNORE INTO paths (relpath) VALUES (?)',
                        (rel,))
        self.db.execute('SELECT path_id FROM paths WHERE relpath = ?', (rel,))
        path_id = self.db.fetchone()[0]

        other_col = 'path1_id' if nid_col == 'nid1' else 'path2_id'

        query = f'UPDATE nodes SET {other_col} = ? WHERE {nid_col} = ?'
        params = [path_id, value]

        self.db.execute(query, params)

    def remove_nid(self, nid_column: str, value: str) -> None:
        self.db.execute(f'DELETE FROM nodes WHERE {nid_column} = ?',
                        (value,))

    def get_twin_nid(self, nid_column: str, value: str) -> str | None:
        other_col = 'nid2' if nid_column == 'nid1' else 'nid1'
        query = f'SELECT {other_col} FROM nodes WHERE {nid_column} = ?'
        params = [value]
        self.db.execute(query, params)
        result = self.db.fetchone()
        return result[0] if result else None

    def get_nid_status(self, nid_column: str, value: str) -> str | None:
        query = f'SELECT status FROM nodes WHERE {nid_column} = ?'
        self.db.execute(query, (value,))
        result = self.db.fetchone()
        return result[0] if result else None

    def get_relpath_matching_current(self, nid_column: str,
                                     value: str) -> str | None:
        """
        Get possible relpath matching the nid value provided as nid1_or_2, read
        from mod_map, or pending, or else, from the already paired nodes, but
        not from unprocessed nodes (we want current value, if there is).
        """
        if (value in self.mod_map
           and self.mod_map[value][1] == nid_column[-1]):
            return str(self.mod_map[value][0].relpath)
        col_idx = 3 if nid_column == 'nid1' else 4
        self.db.execute(f"""
            SELECT relpath1, relpath2 FROM nodes_view
            WHERE {nid_column} = ? AND status IN ('pending', 'paired')
        """, (value,))
        row = self.db.fetchone()
        return row[col_idx - 3] if row else None

    def get_current_paired_relpath(self, nid_column: str,
                                   source_nid: str) -> str | None:
        """
        Get current relpath of the paired Node, if it still exists.

        nid_column the "source" Node's nid ('nid1' or 'nid2')
        """
        dest_side = 'nid2' if nid_column == 'nid1' else 'nid1'
        dest_nid = self.get_twin_nid(nid_column, source_nid)
        if dest_nid:
            return self.get_relpath_matching_current(dest_side, dest_nid)
        else:
            return None

    def preload_nodes_data(self) -> tuple[dict[str, tuple[str, str]],
                                          dict[str, tuple[str, str]]]:
        """
        Load (nid1, nid2, relpath) from all db rows.
        Return two dicts :
          - cache1 : nid1: (relpath, nid2)
          - cache2 : nid2: (relpath, nid1)
        """
        query = 'SELECT nid1, nid2, relpath1, relpath2 FROM nodes_view'
        result = self.db.execute(query)

        cache1 = {}
        cache2 = {}

        for nid1, nid2, relpath1, relpath2 in result.fetchall():
            cache1[nid1] = (relpath1, nid2)
            cache2[nid2] = (relpath2, nid1)

        return cache1, cache2

    def get_stored_relpath_from_nid(self, side: str, nid: str) -> str | None:
        """
        Retrieve the stored relative path for a given node ID and side.

        :param side: '1' or '2'
        :param nid: the node ID
        :return: the stored relative path if found, None otherwise
        """
        column_nid = f'nid{side}'
        column_relpath = f'relpath{side}'
        query = f"""
            SELECT {column_relpath}
            FROM nodes_view
            WHERE {column_nid} = ?
        """
        self.db.execute(query, (nid,))
        row = self.db.fetchone()
        return row[0] if row else None

    def set_paired(self, nid_column: str, value: str) -> None:
        """
        Marks a pair as ‘paired’ by specifying only one of the two NIDs.
        nid_column indicates ‘nid1’ or ‘nid2’, and value the value of the NID
        """
        query = f"""
            UPDATE nodes
            SET status = 'paired'
            WHERE {nid_column} = ?
        """
        self.db.execute(query, (value,))

    def set_unprocessed(self, nid_column: str, value: str) -> None:
        """
        Marks a pair as ‘unprocessed’ by specifying only one of the two NIDs.
        nid_column indicates ‘nid1’ or ‘nid2’, and value the value of the NID
        """
        query = f"""
            UPDATE nodes
            SET status = 'unprocessed'
            WHERE {nid_column} = ?
        """
        self.db.execute(query, (value,))

    def remove_stale_nodes(self, scan1, scan2):
        """
        Remove nodes from the database that have been deleted from both trees.

        :param scan1: list of relpaths from tree 1
        :param scan2: list of relpaths from tree 2
        """
        self.db.execute('SELECT node_id, nid1, nid2, relpath1, relpath2 '
                        'FROM nodes_view')
        stale_ids = []
        missing_paths = set()

        nids_in_sync = set(self.mod_map.keys())

        for row in self.db.fetchall():
            id_, nid1, nid2, rel1, rel2 = row
            if (rel1 not in scan1) and (rel2 not in scan2):
                if nid1 in nids_in_sync or nid2 in nids_in_sync:
                    continue
                stale_ids.append(id_)
                missing_paths.update([rel1, rel2])

        for id_ in stale_ids:
            self.db.execute('DELETE FROM nodes WHERE node_id = ?', (id_,))

        for relpath in missing_paths:
            shared.no_change_msg = ''
            print(_ob(f'DELETED ON BOTH SIDES: {relpath}'))
            LOGGER.info(f'DELETED ON BOTH SIDES: {relpath}')

    def create_ts_file(self):
        replicas = '\n'.join([f'{r} = 0' for r in self.replicas])
        if replicas:
            replicas = '\n' + replicas
        default_content = f"""synced = 0{replicas}
"""
        with open(self.paths['ts'], 'w') as f:
            f.write(default_content)

    def get_timestamp(self, replica=None):
        """Get synced's timestamp or for the provided replica."""
        entry = 'synced'
        if replica is not None:
            entry = replica
        with open(self.paths['ts']) as f:
            ts = toml.load(f)
        if entry not in ts:
            return self.set_timestamp(replica=replica)
        return ts[entry]

    def set_timestamp(self, replica=None):
        """Update synced's timestamp or for the provided replica."""
        entry = 'synced'
        if replica is not None:
            entry = replica
        with open(self.paths['ts']) as f:
            ts = toml.load(f)
        ts[entry] = time()
        with open(self.paths['ts'], 'w') as f:
            toml.dump(ts, f)
        return ts[entry]

    def connected_replicas(self):
        connected_replicas = dict()
        for r in self.replicas:
            if self.replicas[r]['root'].is_dir():
                connected_replicas[r] = self.replicas[r]
            else:
                terminal.echo_warning(f'Cannot find replica {r} '
                                      f"(path: {self.replicas[r]['root']})")
        return connected_replicas
