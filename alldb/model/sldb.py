# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-17'


from UserList import UserList
from UserDict import IterableUserDict
import bsddb
import cjson
decoder = cjson.decode
encoder = cjson.encode

#import cPickle
#encoder = cPickle.dumps
#decoder = cPickle.loads


class BaseObject(object):
	"""docstring for SimpleObject"""
	def __init__(self, oid=None, cls=None, **kwarg):
		self.oid = oid
		self.cls = cls

	def __repr__(self):
		return '<%s: %r>' % (self.__class__.__name__, self.__dict__)

	def dump(self):
		return dict((
			(key, val) 
			for (key, val) in self.__dict__.iteritems()
			if val and not key.startswith('_')))

	def load(self, data):
		self.__dict__.update(data)


class SimpleObject(BaseObject):
	"""docstring for SimpleObject"""
	def __init__(self, oid=None, cls="_SIM", **kwarg):
		BaseObject.__init__(self, oid, cls, **kwarg)
		self.data = kwarg


class ObjectsList(BaseObject, UserList):
	"""docstring for ObjectsList"""
	def __init__(self, oid=None, name=None):
		BaseObject.__init__(self, oid, '_LST')
		UserList.__init__(self)
		self.name = name


class Index(BaseObject, IterableUserDict):
	"""docstring for Index"""
	def __init__(self, oid=None, name=None):
		BaseObject.__init__(self, oid, '_IDX')
		IterableUserDict.__init__(self)
		self.name = name

	def update(self, oid, new_key, old_key=None):
		self.del_item(oid, old_key)
		self.add_item(new_key, oid)

	def add_item(self, key, oid):
		if key not in self.data:
			self.data[key] = []

		if oid not in self.data[key]:
			self.data[key].append(oid)

	def del_item(self, oid, key=None):
		if key is None:
			for ilist in self.data.itervalues():
				if oid in ilist:
					ilist.remove(oid)
		else:
			ilist = self.data[key]
			if oid in ilist:
				ilist.remove(oid)

	def get_all(self):
		for ilist in self.data.itervalues():
			for item in ilist:
				yield item

	def get_matching(self, match_function):
		for key, ilist in self.data.iteritems():
			if match_function(key):
				for item in ilist:
					yield item


class SchemaLessDatabase(object):
	def __init__(self, filename=None):
		self._filename = filename
		self._registered_classess = {
				'_SIM': SimpleObject,
				'_LST': ObjectsList,
				'_IDX': Index
		}	
		if filename:
			self.open(filename)
		
	def __del__(self):
		self.close()

	def open(self, filename):
		if filename:
			self._filename = filename
		if self._filename:
			self._db = bsddb.hashopen(self._filename, 'c')
			self._after_open()
		else:
			raise Exception('No filename')

	def close(self):
		if self._db:
			self._before_close()
			self._db.close()

	def __getitem__(self, oid):
		if isinstance(oid, (list, tuple)):
			return map(self._get_single_object, oid)
		return self._get_single_object(oid)

	def __setitem__(self, oid, obj):
		obj = self._process_object_before_save(obj)
		self._db[str(oid)] = encoder(obj.dump())
		self._process_object_after_save(obj)

	def __delitem__(self, oid):
		oid = str(oid)
		if self._db.has_key(oid):
			del self._db[oid]

	def __contains__(self, oid):
		return self._db.has_key(oid)

	def put(self, obj):
		if isinstance(obj, (list, tuple)):
			map(self._put_single_object, obj)
		else:
			self._put_single_object(obj)

	def sync(self):
		self._db.sync()

	def register_class(self, cls_name, cls):
		self._registered_classess[cls_name] = cls

	def _get_class(self, cls_name):
		return self._registered_classess.get(cls_name, SimpleObject)

	def _get_single_object(self, oid):
		oid = str(oid)
		if self._db.has_key(oid):
			data = decoder(self._db[oid])
			obj_cls = SimpleObject
			if 'cls' in data:
				obj_cls = self._get_class(data['cls'])
			obj = obj_cls()
			obj.load(data)
			obj = self._process_object_after_load(obj)
			return obj
		return None

	def _process_object_after_load(self, obj):
		return obj

	def _process_object_before_save(self, obj):
		return obj

	def _process_object_after_save(self, obj):
		return obj

	def _after_open(self):
		pass

	def _before_close(self):
		pass

	def _put_single_object(self, obj):
		if not obj.oid:
			obj.oid = self.next_oid
		self[obj.oid] = obj

	@property
	def next_oid(self):
		return self.next_seq('OID')

	def next_seq(self, sequence, begin=10000, step=1):
		seq_name = 'SEQ_' + sequence
		seq = self._db[seq_name] if self._db.has_key(seq_name) else begin
		seq = int(seq) + step
		self._db[seq_name] = str(seq)
		self._db.sync()
		return seq

	def _print_all(self):
		for k, v in self._db.iteritems():
			print k, v




if __name__ == '__main__':
	storage = SchemaLessDatabase('test')

	obj = SimpleObject(storage.next_oid, test=322, val=232)
	obj2 = SimpleObject(slsak=2323)
	storage.put(obj)
	storage.put(obj2)

	obj_list = ObjectsList(storage.next_oid)
	obj_list.append(obj.oid)
	obj_list.append(obj.oid)

	idx = Index()
	idx.add_item('name', obj.oid)
	idx.add_item('name', obj2.oid)
	idx.add_item('key', obj2.oid)

	storage.put(obj_list)
	storage.put(idx)

	storage.sync()

	print storage._print_all()

	print storage[2]
	print storage[23]


# vim: encoding=utf8: ff=unix:
