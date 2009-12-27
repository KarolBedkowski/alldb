# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-20'


import wx

from alldb.model import objects

from _ClassesDlg import _ClassesDlg
from EditClassesDlg import EditClassesDlg

class ClassesDlg(_ClassesDlg):
	def __init__(self, parent, db):
		_ClassesDlg.__init__(self, None, -1)
		self._db = db
		self._current_cls = None

		self.GetSizer().Add(
				self.CreateStdDialogButtonSizer(wx.OK), 
				0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 6)

		self.Fit()
		self.fill_classes()
		self._set_buttons_state()

	def fill_classes(self):
		self.lc_classes.DeleteAllItems()
		for no, cls in enumerate(self._db.classes):
			self.lc_classes.InsertStringItem(no, str(cls.name))
			self.lc_classes.SetItemData(no, cls.oid)

	def _edit_class(self, cls_oid):
		cls = self._db.get(cls_oid) if cls_oid else objects.ObjectClass()
		cls_names = [ c.name for c in self._db.classes if c.oid != cls_oid ]
		dlg = EditClassesDlg(self, cls, cls_names)
		if dlg.ShowModal() == wx.ID_OK:
			self._db.put(cls)
			self.fill_classes()
		dlg.Destroy()

	def _on_class_choice(self, event):
		oid = event.GetClientData()
		cls = self._db.get(oid)
		self.show_class(cls)
		event.Skip()

	def _on_list_classes_deselect(self, event):
		self._set_buttons_state()

	def _on_list_classes_selected(self, event):
		self._set_buttons_state()

	def _on_list_classes_activate(self, event):
		oid = event.GetData()
		self._edit_class(oid)
		event.Skip()

	def _on_btn_new(self, event): # wxGlade: _ClassesDlg.<event_handler>
		self._edit_class(None)

	def _on_btn_edit(self, event):
		if self.lc_classes.GetSelectedItemCount() == 0:
			return
		item_idx = self.lc_classes.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		oid = self.lc_classes.GetItemData(item_idx)
		self._edit_class(oid)


	def _on_btn_delete(self, event): # wxGlade: _ClassesDlg.<event_handler>
		print "Event handler `_on_btn_delete' not implemented!"
		event.Skip()

	def _set_buttons_state(self):
		item_selected = self.lc_classes.GetSelectedItemCount() > 0
		self.button_edit.Enable(item_selected)
		self.button_delete.Enable(item_selected)


# vim: encoding=utf8: ff=unix:
