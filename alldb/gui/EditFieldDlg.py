# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-20'


import wx


from _EditFieldDlg import _EditFieldDlg

class EditFieldDlg(_EditFieldDlg):
	def __init__(self, parent, data):
		_EditFieldDlg.__init__(self, parent, -1)

		self._data = data
		self._radios = {
			'str':	self.rb_type_text,
			'bool':	self.rb_type_checkbox,
			'date':	self.rb_type_date,
			'multi':	self.rb_type_multiline
		}

		self.GetSizer().Add(
				self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL), 
				0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 6)

		self.Fit()

		self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)

		self.fill()

	def fill(self):
		data = self._data
		self.tc_name.SetValue(data.get('name') or '')
		self.tc_default.SetValue(data.get('default') or '')
		options = data.get('options') or {}
		self.cb_show_in_title.SetValue(options.get('in_title', False))
		
		ftype = data.get('type') or 'str'
		radio = self._radios.get(ftype)
		if radio:
			radio.SetValue(True)

	def _on_ok(self, evt):
		name = self.tc_name.GetValue().strip()
		if not name:
			dlg = wx.MessageDialog(self, _('Enter name'),
					_('Class'), wx.OK|wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return

		if name in self._data.get('_fields_names', []):
			dlg = wx.MessageDialog(self, _('Field with this name alreaty exists'),
					_('Class'), wx.OK|wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return

		self._data['name'] = name
		self._data['default'] = self.tc_default.GetValue()
		options = self._data.get('options') or {}
		options['in_title'] = self.cb_show_in_title.IsChecked()
		self._data['options'] = options

		for ftype, ctrl in self._radios.iteritems():
			if ctrl.GetValue():
				self._data['type'] = ftype
				break

		self.EndModal(wx.ID_OK)





# vim: encoding=utf8: ff=unix:
