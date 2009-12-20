# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-17'


from sldb import BaseObject, Index

class ObjectClass(BaseObject):
	def __init__(self, oid=None, name=None):
		BaseObject.__init__(self, oid, cls="_OCL")
		self.name = name
		self.fields = []
		self.indexes_oid = []
		self.objects_index = None

		self._indexes = []
		self._objects_index = Index(name="obj index for " + str(self.name))

	def create_object(self, **kwargs):
		obj = Object(ocls=self.oid, **kwargs)
		for name, ftype, default, options in self.fields:
			obj.data[name] = default
			obj._cls_objects_index = self._objects_index
			obj._cls_indexes = self.indexes_oid
		return obj

	def obj2dump(self):
		yield self._objects_index
		yield self

	def _set_objects(self, objs):
		self._objects = objs

	def _get_objects(self):
		return self._objects
	
	objects = property(_get_objects, _set_objects)

	def _set_indexes(self, idxs):
		self._indexes = idxs

	def _get_indexes(self):
		return self._indexes
	
	indexes = property(_get_indexes, _set_indexes)

	def _before_save(self):
		self.objects_index = self._objects_index.oid
		self.indexes_oid = [ idx.oid for idx in self._indexes ]


class Object(BaseObject):
	def __init__(self, oid=None, ocls=None, title=None):
		BaseObject.__init__(self, oid, cls="_OBJ")
		self.ocls = ocls
		self.title = title
		self.data = {}
		self._cls_objects_index = None
		self._cls_indexes = None

	def obj2dump(self):
		yield self
		if self._cls_objects_index:
			yield self._cls_objects_index

	def _before_save(self):
		if self._cls_objects_index is not None:
			self._cls_objects_index.update(self.oid, self.title)
	



# vim: encoding=utf8: ff=unix:
