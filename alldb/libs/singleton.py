
class Singleton(object):
	def __new__(cls, *args, **kwds):
		instance = cls.__dict__.get('__instance__')
		if instance is None:
			instance = object.__new__(cls)
			instance._init__(*args, **kwds)
			cls.__instance__ = instance
		return instance

	def _init__(self, *args, **kwds):
		pass

