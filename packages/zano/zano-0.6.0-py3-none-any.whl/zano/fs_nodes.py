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
import errno
import subprocess
from pathlib import Path


class Node(object):
    """
    Mimic Path to get a quicker access to several methods, plus a mask.

    Node does not inherit from Path to avoid clutter in the tests.
    The mask is used to compute the relative path.
    st_mtime, st_ctime, st_ino are direct access to the Path().stat()
    data.

    """
    def __init__(self, *args, **kwargs):
        # Turn possible Nodes (or any object containing a path field, including
        # FakeFile and FakeDirectory from pyfakefs) among args into Paths in
        # order to be able to feed Path() with them.
        nargs = [a.path if hasattr(a, 'path') else a for a in args]
        self._path = Path(*nargs, **kwargs)
        # The mask of the first argument only will be copied, IF the first
        # argument is a Node itself and if mask has not been explicitely
        # provided in the keyword arguments.
        if 'mask' in kwargs:
            self._mask = kwargs.get('mask')
        elif len(args) >= 1 and isinstance(args[0], Node):
            self._mask = args[0].mask
        else:  # default
            if str(self._path).startswith('/'):
                self._mask = '/'
            else:
                self._mask = ''

    def __hash__(self):
        return hash(self.path)

    def __repr__(self):
        mask = self.mask
        slash = '/'
        if mask in ['', '/']:
            slash = ''
        else:
            mask = f'[[{self._mask}]]'
        rel = self.relpath
        if str(rel) == '.':
            rel = ''
            slash = ''
        return f'Node(\'{mask}{slash}{rel}\')'

    def __eq__(self, other):
        if isinstance(other, Path):
            other = Node(other)
        if not isinstance(other, Node):
            return False
        return self.path == other.path and self.mask == other.mask

    def __str__(self):
        return str(self.path)

    def __truediv__(self, key):
        return Node(self.path / key, mask=self.mask)

    def __rtruediv__(self, key):
        return Node(key / self.path)

    def __lt__(self, other):
        return self.path.__lt__(Node(other).path)

    def __le__(self, other):
        return self.path.__le__(Node(other).path)

    def __gt__(self, other):
        return self.path.__gt__(Node(other).path)

    def __ge__(self, other):
        return self.path.__ge__(Node(other).path)

    @property
    def path(self):
        return self._path

    @property
    def truestem(self):
        # taken from here https://stackoverflow.com/a/74718395/3926735
        return self.name.removesuffix(self.truesuffix)

    @property
    def truesuffix(self):
        # see truestem
        return ''.join(self._path.suffixes)

    @property
    def mask(self):
        return self._mask

    @property
    def name(self):
        return self.path.name

    @property
    def relparent(self):
        return Node(self.path.relative_to(str(self._mask)).parent)

    @property
    def parent(self):
        return Node(self.path.parent)

    @property
    def parents(self):
        for p in self.path.parents:
            yield Node(p)

    @property
    def relpath(self):
        if len(Path(str(self.mask)).parts) == len(self.path.parts):
            return Node('.')
        return Node(self.relparent / self.path.name)

    @property
    def abspath(self):
        return Node(self.path.absolute())

    @property
    def st_ctime(self):
        return self.path.stat().st_ctime

    @property
    def st_crtime(self):
        result = subprocess.run(['stat', '-c', '%W', self.path],
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()

    @property
    def stat(self):
        return self.path.stat()

    @property
    def nid(self):
        return f'{self.st_ino}:{self.st_crtime}'

    @property
    def st_mtime(self):
        return self.path.stat().st_mtime

    @property
    def st_ino(self):
        return self.path.stat().st_ino

    @property
    def size(self):
        if not self.path.exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                    str(self.path.absolute()))
        if self.path.is_dir():
            raise IsADirectoryError(errno.EISDIR, os.strerror(errno.EISDIR),
                                    str(self))
        return self.path.stat().st_size

    @property
    def depth(self):
        return len(self.path.parts) - 1

    @property
    def reldepth(self):
        parts = self.relpath.path.parts
        if parts == []:
            return 0
        else:
            return len(self.relpath.path.parts)

    def exists(self):
        return self.path.exists()

    def touch(self, mode=0o666, exist_ok=True):
        self.path.touch(mode=mode, exist_ok=exist_ok)

    def is_dir(self):
        return self.path.is_dir()

    def is_file(self):
        return self.path.is_file()

    def iterdir(self):
        for p in self.path.iterdir():
            yield Node(p)

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        self.path.mkdir(mode=mode, parents=parents, exist_ok=exist_ok)

    def chmod(self, mode):
        self.path.chmod(mode)

    def match(self, pattern):
        return self.path.match(pattern)

    def set_mtime(self, mtime):
        stat = os.stat(self.path)
        atime = stat.st_atime
        os.utime(self.path, times=(atime, mtime))

    def unlink(self, missing_ok=False):
        self.path.unlink(missing_ok=missing_ok)
