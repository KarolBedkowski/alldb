# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-20'


import wx

from alldb.model import objects

from _EditClassesDlg import _EditClassesDlg

class EditClassesDlg(_EditClassesDlg):
	def __init__(self, parent, cls):
		_EditClassesDlg.__init__(self, None, -1)
		self._cls = cls

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

		self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
		self.Centre(wx.BOTH)

	def show_class(self, cls):
		self.tc_name.SetValue(str(cls.name))
		self.tc_title.SetValue(str(cls.title_expr))
		self._refresh_list(cls)

	def _refresh_list(self, cls):
		self.lc_fields.DeleteAllItems()
		for no, (name, ftype, default, options) in enumerate(cls.fields):
			self.lc_fields.InsertStringItem(no, str(no+1))
			self.lc_fields.SetStringItem(no, 1, str(name))

	def _on_btn_title_refresh(self, event): # wxGlade: _EditClassesDlg.<event_handler>
		print "Event handler `_on_btn_title_refresh' not implemented!"
		event.Skip()

	def _on_fields_activated(self, event): 
		if self.lc_fields.GetSelectedItemCount() == 0:
			return
		item_idx = self.lc_fields.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		name = self._cls.fields[item_idx][0]
		dlg = wx.TextEntryDialog(self, _('Field name:'), _('Class edit'), name)
		if dlg.ShowModal() == wx.ID_OK:
			name = dlg.GetValue()
			if name:
				self._cls.fields[item_idx] = (name, 'str', '', None)
				self._refresh_list(self._cls)
		dlg.Destroy()

	def _on_btn_add_field(self, event):
		dlg = wx.TextEntryDialog(self, _('Field name:'), _('Class edit'), '')
		if dlg.ShowModal() == wx.ID_OK:
			name = dlg.GetValue()
			if name:
				self._cls.fields.append((name, 'str', '', None))
				self._refresh_list(self._cls)
		dlg.Destroy()

	def _on_btn_del_field(self, event): # wxGlade: _EditClassesDlg.<event_handler>
		print "Event handler `_on_btn_del_field' not implemented!"
		event.Skip()

	def _on_ok(self, evt):
		name = self.tc_name.GetValue()
		title_expr = self.tc_title.GetValue()
		if not (name and title_expr):
			return
		
		self._cls.name = name
		self._cls.title_expr = title_expr

		self.EndModal(wx.ID_OK)

# vim: encoding=utf8: ff=unix:
