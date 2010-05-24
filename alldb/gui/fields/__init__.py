# -*- coding: utf-8 -*-

"""
"""
from __future__ import with_statement

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-05-24"


import imp
import pkgutil

from alldb.gui.fields._field import Field

from . import simple
from . import image


class FieldsFactory(object):
	_fields_types = {}

	@classmethod
	def register_field_type(cls, field_class):
		cls._fields_types[field_class.field_type] = field_class

	@classmethod
	def get_class(cls, type_name):
		field_class = cls._fields_types.get(type_name)
		if not field_class:
			field_class = cls._fields_types.get('text')
		return field_class


def import_fields():
#	for _imp, name, _ispkg in pkgutil.iter_modules(__path__):
#		if name.startswith('_'):
#			continue
#		fp, pathname, description = imp.find_module(name, __path__)
#		plug = imp.load_module(name, fp, pathname, description)
	for plugclass in Field.__subclasses__():
		FieldsFactory.register_field_type(plugclass)


import_fields()


# vim: encoding=utf8: ff=unix:
