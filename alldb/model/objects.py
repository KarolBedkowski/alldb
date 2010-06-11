# -*- coding: utf-8 -*-

"""
Obiekty alldb
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-06-11"


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

	def export(self):
		data = self.dump()
		data['oid'] = self.oid
		data['updated'] = self.updated
		return data

	def import_obj(self, data):
		self.restore(data)
		self.oid = data.get('oid')
		self.updated = data.get('updated')


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
		self.changed_fields_names = []

	@property
	def fields_in_list(self):
		if self.title_show:
			yield '__title'
		for field in self.fields:
			if field[3] and field[3].get('in_list'):
				yield field[0]

	@property
	def field_names(self):
		return (field[0] for field in self.fields)

	@property
	def nonblobs_fields(self):
		return (field[0] for field in self.fields if field[1] != 'image')

	@property
	def blob_fields(self):
		return (field[0] for field in self.fields if field[1] == 'image')

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

	def get_field_options(self, field):
		for fld in self.fields:
			if fld[0] == field:
				return fld[3]
		return None

	def update_field_options(self, field, options):
		for fld in self.fields:
			if fld[0] == field:
				fld[3] = options

	def export(self):
		exp = BaseObject.export(self)
		exp['name'] = self.name
		return exp

	def import_obj(self, data):
		BaseObject.import_obj(self, data)
		self.name = data.get('name')


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

	def update_fields_names(self, changes):
		new_data = {}
		for old_name, new_name in changes:
			if old_name in self.data:
				new_data[new_name] = self.data.pop(old_name)
		new_data.update(self.data)
		self.data = new_data


class SearchResult(object):
	""" SearchResult"""

	def __init__(self):
		self.cls = None
		self.reset()

	def reset(self):
		self.tags = {}
		self._items = {}
		self.filtered_items = []
		self.current_sorting_col = 0
		self._last_filter = None
		self._values_cache = {}		# field->(value->[items])

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

	def get_values_for_field(self, field):
		return self._values_cache[field]

	def get_filter_for_field(self, field):
		return dict((value, len(items)) for value, items
				in self._values_cache[field].iteritems())

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

	def update_item(self, item):
		self._items[item.oid] = item
		for field, valuesdict in self._values_cache.iteritems():
			new_value = item.data.get(field)
			if new_value in valuesdict and item in valuesdict[new_value]:
				# without changes
				continue
			for itemlist in valuesdict.itervalues():
				idx = [idx for idx, itm in enumerate(itemlist)
						if itm.oid == item.oid]
				if idx:
					del itemlist[idx[0]]
					break
			values_to_del = [val for val, itemlist in valuesdict.iteritems()
					if len(itemlist) == 0]
			for val in values_to_del:
				del valuesdict[val]
			itemlist = valuesdict.get(new_value, [])
			itemlist.append(item)
			valuesdict[new_value] = itemlist
		for tag in item.tags:
			self.tags[tag] = self.tags.get(tag, 0) + 1

	def del_item(self, item):
		for valuesdict in self._values_cache.itervalues():
			for itemlist in valuesdict.itervalues():
				idx = [idx for idx, itm in enumerate(itemlist)
						if itm.oid == item.oid]
				if idx:
					del itemlist[idx[0]]
					break
			values_to_del = [val for val, itemlist in valuesdict.iteritems()
					if len(itemlist) == 0]
			for val in values_to_del:
				del valuesdict[val]

	def _do_sort_items(self):
		current_sorting_col = abs(self.current_sorting_col) - 1
		if current_sorting_col >= 0:
			reverse = self.current_sorting_col < 0
			func = lambda x: x[1][current_sorting_col]
			self.filtered_items.sort(cmp=locale.strcoll, key=func, reverse=reverse)
		return self.filtered_items

	def _update_tags(self):
		tags = {}
		fields = list(self.cls.nonblobs_fields)
		values = dict((fname, dict()) for fname in fields)
		for item in self._items.itervalues():
			for tag in item.tags:
				tags[tag] = tags.get(tag, 0) + 1
			for fname in fields:
				value = item.data.get(fname)
				nlist = values[fname].get(value, [])
				nlist.append(item)
				values[fname][value] = nlist
		self.tags = tags
		self._values_cache = values


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
	return unicode(value).replace('\n', '')


def get_field_name_human(field):
	if field == '__title':
		return _('Title')
	elif field.startswith('__'):
		field = field[2:]
	return field.capitalize()


# vim: encoding=utf8: ff=unix:
