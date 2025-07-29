#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Androcli - Android CLI tool for reverse shell operations and APK building

A powerful command-line tool for Android penetration testing and reverse shell operations.
This tool allows you to build APK files with reverse shell capabilities and interact
with Android devices remotely.

Author: AryanVBW
Email: whitedevil367467@gmail.com
"""

__version__ = '1.0.0'
__author__ = 'AryanVBW'
__email__ = 'whitedevil367467@gmail.com'
__description__ = 'Android CLI tool for reverse shell operations and APK building'

from .main import main
from .utils import *

__all__ = ['main', 'utils']