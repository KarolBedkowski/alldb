# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-20'


import wx

from _EditClassesDlg import _EditClassesDlg
from EditFieldDlg	import EditFieldDlg


class EditClassesDlg(_EditClassesDlg):
	def __init__(self, parent, cls, cls_names):
		_EditClassesDlg.__init__(self, None, -1)
		self._cls = cls
		self._cls_names = cls_names

		self.GetSizer().Add(
				self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL), 
				0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 6)

		self.Fit()

		self.lc_fields.InsertColumn(0, _('No'))
		self.lc_fields.InsertColumn(1, _('Name'))
		self.lc_fields.InsertColumn(2, _('Type'))
		self.lc_fields.InsertColumn(3, _('Default value'))
		self.lc_fields.InsertColumn(4, _('Options'))

		self.show_class(cls)
		self._set_buttons_status()

		self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
		self.Centre(wx.BOTH)

	def show_class(self, cls):
		self.tc_name.SetValue(str(cls.name or ''))
		self.tc_title.SetValue(str(cls.title_expr or ''))
		self._refresh_list(cls)
		self.show_title(cls)

	def show_title(self, cls):
		if cls.title_auto:
			self.tc_title.Enable(True)
			self.cb_title_auto.SetValue(cls.title_auto)
			self.tc_title.Enable(False)
		self.tc_title.Enable(not cls.title_auto)

	def _refresh_list(self, cls):
		self.lc_fields.DeleteAllItems()
		for no, (name, ftype, default, options) in enumerate(cls.fields):
			self.lc_fields.InsertStringItem(no, str(no+1))
			self.lc_fields.SetStringItem(no, 1, str(name))
			self.lc_fields.SetStringItem(no, 2, str(ftype))
			self.lc_fields.SetStringItem(no, 3, str(default))
			if options:
				opt_str = ', '.join((('%s:%s' % item) for item in options.iteritems()))
				self.lc_fields.SetStringItem(no, 4, opt_str)
		
		self.lc_fields.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		self.lc_fields.SetColumnWidth(1, wx.LIST_AUTOSIZE)
		self.lc_fields.SetColumnWidth(2, wx.LIST_AUTOSIZE)
		self.lc_fields.SetColumnWidth(3, wx.LIST_AUTOSIZE)
		self.lc_fields.SetColumnWidth(4, wx.LIST_AUTOSIZE)

	def _on_btn_title_refresh(self, event):
		if self._cls.fields:
			self.tc_title.SetValue('%%%s' % self._cls.fields[0][0])

	def _on_title_auto(self, event):
		title_auto = self.cb_title_auto.IsChecked()
		self._cls.title_auto = title_auto
		if title_auto:
			self.tc_title.SetValue(self._cls.gen_auto_title())
		self.tc_title.Enable(not title_auto)

	def _on_fields_deselected(self, event):
		self._set_buttons_status()

	def _on_fields_selected(self, event):
		self._set_buttons_status()

	def _on_fields_activated(self, event): 
		item_idx = self._get_selected_field_idx()
		if item_idx < 0:
			return

		field = self._cls.fields[item_idx]
		name = field[0]
		data = dict(name=name, type=field[1], default=field[2], options=field[3])
		data['_fields_names'] = [ field[0] for field in self._cls.fields 
				if field[0] != name]
		dlg = EditFieldDlg(self, data)
		if dlg.ShowModal() == wx.ID_OK:
			field = (data['name'], data['type'], data['default'], data['options'])
			self._cls.fields[item_idx] = field
			self._refresh_list(self._cls)
			self._on_title_auto(None)
		dlg.Destroy()

	def _on_btn_add_field(self, event):
		data = {}
		data['_fields_names'] = [ field[0] for field in self._cls.fields ]
		dlg = EditFieldDlg(self, data)
		if dlg.ShowModal() == wx.ID_OK:
			field = (data['name'], data['type'], data['default'], data['options'])
			self._cls.fields.append(field)
			self._refresh_list(self._cls)
			self._on_title_auto(None)
		dlg.Destroy()

	def _on_btn_del_field(self, event): # wxGlade: _EditClassesDlg.<event_handler>
		item_idx = self._get_selected_field_idx()
		if item_idx < 1:
			return 
		dlg = wx.MessageDialog(self, _('Delete field?'), _('Class'), 
				wx.ICON_QUESTION|wx.YES_NO|wx.NO_DEFAULT)
		if dlg.ShowModal() == wx.ID_YES:
			self._cls.fields.pop(item_idx)
			self._refresh_list(self._cls)
			self._on_title_auto(None)
		dlg.Destroy()

	def _on_button_up(self, event): # wxGlade: _EditClassesDlg.<event_handler>
		item_idx = self._get_selected_field_idx()
		if item_idx < 1:
			return 
		fields = self._cls.fields
		fields[item_idx], fields[item_idx-1] = fields[item_idx-1], fields[item_idx]
		self._refresh_list(self._cls)
		self.lc_fields.SetItemState(item_idx-1, wx.LIST_STATE_SELECTED, 
				wx.LIST_STATE_SELECTED)
		self._on_title_auto(None)

	def _on_button_down(self, event): # wxGlade: _EditClassesDlg.<event_handler>
		item_idx = self._get_selected_field_idx()
		if item_idx < 0 or item_idx == self.lc_fields.GetItemCount() - 1:
			return 
		fields = self._cls.fields
		fields[item_idx], fields[item_idx+1] = fields[item_idx+1], fields[item_idx]
		self._refresh_list(self._cls)
		self.lc_fields.SetItemState(item_idx+1, wx.LIST_STATE_SELECTED, 
				wx.LIST_STATE_SELECTED)
		self._on_title_auto(None)

	def _on_ok(self, evt):
		name = self.tc_name.GetValue()
		title_expr = self.tc_title.GetValue()
		if not (name and title_expr):
			dlg = wx.MessageDialog(self, _('Enter name and title expresion'),
					_('Class'), wx.OK|wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return

		if name in self._cls_names:
			dlg = wx.MessageDialog(self, _('Class with this name alreaty exists'),
					_('Class'), wx.OK|wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return

		self._cls.name = name
		self._cls.title_expr = title_expr

		self.EndModal(wx.ID_OK)

	def _get_selected_field_idx(self):
		if self.lc_fields.GetSelectedItemCount() == 0:
			return -1
		return self.lc_fields.GetNextItem(-1, wx.LIST_NEXT_ALL, 
				wx.LIST_STATE_SELECTED)

	def _set_buttons_status(self):
		selected_item = self.lc_fields.GetSelectedItemCount() > 0
		self.b_del_field.Enable(selected_item)
		self.button_up.Enable(selected_item)
		self.button_down.Enable(selected_item)


# vim: encoding=utf8: ff=unix:
