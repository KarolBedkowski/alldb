# -*- coding: utf-8 -*-

"""
Obiekt bazy dany - dostęp do danych
"""
from __future__ import with_statement

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009'
__version__ = '0.1'
__release__ = '2009-12-17'


import logging

from .sldb import SchemaLessDatabase, SqliteEngine
from .objects import ADObjectClass, ADObject, SearchResult

_LOG = logging.getLogger(__name__)


class Db(SchemaLessDatabase):
	"""docstring for Db"""

	def __init__(self, filename):
		engine = SqliteEngine(filename)
		SchemaLessDatabase.__init__(self, engine)

	@property
	def classes(self):
		return self.get_classes() or []

	def _create_class_object(self, cid, name, data):
		cls = ADObjectClass(cid, name, self)
		cls.restore(data)
		return cls

	def _create_single_object(self, oid, class_id, data):
		obj = ADObject(oid, class_id, self)
		obj.restore(data)
		return obj

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


# vim: encoding=utf8: ff=unix:
