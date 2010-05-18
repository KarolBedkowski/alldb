# -*- coding: utf-8 -*-

"""
"""
from __future__ import with_statement

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-05-14"


import wx


class Field(object):
	field_type = None
	result_type = 'value'
	_on_change_event = wx.EVT_TEXT

	def __init__(self, parent, name, options, default, result_obj):
		self.name = name
		self.options = options
		self.result_obj = result_obj
		self.default = default
		self._panel = None
		self._widget = self._create_widget(parent, options, result_obj)

	@property
	def panel(self):
		return self._panel or self._widget

	@property
	def widget(self):
		return self._widget

	def _get_value(self):
		return self._widget_get_value()

	def _set_value(self, value):
		return self._widget_set_value(value)

	def _del_value(self):
		self._widget_del_value()

	value = property(_get_value, _set_value, _del_value,
			"Access to widget value")

	def bind(self, event, method):
		self.widget.Bind(event, method)

	def bind_on_change(self, method):
		self.widget.Bind(self._on_change_event, method)

	def set_object(self, obj):
		self._widget_set_value(obj.data.get(self.name))

	def clear(self):
		self._widget_del_value()

	def _create_widget(self, parent, options, result_obj):
		return None

	def _widget_get_value(self):
		return self._widget.GetValue()

	def _widget_set_value(self, value):
		self._widget.SetValue(unicode(value or ''))

	def _widget_del_value(self):
		self._widget_set_value(self.default)



# vim: encoding=utf8: ff=unix:
