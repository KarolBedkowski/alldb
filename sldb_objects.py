# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-17'


import time
import logging

_LOG = logging.getLogger(__name__)


class BaseObject(object):
	"""docstring for SimpleObject"""

	__persistattr__ = ('data', )

	def __init__(self, oid=None, context=None):
		self.oid = oid
		self.updated = None
		self.sldb_context = context
		self.data = {}

	def __repr__(self):
		return '<%s: %r>' % (self.__class__.__name__, self.__dict__)

	def __getitem__(self, key, default=None):
		return self.data.get(key, default)

	def __setitem__(self, key, value):
		self.data[key] = value

	def dump(self):
		return dict(((key, getattr(self, key)) for key in self.__persistattr__))

	def restore(self, data):
		for key in self.__persistattr__:
			if key in data:
				setattr(self, key, data[key])

	def before_save(self, context=None):
		if context:
			self.sldb_context = context
		self.updated = time.time()


class ObjectClass(BaseObject):
	__slots__ = ('name', 'default_data', 'sldb_indexes')
	__persistattr__ = ('data', 'default_data')

	def __init__(self, class_id=None, name=None, context=None):
		BaseObject.__init__(self, class_id, context=context)
		self.name = name
		self.default_data = None
		self.sldb_indexes = []

	def create_object(self):
		obj = Object(class_id=self.oid)
		obj.sldb_context = self.sldb_context
		obj.data = self.default_data or {}
		return obj

	def save(self, context=None):
		if context:
			self.sldb_context = context
		if not self.sldb_context:
			raise RuntimeError('No context')
		self.sldb_context.put_class(self)

	def delete(self, context=None):
		if context:
			self.sldb_context = context
		if not self.sldb_context:
			raise RuntimeError('No context')
		self.sldb_context.delete_class(self)


class Object(BaseObject):

	__slots__ = ('class_id', 'created')
	__persistattr__ = ('data', 'created')

	def __init__(self, oid=None, class_id=None, context=None):
		BaseObject.__init__(self, oid, context=context)
		self.class_id = class_id
		self.created = time.time()

	def save(self, context=None):
		if context:
			self.sldb_context = context
		if not self.sldb_context:
			raise RuntimeError('No context')
		self.sldb_context.put_object(self)

	def delete(self, context=None):
		if context:
			self.sldb_context = context
		if not self.sldb_context:
			raise RuntimeError('No context')
		self.sldb_context.delete_object(self)

# vim: encoding=utf8: ff=unix:
