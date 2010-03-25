# -*- coding: utf-8 -*-

"""
Obiekty alldb
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009'
__version__ = '0.1'
__release__ = '2009-12-17'


import logging
import re
import locale

from . import sldb

_LOG = logging.getLogger(__name__)


class ADObjectClass(sldb.ObjectClass):
	__persistattr__ = sldb.ObjectClass.__persistattr__ + ('title_expr',
			'title_show', 'title_auto', 'fields')

	def __init__(self, class_id=None, name=None, context=None):
		sldb.ObjectClass.__init__(self, class_id, name, context)
		self.title_expr = None
		self.title_show = True
		self.title_auto = True
		self.fields = []

	def gen_auto_title(self):
		title = ' - '.join(('%%(%s)' % field[0])
				for field in self.fields
				if field[3] and field[3].get('in_title', False))
		if not title and self.fields:
			title = '%%(%s)' % self.fields[0][0]
		return title or ''

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

	def get_field(self, field):
		for fld in self.fields:
			if fld[0] == field:
				return fld
		return None


class ADObject(sldb.Object):
	__persistattr__ = sldb.Object.__persistattr__ + ('tags', 'title')

	def __init__(self, oid=None, class_id=None, context=None):
		sldb.Object.__init__(self, oid, class_id, context)
		self.tags = []
		self.title = None

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

	def get_value(self, key):
		if key.startswith('__') and hasattr(self, key[2:]):
			return getattr(self, key[2:])
		return self.data.get(key)

	def get_values(self, keys):
		return ','.join(self.get_value(key) for key in keys)

	def check_for_changes(self, new_data, tags):
		for key, val in new_data.iteritems():
			value = self.data.get(key)
			if value != val and (value or val):
				return True

		return self.tags != tags2str(tags)

	def before_save(self, context=None):
		sldb.Object.before_save(self, context)

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

	def duplicate(self):
		obj = super(ADObject, self).duplicate()
		obj.tags = self.tags[:]
		obj.title = self.title
		return obj


class SearchResult(object):
	"""docstring for SearchResult"""

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
		for field in self.cls.fields:
			fields.append(field[0])
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
		return _('None')
	if value == True:
		return _('True')
	if value == False:
		return _('False')
	return value


# vim: encoding=utf8: ff=unix:
