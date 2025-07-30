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
import datetime

import click
from importlib.metadata import version

from microlib.terminal import echo_error

from . import env, commands
from .errors import ZanoError
from zano.shared import MAIN_LOGGER, LOGGER

__version__ = version('zano')

PYVER = sys.version.replace('\n', ' ')
MESSAGE = f'Zano {__version__}\n'\
    f'running under python {PYVER}.\n'\
    'Copyright (C) 2021-2025 Nicolas Hainaux\n'\
    'This program comes with ABSOLUTELY NO WARRANTY.\n'\
    'This is free software, and you are welcome to redistribute it '\
    'under certain conditions. Its license is the GPL version 3 or later.'

__all__ = ['run']


@click.group()
@click.version_option(message=MESSAGE)
def run():
    """Help synchronize folders, even when both sides have changes."""


def _cmd(cmd, *args, do_click_echo=echo_error, **kwargs):
    """Generic command"""
    ts = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    LOGGER.info(f'\n{ts} STARTING {cmd.__qualname__}')
    try:
        cmd(*args, **kwargs)
    except ZanoError as e:
        do_click_echo(str(e))


@run.command('sync')
@click.argument('name')
@click.option('-B', '--backup-before', is_flag=True, default=False,
              show_default=True, help='if true, a backup of each synced side '
              'will be performed BEFORE the synchronization. Requires to '
              'provide a backup path for each synced side in the bundle\'s '
              'config file. Backups are not filtered, so everything can be '
              'restored from them.')
@click.option('-b', '--backup-after', is_flag=True, default=False,
              show_default=True, help='if true, a backup of each synced side '
              'will be performed AFTER the synchronization. Requires to '
              'provide a backup path for each synced side in the bundle\'s '
              'config file. Backups are not filtered, so everything can be '
              'restored from them.')
@click.option('--push', is_flag=True, default=False,
              show_default=True, help='if true, no question will be asked '
              'before pushing changes to replicas.')
@click.option('--autocommit', type=bool, default=None,
              show_default=False, help='turn autocommit mode on or off.')
def sync(name, backup_before, backup_after, push, autocommit):
    """
    Synchronize two directories.
    """
    MAIN_LOGGER.info(f'sync starting: {name = }')

    if autocommit is None:
        autocommit = env.load_config()['autocommit']

    _cmd(commands.sync, name, backup_before=backup_before,
         backup_after=backup_after, push=push, autocommit=autocommit)
    MAIN_LOGGER.info('sync finished')
