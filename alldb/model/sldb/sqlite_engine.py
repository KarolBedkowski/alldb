# -*- coding: utf-8 -*-

"""
Engine do zapisywania danych w bazie sqlite.
"""
from __future__ import with_statement

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2010'
__version__ = '0.1'
__release__ = '2010-02-21'

import logging
import sqlite3
try:
	import cjson
	_DECODER = cjson.decode
	_ENCODER = cjson.encode
except ImportError:
	import json
	_DECODER = json.loads
	_ENCODER = json.dumps

#import cPickle
#_ENCODER = cPickle.dumps
#_DECODER = cPickle.loads

_LOG = logging.getLogger(__name__)


_INIT_SQLS = (
'''create table if not exists classes (
	id integer primary key autoincrement,
	name varchar(100),
	updated timestamp,
	data blob)''',
"""create table if not exists objects (
	id integer primary key autoincrement,
	class_id integer references classes (id) on delete cascade,
	updated timestamp,
	data blob)""",
"""create index if not exists objects_class_idx
	on objects (class_id)""",
"""create table if not exists indexes (
	id integer primary key autoincrement,
	name varchar(100),
	updated timestamp,
	class_id integer references classes (id) on delete cascade)""",
'''create index if not exists indexes_idx1
	on indexes (class_id, name)''',
'''create table if not exists index_objects (
	idx_id integer not null references indexes (id) on delete cascade,
	obj_id integer not null references indexes (id) on delete cascade,
	value blob)''')


class SqliteEngine(object):
	"""docstring for SqliteEngine"""

	def __init__(self, filename):
		self.filename = filename
		self.database = None

	def __contains__(self, oid):
		if not self.database:
			return False
		cur = self.database.cursor()
		cur.execute('select 1 from objects where oid=?', (oid, ))
		obj = cur.fetchone()
		cur.close()
		return bool(obj)

	def open(self):
		_LOG.info('SchemaLessDatabase.open(); filename=%s', self.filename)
		self.database = sqlite3.connect(self.filename)
		self._after_open()

	def close(self):
		if self.database:
			self.database.close()

	def sync(self):
		if self.database:
			self.database.commit()

	def create_transaction(self, context):
		if not self.database:
			raise ValueError('No database')
		return SqliteEngineTx(self, context)

	def _after_open(self):
		cur = self.database.cursor()
		for sql in _INIT_SQLS:
			cur.execute(sql)
		cur.close()
		self.database.commit()


class SqliteEngineTx(object):

	def __init__(self, engine, context):
		self._cursor = None
		self._engine = engine
		self._context = context

	@property
	def context(self):
		return self._context

	def __enter__(self):
		self.open()
		return self

	def __exit__(self, type_=None, value=None, traceback=None):
		self.close()

	def open(self):
		if self._cursor is None:
			self._cursor = self._engine.database.cursor()

	def close(self):
		if self._cursor:
			self._cursor.close()
			self._cursor = None

	def get_object(self, oid):
		_LOG.debug('SqliteEngineTx.get(%r)', oid)
		self._cursor.execute('select id, class_id, data from objects where id = ?',
				(oid, ))
		for oid, class_id, data in self._cursor:
			yield oid, class_id, _DECODER(data)

	def get_objects_by_class(self, class_id):
		_LOG.debug('SqliteEngineTx.get_objects_by_class(%r)', class_id)
		self._cursor.execute(
				'select id, class_id, data from objects where class_id = ?',
				(class_id, ))
		for oid, class_id, data in self._cursor:
			yield oid, class_id, _DECODER(data)

	def del_object(self, oid):
		_LOG.debug('SqliteEngineTx.del_object(%r)', oid)
		if not hasattr(oid, '__iter__'):
			oid = (oid, )
		self._cursor.execute('delete from objects where oid=?', oid)

	def put_object(self, objs):
		_LOG.debug('SqliteEngineTx.put(%r)', objs)
		cur = self._cursor
		for obj in objs:
			data = _ENCODER(obj.dump())
			if obj.oid:
				cur.execute('update objects set class_id=?, data=? where oid=?',
						(obj.class_id, data, obj.oid))
			else:
				cur.execute('insert into objects (oid, class_id, data) values (?, ?, ?)',
						(obj.oid, obj.class_id, data))
				obj.oid = cur.lastrowid
			obj.sldb_context = self._context
			_LOG.debug('saved %r', obj)

	def get_class(self, class_id):
		self._cursor.execute('select id, name, data from classes where id=?',
				(class_id, ))
		for cid, name, data in self._cursor:
			yield (cid, name, _DECODER(data))

	def put_class(self, clsses):
		cur = self._cursor
		for cls in clsses:
			data = _ENCODER(cls.dump())
			if cls.oid is None or cls.oid <= 0:
				cur.execute('insert into classes (name, data) values (?, ?)',
						(cls.name, data))
				cls.oid = cur.lastrowid
			else:
				cur.execute('update classes set name=?, data=? where id=?',
						(cls.name, data, cls.oid))
			cls.sldb_context = self._context

	def get_classes(self):
		self._cursor.execute('select id, name, data from classes order by name')
		for cid, name, data in self._cursor:
			yield (cid, name, _DECODER(data))

	def del_class(self, class_id):
		_LOG.debug('SqliteEngineTx.del_class(%r)', class_id)
		if not hasattr(class_id, '__iter__'):
			class_id = (class_id, )
		self._cursor.execute('delete from classws where class_id=?', class_id)



# vim: encoding=utf8: ff=unix: