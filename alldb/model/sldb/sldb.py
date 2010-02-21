# -*- coding: utf-8 -*-

"""
Baza danych bez-schematowa
"""
from __future__ import with_statement

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009'
__version__ = '0.1'
__release__ = '2009-12-17'

import logging
import time

from . import sldb_objects

_LOG = logging.getLogger(__name__)


class SchemaLessDatabase(object):

	def __init__(self, engine):
		self._engine = engine

	def __contains__(self, oid):
		return oid in self._engine

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

	def put_object(self, obj):
		with self._engine.create_transaction(self) as trans:
			obj = obj if hasattr(obj, '__iter__') else (obj, )
			for iobj in obj:
				if hasattr(iobj, 'before_save'):
					iobj.before_save()
			trans.put_object(obj)
		self._engine.sync()

	def get_object(self, oid):
		with self._engine.create_transaction(self) as trans:
			res = trans.get_object(oid)
			for oid, class_id, data in res:
				return self._create_single_object(oid, class_id, data)

	def get_objects_by_class(self, class_id):
		with self._engine.create_transaction(self) as trans:
			res = trans.get_objects_by_class(class_id)
			return [self._create_single_object(oid, class_id, data)
					for oid, class_id, data in res]

	def _create_class_object(self, cid, name, data):
		cls = sldb_objects.ObjectClass(cid, name, self)
		cls.restore(data)
		return cls

	def _create_single_object(self, oid, class_id, data):
		obj = sldb_objects.Object(oid, class_id, self)
		obj.restore(data)
		return obj


if __name__ == '__main__':

	def test():
		from .sqlite_engine import SqliteEngine

		engine = SqliteEngine('test')
		storage = SchemaLessDatabase(engine)
		storage.open()

		cls = sldb_objects.ObjectClass(name='test' + time.asctime())
		cls.default_data = [('f1', 'str', '', None), ('f2', 'int', '', None)]
		storage.put_class(cls)
		print cls

		cid = cls.oid
		cls = storage.get_class(cid)
		print cls

		print '\nget_classes'
		clss = storage.get_classes()
		print '\n'.join((str(_cls) for _cls in clss))

		print

		obj = cls.create_object()
		storage.put_object(obj)
		print obj

		obj = storage.get_object(obj.oid)
		print obj

		print '\nget_objects_by_class'
		print '\n'.join(str(_obj) for _obj in storage.get_objects_by_class(cls.oid))


		storage.close()

	test()

# vim: encoding=utf8: ff=unix:
