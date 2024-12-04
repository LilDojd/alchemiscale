#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Copyright 2011-2021, Nigel Small
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Previously a Py2to3 compatibility layer from py2neo
from __future__ import absolute_import

from configparser import ConfigParser
import os

atomic_types = (bool, bytearray, bytes, float, int, str)
bytes_types = (bytearray, bytes)
integer_types = (int,)
list_types = (list, map)
numeric_types = (int, float)
string_types = (bytes, str)
unicode_types = (str,)
utf8_types = ()

long = int
uchr = chr
UNICODE = str


def ustr(s, encoding="utf-8"):
    """Convert a value to a Unicode string, held in a Python `str` object."""
    if isinstance(s, str):
        return s
    elif isinstance(s, (bytes, bytearray)):
        return s.decode(encoding=encoding)
    else:
        try:
            return s.__str__()
        except AttributeError:
            return str(s, encoding=encoding)


def xstr(s, encoding="utf-8"):
    """Convert argument to string type returned by __str__."""
    if isinstance(s, str):
        return s
    elif isinstance(s, bytes):
        return s.decode(encoding)
    else:
        return str(s)


class PropertiesParser(ConfigParser):
    def read_properties(self, filename, section=None):
        if not section:
            basename = os.path.basename(filename)
            if basename.endswith(".properties"):
                section = basename[:-11]
            else:
                section = basename
        with open(filename) as f:
            data = f.read()
        self.read_string("[%s]\n%s" % (section, data), filename)
