# -*- coding: UTF-8 -*-

from contextlib import contextmanager
import time
import logging

_LOG = logging.getLogger(__name__)


@contextmanager
def time_it(name):
	_ts = time.time()
	yield
	_LOG.debug('%s: %0.4f', name, time.time() - _ts)


