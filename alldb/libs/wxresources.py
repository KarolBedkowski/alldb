# -*- coding: utf-8 -*-

"""
"""
from __future__ import with_statement


__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2004-2010"
__version__ = "2010-05-14"


import re

from wx import xrc

from .appconfig import AppConfig


def _localize(match_object):
	return ''.join((match_object.group(1), _(match_object.group(2)),
			match_object.group(3)))


_CACHE = {}


def load_xrc_resource(filename):
	xrcfile_path = AppConfig().get_data_file(filename)
	res = _CACHE.get(xrcfile_path)
	if res is None:
		with open(xrcfile_path) as xrc_file:
			data = xrc_file.read()
		data = data.decode('UTF-8')
		re_gettext = re.compile(r'(\<label\>)(.*?)(\<\/label\>)')
		data = re_gettext.sub(_localize, data)
		re_gettext = re.compile(r'(\<title\>)(.*?)(\<\/title\>)')
		data = re_gettext.sub(_localize, data)
		re_gettext = re.compile(r'(\<tooltip\>)(.*?)(\<\/tooltip\>)')
		data = re_gettext.sub(_localize, data)
		data = data.encode('UTF-8')

		res = xrc.EmptyXmlResource()
		res.LoadFromString(data)
		_CACHE[xrcfile_path] = res

	return res

# vim: encoding=utf8: ff=unix:
