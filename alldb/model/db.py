# -*- coding: utf-8 -*-

"""
Obiekt bazy dany - dostęp do danych
"""
from __future__ import with_statement

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-05-17"


import os.path
import logging
import sqlite3

from alldb.libs import debug

from .sqlite_engine import SqliteEngineTx
from .sqls import INIT_SQLS
from .objects import ADObjectClass, ADObject, SearchResult


_LOG = logging.getLogger(__name__)


class Db(object):
	"""docstring for Db"""

	def __init__(self, filename):
		self.filename = filename
		self._database = None

	@property
	def classes(self):
		return self.get_classes() or []

	def open(self):
		_LOG.info('SchemaLessDatabase.open()')
		bdir = os.path.dirname(self.filename)
		if bdir and not os.path.exists(bdir):
			os.makedirs(bdir)
		self._database = sqlite3.connect(self.filename)
		self._after_open()

	def close(self):
		_LOG.info('SchemaLessDatabase.close()')
		if self._database:
			self._database.close()

	def sync(self):
		if self._database:
			self._database.commit()

	def create_cursor(self):
		if self._database:
			return self._database.cursor()
		return None

	def put_class(self, cls):
		with SqliteEngineTx(self) as trans:
			cls = cls if hasattr(cls, '__iter__') else (cls, )
			for icls in cls:
				if hasattr(icls, 'before_save'):
					icls.before_save()
				if icls.changed_fields_names:
					res = list(trans.get_objects_by_class(icls.oid))
					for oid, class_id, data in res:
						obj = self._create_single_object(oid, class_id, data)
						obj.update_fields_names(icls.changed_fields_names)
						trans.put_object((obj, ))
					trans.rename_fields_in_blobs(icls.oid, icls.changed_fields_names)
			trans.put_class(cls)
		self.sync()

	def get_class(self, class_id):
		with SqliteEngineTx(self) as trans:
			res = trans.get_class(class_id)
			for oid, name, data in res:
				return self._create_class_object(oid, name, data)

	def get_classes(self):
		with SqliteEngineTx(self) as trans:
			return [self._create_class_object(cid, name, data)
					for cid, name, data in trans.get_classes()]

	def del_class(self, oids):
		with SqliteEngineTx(self) as trans:
			trans.del_class(oids)
		self.sync()

	def load_class(self, class_id):
		_LOG.info('Db.load_class(%r)', class_id)
		result = SearchResult()
		cls = self.get_class(class_id)
		if cls:
			result.set_class(cls)
			items = self.get_objects_by_class(class_id)
			result.set_items(items)
		return result

	def put_object(self, obj):
		with SqliteEngineTx(self) as trans:
			self.put_object_in_trans(trans, obj)
		self.sync()

	def put_object_in_trans(self, trans, obj):
		obj = obj if hasattr(obj, '__iter__') else (obj, )
		for iobj in obj:
			if hasattr(iobj, 'before_save'):
				iobj.before_save()
			trans.put_object((iobj, ))
			for field, blob in iobj.blobs.iteritems():
				trans.put_blob(iobj.oid, field, blob)

	def get_object(self, oid):
		with SqliteEngineTx(self) as trans:
			res = trans.get_object(oid)
			for oid, class_id, data in res:
				return self._create_single_object(oid, class_id, data)

	def del_objects(self, oids):
		with SqliteEngineTx(self) as trans:
			trans.del_object(oids)
		self.sync()

	def get_objects_by_class(self, class_id):
		with SqliteEngineTx(self) as trans:
			res = trans.get_objects_by_class(class_id)
			return [self._create_single_object(oid, class_id, data)
					for oid, class_id, data in res]

	@debug.time_method
	def get_blob(self, object_id, field):
		with SqliteEngineTx(self) as trans:
			return trans.get_blob(object_id, field)

	def put_blob(self, object_id, field, data):
		with SqliteEngineTx(self) as trans:
			trans.put_blob(object_id, field, data)
		self.sync()

	def optimize(self):
		"""optimize sql database"""
		_LOG.info('Db.optimize')
		cur = self._database.cursor()
		_LOG.debug('Db.optimize: vacum')
		cur.executescript('vacuum;')
		_LOG.debug('Db.optimize: analyze')
		cur.executescript('analyze;')
		_LOG.debug('Db.optimize: done')
		cur.close()

	def create_backup(self, filename):
		with SqliteEngineTx(self) as trans:
			trans.create_backup(filename)

	def _create_class_object(self, cid, name, data):
		cls = ADObjectClass(cid, name, self)
		cls.restore(data)
		return cls

	def _create_single_object(self, oid, class_id, data):
		obj = ADObject(oid, class_id, self)
		obj.restore(data)
		return obj

	def _after_open(self):
		cur = self._database.cursor()
		for sql in INIT_SQLS:
			cur.executescript(sql)
		cur.close()
		self._database.commit()



# vim: encoding=utf8: ff=unix:
