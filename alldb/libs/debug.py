# -*- coding: UTF-8 -*-


__author__ = "Karol Będkowski"
__copyright__ = "Copyright (C) Karol Będkowski, 2009-2010"
__version__ = "2010-05-03"


from contextlib import contextmanager
import time
import logging

_LOG = logging.getLogger(__name__)


@contextmanager
def time_it(name):
	_ts = time.time()
	yield
	_LOG.debug('%s: %0.4f', name, time.time() - _ts)
