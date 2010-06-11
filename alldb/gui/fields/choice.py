# -*- coding: utf-8 -*-

"""
"""
from __future__ import with_statement

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-06-11"


import wx

from alldb.gui.dlg_edit_values import DlgEditValues
from alldb.gui.fields._field import Field


class ChoiceField(Field):
	field_type = 'choice'
	_on_change_event = wx.EVT_CHOICE

	def _create_widget(self, parent, options, _result_obj):
		values = options.get('values') or []
		self._values = values
		ctrl =  wx.Choice(parent, -1, choices=values)
		btn_define = wx.Button(parent, -1, _("Define"))
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(ctrl, 1, wx.EXPAND)
		sizer.Add((6, 6))
		sizer.Add(btn_define)
		self._panel = sizer
		btn_define.Bind(wx.EVT_BUTTON, self._on_btn_define)
		return ctrl

	def _widget_set_value(self, value):
		self._widget.Clear()
		if '' not in self._values:
			self._widget.Append('')
		for val in sorted(self._values):
			self._widget.Append(val)
		if value:
			if value not in self._values:
				self._widget.Append(value)
			self._widget.SetStringSelection(value)
		else:
			self._widget.SetSelection(-1)

	def _widget_get_value(self):
		return self._widget.GetStringSelection()

	def _on_btn_define(self, evt):
		cls = self.result_obj.cls
		options = cls.get_field_options(self.name)
		dlg = DlgEditValues(self._widget, options)
		if dlg.ShowModal() == wx.ID_OK:
			cls.update_field_options(self.name, options)
			cls.save()
			self._options = options
			self._values = options['values']
			val = self._widget_get_value()
			self._widget_set_value(val)
		dlg.Destroy()


# vim: encoding=utf8: ff=unix:
