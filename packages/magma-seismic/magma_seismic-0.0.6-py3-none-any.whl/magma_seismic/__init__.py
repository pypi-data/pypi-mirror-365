#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pkg_resources import get_distribution

from magma_seismic.download import Download

__version__ = get_distribution("magma-seismic").version
__author__ = "Martanto"
__author_email__ = "martanto@live.COM"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025, MAGMA Indonesia"
__url__ = "https://github.com/martanto/magma-seismic"

__all__ = [
    "__version__",
    "__author__",
    "__author_email__",
    "__license__",
    "__copyright__",
    "Download",
]
