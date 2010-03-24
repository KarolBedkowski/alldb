# -*- coding: utf-8 -*-

"""
"""
from __future__ import with_statement


__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009,2010'
__version__ = '0.1'
__release__ = '2009-12-20'


import re

from wx import xrc

from .appconfig import AppConfig


def _localize(match_object):
	return ''.join((match_object.group(1), _(match_object.group(2)),
			match_object.group(3)))


_CACHE = {}


def load_xrc_resource(filename):
	xrcfile_path = AppConfig().get_data_file('alldb.xrc')
	data = _CACHE.get(xrcfile_path)
	if data is None:
		with open(xrcfile_path) as xrc_file:
			data = xrc_file.read()
		data = data.decode('UTF-8')
		re_gettext = re.compile(r'(\<label\>)(.*?)(\<\/label\>)')
		data = re_gettext.sub(_localize, data)
		data = data.encode('UTF-8')
		_CACHE[xrcfile_path] = data

	res = xrc.EmptyXmlResource()
	res.LoadFromString(data)
	return res

# vim: encoding=utf8: ff=unix:
