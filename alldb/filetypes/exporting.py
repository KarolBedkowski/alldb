# -*- coding: utf-8 -*-

"""
AllDb
Eksportowanie i importoweanie plików kategori
"""
from __future__ import with_statement


__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-06-11"


import gzip
import base64
import time
import logging
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


_LOG = logging.getLogger(__name__)


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


def export_items(parent_wnd, cls, items):
	filename = cls.name + '.alldb'
	filename = dialogs.dialog_file_save(parent_wnd, _('Select destination file'),
			_('AllDB Files (*.alldb)|*.alldb|All files|*.*'),
			filename)
	if filename is None:
		return

	efile = None
	try:
		efile = gzip.open(filename, 'w')
		efile.write('AllDb|Export|Items|1.0|#|')
		efile.write('|'.join((str(cls.oid), cls.name, '#', time.asctime())))
		efile.write('\n')
		blob_fields = list(cls.blob_fields)
		for item in items:
			efile.write('OBJ:')
			efile.write(_ENCODER(item.export()))
			efile.write('\n')
			for blob_field in blob_fields:
				blob = item.get_blob(blob_field)
				if blob:
					efile.write('BLO:')
					sdata = dict(object_id=item.oid, field=blob_field,
							data=base64.b64encode(blob))
					efile.write(_ENCODER(sdata))
					efile.write('\n')
	except IOError, err:
		_LOG.error('export_items: IOError', err)
		raise RuntimeError(err)
	finally:
		if efile:
			efile.close()


def import_items(parent_wnd, cls, database):
	filename = dialogs.dialog_file_load(parent_wnd, _('Select source file'),
			_('AllDB Files (*.alldb)|*.alldb|All files|*'))
	if filename is None:
		return None, None

	efile = None
	loaded_obj, loaded_blob = 0, 0
	try:
		efile = gzip.open(filename, 'r')
		header = efile.readline()
		if not header.startswith('AllDb|Export|Items|1.0|#|'):
			raise RuntimeError(_('Invalid file'))
		#_head, _cls_info, _comments = header.split('|#|', 2)
		#cls_id, cls_name = cls_info.split('|', 1)
		ids_converts = {}
		with database.create_transaction() as trans:
			while True:
				line = efile.readline()
				if line == '':
					break
				line = line.strip()
				item_type, item_data = line.split(":", 1)
				data = _DECODER(item_data)
				if item_type == 'OBJ':
					obj = cls.create_object()
					obj.import_obj(data)
					obj.oid = None
					database.put_object_in_trans(trans, obj)
					ids_converts[data['oid']] = obj.oid
					loaded_obj += 1
				elif item_type == 'BLO':
					obj_id = ids_converts[data['object_id']]
					field = data['field']
					blob = base64.b64decode(data['data'])
					trans.put_blob(obj_id, field, blob)
					loaded_blob += 1
		database.sync()
	except IOError, err:
		_LOG.error('import_items: IOError', err)
		raise RuntimeError(err)
	finally:
		if efile:
			efile.close()
	return loaded_obj, loaded_blob


# vim: encoding=utf8: ff=unix:
