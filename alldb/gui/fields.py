# -*- coding: utf-8 -*-

"""
"""
from __future__ import with_statement

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (C) Karol Będkowski, 2009-2010"
__version__ = "2010-05-06"


import os.path
import time
import cStringIO

import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.newevent
import wx.lib.imagebrowser as imgbr
import wx.gizmos as gizmos
from wx.lib import masked

from alldb.gui.dlg_select_tags import DlgSelectTags
from alldb.libs.textctrlautocomplete import TextCtrlAutoComplete


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


class Field:
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


class SimpleTextField(Field):
	field_type = 'text'

	def _create_widget(self, parent, options, result_obj):
		return MyTextCtrlAutoComplete(parent, result_obj, self.name)


FieldsFactory.register_field_type(SimpleTextField)


class MultilineTextField(Field):
	field_type = 'multi'

	def _create_widget(self, parent, options, result_obj):
		return MyTextCtrlAutoComplete(parent, result_obj, self.name,
				size=(-1, 100), style=wx.TE_MULTILINE)


FieldsFactory.register_field_type(MultilineTextField)


class BooleanField(Field):
	field_type = 'bool'
	_on_change_event = wx.EVT_CHECKBOX

	def _create_widget(self, parent, options, result_obj):
		return wx.CheckBox(parent, -1)

	def _widget_set_value(self, value):
		self._widget.SetValue(bool(value))


FieldsFactory.register_field_type(BooleanField)


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


FieldsFactory.register_field_type(DateField)


class ListField(Field):
	field_type = 'list'

	def _create_widget(self, parent, options, result_obj):
		return gizmos.EditableListBox(self, -1)

	def _widget_set_value(self, value):
		self._widget.SetStrings(value or '')


FieldsFactory.register_field_type(ListField)


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


FieldsFactory.register_field_type(ChoiceField)


class ImageField(Field):
	field_type = 'image'
	result_type = 'blob'
	
	def __init__(self, parent, name, options, default, result_obj):
		Field.__init__(self, parent, name, options, default, result_obj)
		self._blob = None

	def _create_widget(self, parent, options, result_obj):
		width_height = (int(options.get('width', 100)),
				int(options.get('height', 100)))
		ctrl = wx.StaticBitmap(parent, -1, size=width_height)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(ctrl, 1, wx.EXPAND)
		box.Add((6, 6))
		bbox = wx.FlexGridSizer(3, 1, 6, 6)
		bbox.AddGrowableRow(0)
		bbox.Add((1, 1), 1)
		btn = wx.Button(parent, -1, _('Select'))
		btn.Bind(wx.EVT_BUTTON, self._on_btn_image_select)
		bbox.Add(btn)
		btn = wx.Button(parent, -1, _('Clear'))
		btn.Bind(wx.EVT_BUTTON, self._on_btn_image_clear)
		bbox.Add(btn)
		box.Add(bbox, 0, wx.EXPAND)
		self._panel = box
		return ctrl

	def set_object(self, obj):
		self._blob = obj.get_blob(self.name)
		self._widget_set_value(self._blob)

	def _widget_get_value(self):
		return self._blob

	def _widget_set_value(self, value):
		img = None
		if value:
			img = wx.ImageFromStream(cStringIO.StringIO(value))
		if img is None or not img.IsOk():
			img = wx.EmptyImage(1, 1)
			self._widget.Show(False)
		else:
			bmp = img.ConvertToBitmap()
			self._widget.SetBitmap(bmp)
			self._widget.Show(True)
			self._widget.SetSize((img.GetWidth(), img.GetHeight()))
			self._widget.GetParent().Layout()
			self._widget.GetParent().Refresh()

	def _widget_del_value(self):
		self._widget_set_value(None)

	def _on_btn_image_select(self, evt):
		dlg = imgbr.ImageDialog(self._widget)
		if dlg.ShowModal() == wx.ID_OK:
			filename = dlg.GetFile()
			data = None
			img = wx.Image(filename)
			if img:
				opt = self.options
				width, height = opt.get('width'), opt.get('height')
				if width and height:
					width, height = int(width), int(height)
					if width < img.GetWidth() or height < img.GetHeight():
						scale = min(float(width) / img.GetWidth(),
								float(height) / img.GetHeight())
						img = img.Scale(int(img.GetWidth() * scale),
								int(img.GetHeight() * scale))
				output = cStringIO.StringIO()
				img.SaveStream(output, wx.BITMAP_TYPE_JPEG)
				self._blob = output.getvalue()
				self._widget_set_value(self._blob)
		dlg.Destroy()

	def _on_btn_image_clear(self, evt):
		self._blob = None
		self._widget_set_value(None)


FieldsFactory.register_field_type(ImageField)


class NumericField(Field):
	field_type = 'numeric'

	def _create_widget(self, parent, options, result_obj):
		return masked.NumCtrl(self, -1, groupDigits=False, allowNone=True)


FieldsFactory.register_field_type(NumericField)



# vim: encoding=utf8: ff=unix:
