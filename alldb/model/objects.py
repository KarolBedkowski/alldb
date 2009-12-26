# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-17'


import re

from sldb import BaseObject, Index

class ObjectClass(BaseObject):
	def __init__(self, oid=None, name=None, context=None):
		BaseObject.__init__(self, oid, cls="_OCL", context=context)
		self.name = name
		self.fields = []
		self.indexes_oid = []
		self.objects_index = None
		self.title_expr = None

		self._indexes = []
		self._objects_index = Index(name="obj index for " + str(self.name))

	def create_object(self, **kwargs):
		obj = Object(ocls=self.oid, **kwargs)
		obj._context = self._context
		obj._cls_objects_index = self._objects_index
		obj._cls_indexes = self.indexes_oid
		for name, ftype, default, options in self.fields:
			obj.data[name] = default
		return obj

	def obj2dump(self):
		yield self._objects_index
		yield self

	def _set_indexes(self, idxs):
		self._indexes = idxs

	def _get_indexes(self):
		return self._indexes
	
	indexes = property(_get_indexes, _set_indexes)

	@property
	def objects(self):
		return self._context.get_objects_by_index(self.objects_index)

	def _before_save(self):
		self.objects_index = self._objects_index.oid
		self.indexes_oid = [ idx.oid for idx in self._indexes ]

	def _after_load(self):
		indexes_oid = self.indexes_oid
		if indexes_oid:
			self.indexes = self._context.get(indexes_oid)
		if self.objects_index:
			self._objects_index = self._context.get(self.objects_index)

	def _after_save(self):
		class_index = self._context.classes_index
		class_index.update(self.oid, self.name)
		class_index.save()



class Object(BaseObject):
	def __init__(self, oid=None, ocls=None, context=None, title=None):
		BaseObject.__init__(self, oid, cls="_OBJ", context=context)
		self.ocls = ocls
		self.title = title
		self.data = {}
		self._cls_objects_index = None
		self._cls_indexes = None
		self.tags = []

	def obj2dump(self):
		yield self
		if self._cls_objects_index:
			yield self._cls_objects_index

	def _before_save(self):
		cls = self._context.get(self.ocls)
		title_expr = cls.title_expr
		if title_expr:
			repl = lambda x: ("%%" + x.group(0)[1:].strip()+"s ")
			title_expr = re.sub('(%\([\w ]+\))', repl, title_expr)
			repl = lambda x: ('%%(%s)s ' % x.group(0)[1:].strip())
			title_expr = re.sub('(%[\w ]+)', repl, title_expr)
			print title_expr
			self.title = title_expr % (self.data)
		if not self.title:
			self.title = ':'.join(self.data.items()[0])

		if self._cls_objects_index is not None:
			self._cls_objects_index.update(self.oid, self.title)

	def set_tags(self, tagstr):
		if tagstr.strip():
			self.tags = [ tag.strip() for tag in tagstr.split(',') ]
		else:
			self.tags = []

	def has_tags(self, taglist):
		for tag in taglist:
			if tag in self.tags:
				return True
		return False

	@property
	def tags_str(self):
		return ', '.join(self.tags)



# vim: encoding=utf8: ff=unix:
