# -*- coding: utf-8 -*-

"""
"""
from __future__ import with_statement

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-17'

import logging
import time

from sldb import SchemaLessDatabase
import sldb_objects
from sqlite_engine import SqliteEngine

engine = SqliteEngine('test')
storage = SchemaLessDatabase(engine)
storage.open()

cls = sldb_objects.ObjectClass(name='test'+time.asctime())
cls.default_data = [('f1', 'str', '', None), ('f2', 'int', '', None)]
storage.put_class(cls)
print cls

cid = cls.oid
cls = storage.get_class(cid)
print cls

print '\nget_classes'
clss = storage.get_classes()
print '\n'.join(map(str, clss))

print

obj = cls.create_object()
storage.put_object(obj)
print obj

obj = storage.get_object(obj.oid)
print obj

print '\nget_objects_by_class'
print '\n'.join(map(str, storage.get_objects_by_class(cls.oid)))


storage.close()
# vim: encoding=utf8: ff=unix:
