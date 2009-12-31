# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-17'


from sldb import SchemaLessDatabase, Index
import objects



CLASS_IDX_OID = 'IDX_CLASSES'


class Db(SchemaLessDatabase):
	"""docstring for Db"""
	def __init__(self, *args, **kwargs):
		SchemaLessDatabase.__init__(self, *args, **kwargs)
		self.register_class('_OCL', objects.ObjectClass)
		self.register_class('_OBJ', objects.Object)

	def _after_open(self):
		SchemaLessDatabase._after_open(self)
		if CLASS_IDX_OID not in self:
			class_index = Index(CLASS_IDX_OID)
			self.put(class_index)

	def _put_single_object(self, obj):
		if hasattr(obj, 'obj2dump'):
			for subobj in obj.obj2dump():
				if subobj == obj:
					SchemaLessDatabase._put_single_object(self, subobj)
				else:
					self._put_single_object(subobj)
		else:
			SchemaLessDatabase._put_single_object(self, obj)

	@property
	def classes(self):
		class_index = self.get(CLASS_IDX_OID)
		if class_index is None:
			return
		return [self.get(oid)
				for item in class_index.data.itervalues() 
				for oid in item ]

	@property
	def classes_index(self):
		return self.get(CLASS_IDX_OID)

	def get_class_by_name(self, name):
		class_index = self.get(CLASS_IDX_OID)
		if class_index is None:
			return
		return [self.get(oid)
				for item in class_index.data[name]
				for oid in item ]

	def get_objects_by_class(self, class_oid):
		cls = self.get(class_oid)
		objects_index = cls.objects_index
		return self.get_objects_by_index(objects_index)

	def get_objects_by_index(self, index_oid, match_function=None):
		index = self.get(index_oid)
		if not isinstance(index, Index):
			return None
		if match_function:
			items = index.get_matching(match_function)
		else:
			items = index.get_all()
		return self.get(list(items))






# vim: encoding=utf8: ff=unix:
