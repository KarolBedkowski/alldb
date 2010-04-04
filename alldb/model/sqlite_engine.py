# -*- coding: utf-8 -*-

"""
Engine do zapisywania danych w bazie sqlite.
"""
from __future__ import with_statement

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2010'
__version__ = '0.1'
__release__ = '2010-02-21'

import logging
import sqlite3
import os
import os.path
import base64
import gzip
try:
	import cjson
	_DECODER = cjson.decode
	_ENCODER = cjson.encode
except ImportError:
	import json
	_DECODER = json.loads
	_ENCODER = json.dumps


_LOG = logging.getLogger(__name__)

_INIT_SQLS = (
	'''PRAGMA encoding = "UTF-8";''',
	'''PRAGMA foreign_keys = 1;''',
	'''PRAGMA locking_mode=EXCLUSIVE; ''',
	'''create table if not exists classes (
		id integer primary key autoincrement,
		name varchar(100),
		updated timestamp,
		data blob);''',
	'''create table if not exists objects (
		id integer primary key autoincrement,
		class_id integer references classes (id) on delete cascade,
		updated timestamp,
		data blob);''',
	'''create index if not exists objects_class_idx
		on objects (class_id);''',
	'''create table if not exists blobs (
		object_id integer references objects (id) on delete cascade,
		field varchar,
		data blob,
		primary key (object_id, field));''')


class SqliteEngine(object):
	"""docstring for SqliteEngine"""

	def __init__(self, filename):
		self.filename = filename
		self.database = None

	def __contains__(self, oid):
		if not self.database:
			return False
		cur = self.database.cursor()
		cur.execute('select 1 from objects where id=?', (oid, ))
		obj = cur.fetchone()
		cur.close()
		return bool(obj)

	def open(self):
		_LOG.info('SqliteEngine.open(); filename=%s', self.filename)
		bdir = os.path.dirname(self.filename)
		if not os.path.exists(bdir):
			os.makedirs(bdir)
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

	def optimize(self):
		_LOG.info('SqliteEngine.optimize')
		cur = self.database.cursor()
		_LOG.debug('SqliteEngine.optimize: vacum')
		cur.executescript('vacuum;')
		_LOG.debug('SqliteEngine.optimize: analyze')
		cur.executescript('analyze;')
		_LOG.debug('SqliteEngine.optimize: done')
		cur.close()

	def _after_open(self):
		cur = self.database.cursor()
		for sql in _INIT_SQLS:
			cur.executescript(sql)
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
		for ioid in oid:
			self._cursor.execute('delete from objects where id=?', (ioid, ))

	def put_object(self, objs):
		_LOG.debug('SqliteEngineTx.put(%r)', objs)
		cur = self._cursor
		for obj in objs:
			data = _ENCODER(obj.dump())
			if obj.oid:
				cur.execute('update objects set class_id=?, data=? where id=?',
						(obj.class_id, data, obj.oid))
			else:
				cur.execute('insert into objects (id, class_id, data) values (?, ?, ?)',
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
		for cid in class_id:
			self._cursor.execute('delete from classes where id = ?', (cid, ))

	def get_blob(self, object_id, field):
		_LOG.debug('SqliteEngineTx.get_blob(%s, %s)', object_id, field)
		self._cursor.execute('select data from blobs where object_id=? and field=?',
				(object_id, field))
		data = self._cursor.fetchone()
		return data[0] if data else None

	def put_blob(self, object_id, field, data):
		_LOG.debug('SqliteEngineTx.put_blob(%s, %s, len=%d)', object_id, field,
				len(data or []))
		self._cursor.execute('delete from blobs where object_id=? and field=?',
				(object_id, field))
		if data:
			self._cursor.execute('insert into blobs (object_id, field, data) values '\
					'(?, ?, ?)', (object_id, field, sqlite3.Binary(data)))

	def rename_fields_in_blobs(self, class_id, changes):
		for old_name, new_name in changes:
			self._cursor.execute('update blobs set field=? where object_id in '
					'(select id from objects where class_id=?) and field=?',
					(new_name, class_id, old_name))

	def create_backup(self, filename):
		bfile =  gzip.open(filename, 'w')
		self._cursor.execute('select id, name, data from classes')
		for row in self._cursor:
			bfile.write('CLS:' + _ENCODER(row) + '\n')
		self._cursor.execute('select id, class_id, data from objects')
		for row in self._cursor:
			bfile.write('OBJ:' + _ENCODER(row) + '\n')
		self._cursor.execute('select object_id, field, data from blobs')
		for object_id, field, data in self._cursor:
			sdata = dict(object_id=object_id, field=field,
					data=base64.b64encode(data))
			bfile.write('BLO:' + _ENCODER(sdata) + '\n')
		bfile.close()


# vim: encoding=utf8: ff=unix:
