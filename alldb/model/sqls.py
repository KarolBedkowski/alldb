# -*- coding: utf-8 -*-

"""
"""
from __future__ import with_statement


__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-05-17"


INIT_SQLS = (
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


OPTIMISE_SQLS = (
		'vacuum;',
		'analyze;',
)


# vim: encoding=utf8: ff=unix:
