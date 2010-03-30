# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009'
__version__ = '0.1'
__release__ = '2009-12-20'


import wx
from wx import xrc

from alldb.libs import wxresources
from alldb.gui.dialogs import message_boxes as msgbox

from .dlg_edit_values import DlgEditValues


class DlgEditField(object):
	def __init__(self, parent, data):
		self.res = wxresources.load_xrc_resource('alldb.xrc')
		self._load_controls(parent)
		self._create_bindings()
		self._setup(data)

	def run(self):
		res = self.wnd.ShowModal() == wx.ID_OK
		self.wnd.Destroy()
		return res

	def _load_controls(self, parent):
		self.wnd = self.res.LoadDialog(parent, 'dlg_edit_field')
		assert self.wnd is not None
		self.rb_type_text = xrc.XRCCTRL(self.wnd, 'rb_type_text')
		self.rb_type_checkbox = xrc.XRCCTRL(self.wnd, 'rb_type_checkbox')
		self.rb_type_date = xrc.XRCCTRL(self.wnd, 'rb_type_date')
		self.rb_type_multiline = xrc.XRCCTRL(self.wnd, 'rb_type_multiline')
		self.rb_type_list = xrc.XRCCTRL(self.wnd, 'rb_type_list')
		self.rb_type_choice = xrc.XRCCTRL(self.wnd, 'rb_type_choice')
		self.rb_type_image = xrc.XRCCTRL(self.wnd, 'rb_type_image')
		self.tc_name = xrc.XRCCTRL(self.wnd, 'tc_name')
		self.tc_default = xrc.XRCCTRL(self.wnd, 'tc_default')
		self.cb_show_in_title = xrc.XRCCTRL(self.wnd, 'cb_show_in_title')
		self.cb_show_in_list = xrc.XRCCTRL(self.wnd, 'cb_show_in_list')
		self.btn_values = xrc.XRCCTRL(self.wnd, 'btn_values')
		panel = xrc.XRCCTRL(self.wnd, 'panel_tc_width')
		self._tc_width = self._create_tc_number(panel)
		panel = xrc.XRCCTRL(self.wnd, 'panel_tc_height')
		self._tc_height = self._create_tc_number(panel)

		self._radios = {
			'str': self.rb_type_text,
			'bool': self.rb_type_checkbox,
			'date': self.rb_type_date,
			'multi': self.rb_type_multiline,
			'list': self.rb_type_list,
			'choice': self.rb_type_choice,
			'image': self.rb_type_image, }

	def _create_bindings(self):
		wnd = self.wnd
		wnd.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
		wnd.Bind(wx.EVT_BUTTON, self._on_btn_values, self.btn_values)
		for widget in self._radios.itervalues():
			wnd.Bind(wx.EVT_RADIOBUTTON, self._on_rb_type_choice, widget)

	def _setup(self, data):
		if not data.get('options'):
			data['options'] = {}
		self._data = data
		self.tc_name.SetValue(data.get('name') or '')
		self.tc_default.SetValue(data.get('default') or '')
		options = data.get('options') or {}
		self.cb_show_in_title.SetValue(options.get('in_title', False))
		self.cb_show_in_list.SetValue(options.get('in_list', False))
		self._tc_width.SetValue(str(options.get('width', '')))
		self._tc_height.SetValue(str(options.get('height', '')))

		ftype = data.get('type') or 'str'
		radio = self._radios.get(ftype)
		if radio:
			radio.SetValue(True)
		self._on_rb_type_choice(None)

	def _create_tc_number(self, panel):
		tc = wx.TextCtrl(panel, -1)
		box = wx.BoxSizer(wx.VERTICAL)
		box.Add(tc, 1, wx.EXPAND)
		panel.SetSizerAndFit(box)
		return tc

	def _on_ok(self, evt):
		name = self.tc_name.GetValue().strip()
		if not name:
			msgbox.message_box_error_ex(self.wnd, _('Cannot add this field'),
					_('Name field is required.\nPlease enter name for field.'))
			return
		if name in self._data.get('_fields_names', []):
			msgbox.message_box_error_ex(self.wnd, _('Cannot add this field'),
					_('Field with this name already exists.\nPlease enter other name.'))
			return

		for ftype, ctrl in self._radios.iteritems():
			if ctrl.GetValue():
				self._data['type'] = ftype
				break

		blob = self._data['type'] == 'image'
		self._data['name'] = name
		self._data['default'] = None if blob else self.tc_default.GetValue()
		options = self._data.get('options') or {}
		options['in_title'] = self.cb_show_in_title.IsChecked() and not blob
		options['in_list'] = self.cb_show_in_list.IsChecked() and not blob
		if blob:
			options['width'] = self._tc_width.GetValue()
			options['height'] = self._tc_height.GetValue()
		self._data['options'] = options
		self.wnd.EndModal(wx.ID_OK)

	def _on_rb_type_choice(self, event):
		type_choice = self.rb_type_choice.GetValue()
		self.btn_values.Enable(type_choice)
		type_image = self.rb_type_image.GetValue()
		self.tc_default.Enable(not type_image)
		self.cb_show_in_list.Enable(not type_image)
		self.cb_show_in_title.Enable(not type_image)
		self._tc_width.Enable(type_image)
		self._tc_height.Enable(type_image)

	def _on_btn_values(self, event):
		values = self._data['options'].get('values')
		data = dict(values=values)
		dlg = DlgEditValues(self.wnd, data)
		if dlg.ShowModal() == wx.ID_OK:
			self._data['options']['values'] = data['values']
		dlg.Destroy()


# vim: encoding=utf8: ff=unix:
