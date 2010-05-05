# -*- coding: UTF-8 -*-


__author__ = "Karol Będkowski"
__copyright__ = "Copyright (C) Karol Będkowski, 2009-2010"
__version__ = "2010-05-05"


from contextlib import contextmanager
import time
import logging
from functools import wraps

_LOG = logging.getLogger(__name__)


@contextmanager
def time_it(name):
	_ts = time.time()
	yield
	_LOG.debug('%s: %0.4f', name, time.time() - _ts)


def time_method(func):
	if __debug__:

		@wraps(func)
		def wrapper(*args, **kwds):
			_ts = time.time()
			res = func(*args, **kwds)
			_LOG.debug('%s.%s: %0.4f', func.__module__, func.__name__,
					time.time() - _ts)
			return res
		return wrapper
	return func
