# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-17'


import re
import time

from sldb import BaseObject, Index

class ObjectClass(BaseObject):
	def __init__(self, oid=None, name=None, context=None):
		BaseObject.__init__(self, oid, cls="_OCL", context=context)
		self.name = name
		self.fields = []
		self.indexes_oid = []
		self.objects_index = None
		self.title_expr = None
		self.title_auto = True
		self.title_show = True

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

	@property
	def fields_in_list(self):
		fields = []
		if self.title_show:
			fields.append('__title')
		for field in self.fields:
			if field[3] and field[3].get('in_title'):
				fields.append(field[0])
		return fields

	def filter_objects(self, name_filter, tags, cols=None):
		items = self.objects
		if name_filter:
			name_filter = name_filter.lower()
			fields2check = self.fields_in_list
			def check(item):
				for field in fields2check:
					val = item.get_value(field)
					if val and val.lower().find(name_filter) > -1:
						return True
				return False
			items = ( item for item in items if check(item) )

		if tags:
			items = ( item for item in items if item.has_tags(tags) )

		if cols:
			items = [ (item.oid, [ item.get_value(col) for col in cols ]) for item in items ]
		else:
			if self.title_show:
				items = [ (item.oid, [item.title]) for item in items ]
			else:
				items = [ (item.oid, 
	 					[ '='.join((key, str(val))) for key, val in item.data.iteritems() ])
						for item in items ]

		return items

	def get_object_info(self, oid, cols=None):
		item = self._context.get(oid)
		if cols:
			item = (item.oid, [ item.get_value(col) for col in cols ])
		else:
			if self.title_show:
				item = (item.oid, [item.title])
			else:
				item = (item.oid, [ '='.join((key, str(val))) for key, val in item.data.iteritems() ])

		return item

	def get_all_items_tags(self):
		tags = {}
		for item in self.objects:
			for tag in item.tags:
				tags[tag] = tags.get(tag, 0) + 1
		return tags

	def gen_auto_title(self):
		title = ' - '.join([('%%(%s)'%field[0])
				for field in self.fields
				if field[3] and field[3].get('in_title', False) ])
		if not title and self.fields:
			title = '%%(%s)' % self.fields[0][0]
		self.title = title or ''
		return self.title

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
		self.date_created = None
		self.date_modified = None

	def get_value(self, key):
		if key.startswith('__'):
			return self.__dict__.get(key[2:])
		return self.data.get(key)

	def get_values(self, keys):
		return ','.join((self.get_value(key) for key in keys ))

	def obj2dump(self):
		yield self
		if self._cls_objects_index:
			yield self._cls_objects_index

	def _before_save(self):
		if not self.date_created:
			self.date_created = time.time()

		self.date_modified = time.time()

		cls = self._context.get(self.ocls)
		title_expr = cls.title_expr
		if title_expr:
			repl = lambda x: ("%" + x.group(0)[1:].strip()+"s ")
			title_expr = re.sub('(%\([\w ]+\))', repl, title_expr)
			repl = lambda x: ('%(%s)s ' % x.group(0)[1:].strip())
			title_expr = re.sub('(%[\w ]+)', repl, title_expr)
			self.title = title_expr % (self.data)
		if not self.title:
			self.title = ':'.join(self.data.items()[0])

		if self._cls_objects_index is None:
			cls = self._context.get(self.ocls)
			self._cls_objects_index = cls._objects_index
		self._cls_objects_index.update(self.oid, self.title)

	def _before_delete(self):
		if self._cls_objects_index is not None:
			self._cls_objects_index.del_item(self.oid)
			self._cls_objects_index.save()

	def set_tags(self, tagstr):
		self.tags = tags2str(tagstr)

	def has_tags(self, taglist):
		for tag in taglist:
			if tag in self.tags:
				return True
		return False

	@property
	def tags_str(self):
		return ', '.join(self.tags)

	def duplicate(self):
		newobj = self.__class__(ocls=self.ocls, context=self._context)
		newobj.title = self.title
		newobj.data = self.data.copy()
		newobj._cls_objects_index = self._cls_objects_index
		newobj._cls_indexes = self._cls_indexes
		newobj.tags = list(self.tags)
		newobj.date_created = None
		newobj.date_modified = None
		return newobj

	def check_for_changes(self, new_data, tags):
		for key, val in new_data.iteritems():
			if self.data.get(key) != val:
				return True

		return self.tags != tags2str(tags)


def tags2str(tagstr):
	tagstr = tagstr.strip() if tagstr else ''
	if tagstr:
		return sorted(( tag.strip() for tag in tagstr.split(',') ))
	return []



# vim: encoding=utf8: ff=unix:
