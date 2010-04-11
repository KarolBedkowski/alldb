# -*- coding: utf-8 -*-

"""
AllDb
Eksportowanie i importoweanie plików kategori
"""
from __future__ import with_statement

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009'
__version__ = '0.1'
__release__ = '2009-11-12'


import time
try:
	import cjson
	_DECODER = cjson.decode
	_ENCODER = cjson.encode
except ImportError:
	import json
	_DECODER = json.loads
	_ENCODER = json.dumps

from alldb.gui.dialogs import dialogs
from alldb.model import objects
from alldb.libs import appconfig


def export_category(parent_wnd, cls):
	filename = cls.name + '.category'
	filename = dialogs.dialog_file_save(parent_wnd, _('Export category'),
			_('Category Files (*.category)|*.category|All files|*.*'),
			filename)
	if filename is None:
		return

	with open(filename, 'w') as efile:
		efile.write('AllDb|Export|Category|1.0|' + time.asctime() + '\n')
		efile.write(_ENCODER(cls.export()))


def import_category(parent_wnd):
	acfg = appconfig.AppConfig()
	filename = dialogs.dialog_file_load(parent_wnd, _('Import category'),
			_('Category Files (*.category)|*.category|All files|*.*'),
			default_dir=acfg.templates_dir)
	if filename is None:
		return None

	items = []
	with open(filename, 'r') as efile:
		header = efile.readline()
		if not header.startswith('AllDb|Export|Category|1.0|'):
			raise RuntimeError(_('Invalid export file'))
		for line in efile:
			cls = objects.ADObjectClass()
			cls.import_obj(_DECODER(line))
			items.append(cls)
	if not items:
		raise RuntimeError(_('Invalid data in export file'))
	return items



# vim: encoding=utf8: ff=unix:
