# -*- coding: utf-8 -*-

"""
"""
from __future__ import with_statement

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-05-14"


import cStringIO

import wx
import wx.lib.newevent
import wx.gizmos as gizmos
from wx.lib import masked

from alldb.libs.textctrlautocomplete import TextCtrlAutoComplete

from alldb.gui.fields._field import Field


class MyTextCtrlAutoComplete(TextCtrlAutoComplete):
	def __init__(self, parent, result, field_name, *args, **kwargs):
		TextCtrlAutoComplete.__init__(self, parent, choices=[''], *args,
				**kwargs)
		self._entryCallback = self._entry_callback
		self._result = result
		self._field_name = field_name

	def SetValue(self, value):
		self.ChangeValue(value)

	def _entry_callback(self):
		text = self.GetValue().lower()
		all_choices = self._result.get_values_for_field(self._field_name)
		choices = [choice or '' for choice in all_choices
				if self._match(text, choice)]
		if choices != self._choices:
			self.SetChoices(choices)

	def _match(self, text, choice):
		return (choice or '').lower().startswith(text)


class SimpleTextField(Field):
	field_type = 'text'

	def _create_widget(self, parent, options, result_obj):
		return MyTextCtrlAutoComplete(parent, result_obj, self.name)


class MultilineTextField(Field):
	field_type = 'multi'

	def _create_widget(self, parent, options, result_obj):
		return MyTextCtrlAutoComplete(parent, result_obj, self.name,
				size=(-1, 100), style=wx.TE_MULTILINE)


class BooleanField(Field):
	field_type = 'bool'
	_on_change_event = wx.EVT_CHECKBOX

	def _create_widget(self, parent, options, result_obj):
		return wx.CheckBox(parent, -1)

	def _widget_set_value(self, value):
		self._widget.SetValue(bool(value))


class DateField(Field):
	field_type = 'date'

	def _create_widget(self, parent, options, result_obj):
		return wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN | \
				wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)

	def _widget_set_value(self, value):
		date = wx.DateTime()
		if date:
			try:
				date.ParseDate(value)
			except Exception, err:
				print err
		self._widget.SetValue(date)

	def _widget_get_value(self):
		wxdate = self.self._widget.GetValue()
		return wxdate.Format() if wxdate else None


class ListField(Field):
	field_type = 'list'

	def _create_widget(self, parent, options, result_obj):
		return gizmos.EditableListBox(self, -1)

	def _widget_set_value(self, value):
		self._widget.SetStrings(value or '')


class ChoiceField(Field):
	field_type = 'choice'
	_on_change_event = wx.EVT_CHOICE

	def _create_widget(self, parent, options, result_obj):
		values = options.get('values') or []
		return wx.Choice(self, -1, choices=values)

	def _widget_set_value(self, value):
		if value:
			self._widget.SetStringSelection(value)
		else:
			self._widget.SetSelection(-1)


class NumericField(Field):
	field_type = 'numeric'

	def _create_widget(self, parent, options, result_obj):
		return masked.NumCtrl(self, -1, groupDigits=False, allowNone=True)


# vim: encoding=utf8: ff=unix:
