# -*- coding: utf-8 -*-

"""
Obiekty alldb
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2009-2010'
__version__ = '0.1'
__release__ = '2009-12-17'


import time
import logging
import re
import locale


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

	def duplicate(self):
		obj = self.__class__()
		obj.sldb_context = self.sldb_context
		obj.data = self.data.copy()
		return obj


class ADObjectClass(BaseObject):
	__persistattr__ = ('data', 'default_data', 'title_expr', 'title_show',
			'title_auto', 'fields')
	__slots__ = ('name', 'default_data', 'title_expr', 'title_show', 'title_auto',
			'fields')

	def __init__(self, class_id=None, name=None, context=None):
		BaseObject.__init__(self, class_id, context=context)
		self.name = name
		self.default_data = None
		self.title_expr = None
		self.title_show = True
		self.title_auto = True
		self.fields = []

	@property
	def fields_in_list(self):
		fields = []
		if self.title_show:
			fields.append('__title')
		for field in self.fields:
			if field[3] and field[3].get('in_list'):
				fields.append(field[0])
		return fields

	def create_object(self):
		obj = ADObject(class_id=self.oid)
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

	def gen_auto_title(self):
		title = ' - '.join(('%%(%s)' % field[0])
				for field in self.fields
				if field[3] and field[3].get('in_title', False))
		if not title and self.fields:
			title = '%%(%s)' % self.fields[0][0]
		return title or ''

	def get_field(self, field):
		for fld in self.fields:
			if fld[0] == field:
				return fld
		return None


class ADObject(BaseObject):
	__persistattr__ = ('data', 'created', 'tags', 'title')
	__slots__ = ('class_id', 'created', 'tags', 'title', 'blobs')

	def __init__(self, oid=None, class_id=None, context=None):
		BaseObject.__init__(self, oid, context=context)
		self.class_id = class_id
		self.created = time.time()
		self.tags = []
		self.title = None
		self.blobs = {}

	@property
	def tags_str(self):
		return ', '.join(self.tags)

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

	def duplicate(self):
		obj = super(ADObject, self).duplicate()
		obj.class_id = self.class_id
		obj.tags = self.tags[:]
		obj.title = self.title
		return obj

	def set_tags(self, tagstr):
		self.tags = tags2str(tagstr)

	def has_tags(self, taglist):
		for tag in taglist:
			if tag in self.tags:
				return True
		return False

	def get_value(self, key):
		if key.startswith('__') and hasattr(self, key[2:]):
			return getattr(self, key[2:])
		return self.data.get(key)

	def get_values(self, keys):
		return ','.join(self.get_value(key) for key in keys)

	def get_blob(self, field):
		return self.sldb_context.get_blob(self.oid, field)

	def check_for_changes(self, new_data, tags, blobs):
		for key, val in new_data.iteritems():
			value = self.data.get(key)
			if value != val and (value or val):
				return True
		for field, blob in blobs.iteritems():
			if (blob is None and self.data.get(field, 0) != 0) or \
					(blob and len(blob) != self.data.get(field)):
				return True
		return self.tags != tags2str(tags)

	def before_save(self, context=None):
		BaseObject.before_save(self, context)
		cls = self.sldb_context.get_class(self.class_id)
		title_expr = cls.title_expr

		if title_expr:
			repl = lambda x: ("%" + x.group(0)[1:].strip() + "s ")
			title_expr = re.sub('(%\([\w ]+\))', repl, title_expr)
			repl = lambda x: ('%(%s)s ' % x.group(0)[1:].strip())
			title_expr = re.sub('(%[\w ]+)', repl, title_expr)
			self.title = title_expr % (self.data)
		if not self.title:
			self.title = ':'.join(self.data.items()[0])
		for name, ftype, _defautl, _options in cls.fields:
			if ftype == 'image':
				if self.data[name] == 0:
					self.blobs[name] = None


class SearchResult(object):
	""" SearchResult"""

	def __init__(self):
		self.cls = None
		self.reset()

	@property
	def items(self):
		self_items = self._items
		return (self_items[oid] for oid, _data in self.filtered_items)

	@property
	def fields(self):
		fields = []
		for name, ftype, _default, _options in self.cls.fields:
			if ftype != 'image':
				fields.append(name)
		fields.sort()
		fields.insert(0, _('Tags'))
		return fields

	def get_filter_for_field(self, field):
		filters = {}
		for item in self._items.itervalues():
			val = item.data.get(field)
			filters[val] = filters.get(val, 0) + 1
		return filters

	def reset(self):
		self.tags = {}
		self._items = {}
		self.filtered_items = []
		self.current_sorting_col = 0
		self._last_filter = None

	def set_class(self, cls):
		self.cls = cls
		self.reset()

	def set_items(self, items):
		self._items = dict((item.oid, item) for item in items)
		self._update_tags()

	def filter_items(self, name_filter, tags, cols, key):
		if (name_filter, tags, cols, key) == self._last_filter:
			return self.filtered_items

		_LOG.debug('filter_items(%r, %r, %r)', name_filter, tags, cols)
		self._last_filter = (name_filter, tags, cols, key)
		items = self._items.itervalues()
		if name_filter:
			name_filter = name_filter.lower()

			def check(item):
				for field in cols:
					val = item.get_value(field)
					if val and val.lower().find(name_filter) > -1:
						return True
				return False
			items = (item for item in items if check(item))

		if tags:
			if key == _('Tags'):
				items = (item for item in items if item.has_tags(tags))
			else:
				items = (item for item in items if item.data.get(key) in tags)

		self.filtered_items = [(item.oid, [item.get_value(col) for col in cols])
				for item in items]
		self._do_sort_items()
		return self.filtered_items

	def sort_items(self, col):
		if abs(self.current_sorting_col) == col:
			self.current_sorting_col = - self.current_sorting_col
		else:
			self.current_sorting_col = max(col, 1)
		return self._do_sort_items()

	def _do_sort_items(self):
		current_sorting_col = abs(self.current_sorting_col) - 1
		if current_sorting_col >= 0:
			reverse = self.current_sorting_col < 0
			func = lambda x: x[1][current_sorting_col]
			self.filtered_items.sort(cmp=locale.strcoll, key=func, reverse=reverse)
		return self.filtered_items

	def _update_tags(self):
		tags = {}
		for item in self._items.itervalues():
			for tag in item.tags:
				tags[tag] = tags.get(tag, 0) + 1
		self.tags = tags


def tags2str(tagstr):
	tagstr = tagstr.strip() if tagstr else ''
	if tagstr:
		return sorted(tag.strip() for tag in tagstr.split(','))
	return []


def get_field_value_human(value):
	if value is None:
		return ''
	if value == True:
		return _('True')
	if value == False:
		return _('False')
	return value


# vim: encoding=utf8: ff=unix:
