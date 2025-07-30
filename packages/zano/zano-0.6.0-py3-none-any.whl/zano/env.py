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

import json
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

import blessed
from microlib import XDict

LOG_CONFIG = {}

ZANO_LOCAL_SHARE = Path.home() / '.local/share/zano'
ZANO_CONFIG_DIR = Path.home() / '.config/zano'
ROOT_PATH = Path(__file__).parent.parent.parent

BACKUP_LOG_DIR = Path('~/.local/log/zano')

DEFAULT_CONFIG = {'logging': {'log_dir': '~/.local/share/zano/log',
                              'log_level': 'INFO',
                              'max_bytes': '1',  # MB
                              'backup_count': 9
                              },
                  'autocommit': True
                  }


def load_config():
    """Load configuration file"""
    config = XDict(DEFAULT_CONFIG)

    # Paths to check for configuration file
    config_paths = [Path('/etc/zano/zano.json'),
                    Path.home() / '.config/zano/zano.json']

    # Update config with user redefined settings, if any
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config.recursive_update(json.load(f))
            except Exception as e:
                print(f'Error reading {config_path}: {e}')

    return config


def _gb(arg):
    term = blessed.Terminal()
    return term.green(term.bold(arg))


def _yb(arg):
    term = blessed.Terminal()
    return term.gold(term.bold(arg))


def _ob(arg):
    term = blessed.Terminal()
    return term.darkorange(term.bold(arg))


def _rb(arg):
    term = blessed.Terminal()
    return term.firebrick(term.bold(arg))


def _bb(arg):
    term = blessed.Terminal()
    return term.steelblue1(term.bold(arg))


def configure_logging():
    global LOG_CONFIG
    LOG_CONFIG = load_config()['logging']

    log_dir0 = Path(LOG_CONFIG.get('log_dir')).expanduser()
    log_level_name = LOG_CONFIG.get('log_level', 'INFO')
    log_level = getattr(logging, log_level_name)

    # check we have the rights to write to the path defined from config;
    # otherwise fallback to another place
    try:
        log_dir0.mkdir(parents=True, exist_ok=True)
        log_dir = log_dir0
    except PermissionError:
        log_dir1 = BACKUP_LOG_DIR.expanduser()
        log_dir1.mkdir(parents=True, exist_ok=True)
        print(f'Cannot use {log_dir0}, using {log_dir1} instead')
        log_dir = log_dir1

    log_file = log_dir / 'zano.log'
    LOG_CONFIG.update({'log_dir': log_dir, 'log_file': log_file})

    # Setup root logger, formatter, handlers
    logger = logging.getLogger()
    logger.setLevel(log_level)

    return logger


def get_logger(name, simple_format=False):
    """
    Get a logger using simple or detailed format.

    :param name: logger's name
    :type name: str
    :param simple_format: use detailed or simple messages
    :type simple_format: boolean (True or False)
    """
    global LOG_CONFIG
    # Ensure basic configuration has been made
    if not LOG_CONFIG:
        configure_logging()

    logger = logging.getLogger(name)

    # Remove existing loggers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    if simple_format:
        formatter = logging.Formatter('%(message)s')
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - '
            '[%(filename)s:%(lineno)d] - %(message)s'
        )

    log_file = LOG_CONFIG['log_dir'] / f'{name.replace(".", "_")}.log'

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=int(LOG_CONFIG['max_bytes']) * 1024 * 1024,
        backupCount=int(LOG_CONFIG['backup_count'])
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
