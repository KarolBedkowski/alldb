# -*- coding: utf-8 -*-

"""
Obiekt bazy dany - dostęp do danych
"""
from __future__ import with_statement

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2009-2010'
__version__ = '0.1'
__release__ = '2009-12-17'


import logging

from .sqlite_engine import SqliteEngine
from .objects import ADObjectClass, ADObject, SearchResult

_LOG = logging.getLogger(__name__)


class Db(object):
	"""docstring for Db"""

	def __init__(self, filename):
		self._engine = SqliteEngine(filename)

	def __contains__(self, oid):
		return oid in self._engine

	@property
	def classes(self):
		return self.get_classes() or []

	def open(self):
		_LOG.info('SchemaLessDatabase.open()')
		self._engine.open()

	def close(self):
		_LOG.info('SchemaLessDatabase.close()')
		self._engine.close()

	def put_class(self, cls):
		with self._engine.create_transaction(self) as trans:
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
		self._engine.sync()

	def get_class(self, class_id):
		with self._engine.create_transaction(self) as trans:
			res = trans.get_class(class_id)
			for oid, name, data in res:
				return self._create_class_object(oid, name, data)

	def get_classes(self):
		with self._engine.create_transaction(self) as trans:
			return [self._create_class_object(cid, name, data)
					for cid, name, data in trans.get_classes()]

	def del_class(self, oids):
		with self._engine.create_transaction(self) as trans:
			trans.del_class(oids)
		self._engine.sync()

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
		with self._engine.create_transaction(self) as trans:
			obj = obj if hasattr(obj, '__iter__') else (obj, )
			for iobj in obj:
				if hasattr(iobj, 'before_save'):
					iobj.before_save()
				trans.put_object((iobj, ))
				for field, blob in iobj.blobs.iteritems():
					trans.put_blob(iobj.oid, field, blob)
		self._engine.sync()

	def get_object(self, oid):
		with self._engine.create_transaction(self) as trans:
			res = trans.get_object(oid)
			for oid, class_id, data in res:
				return self._create_single_object(oid, class_id, data)

	def del_objects(self, oids):
		with self._engine.create_transaction(self) as trans:
			trans.del_object(oids)
		self._engine.sync()

	def get_objects_by_class(self, class_id):
		with self._engine.create_transaction(self) as trans:
			res = trans.get_objects_by_class(class_id)
			return [self._create_single_object(oid, class_id, data)
					for oid, class_id, data in res]

	def get_blob(self, object_id, field):
		with self._engine.create_transaction(self) as trans:
			return trans.get_blob(object_id, field)

	def put_blob(self, object_id, field, data):
		with self._engine.create_transaction(self) as trans:
			trans.put_blob(object_id, field, data)
		self._engine.sync()

	def optimize(self):
		"""optimize sql database"""
		self._engine.optimize()

	def create_backup(self, filename):
		with self._engine.create_transaction(self) as trans:
			trans.create_backup(filename)

	def _create_class_object(self, cid, name, data):
		cls = ADObjectClass(cid, name, self)
		cls.restore(data)
		return cls

	def _create_single_object(self, oid, class_id, data):
		obj = ADObject(oid, class_id, self)
		obj.restore(data)
		return obj


# vim: encoding=utf8: ff=unix:
