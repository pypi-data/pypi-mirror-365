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

class ZanoError(Exception):
    """Basic exception for errors raised by Zano."""
    def __init__(self, msg):
        super().__init__(msg)


class ConfigFileError(ZanoError):
    """When the configuration file is not correct."""
    def __init__(self, msg):
        super().__init__(msg)


class CommandError(ZanoError):
    """When a inappropriate command has been issued by the user."""
    def __init__(self, msg):
        super().__init__(msg)


class MissingPathError(ZanoError):
    """When a user provided path is required but does not exist."""
    def __init__(self, msg):
        super().__init__(msg)


class NoSuchBundleError(ZanoError):
    """When no bundle matching the name provided by user can be found."""
    def __init__(self, msg):
        super().__init__(msg)
