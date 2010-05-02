# -*- coding: utf-8 -*-

"""
"""

from __future__ import with_statement

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009'
__version__ = '0.1'
__release__ = '2009-12-20'


import time

import wx
from wx import xrc

from alldb.model import objects
from alldb.libs import wxresources
from alldb.gui.dialogs import message_boxes as msgbox
from alldb.filetypes import exporting

from .dlg_edit_class import DlgEditClass


class DlgClasses(object):
	def __init__(self, parent, db):
		self.res = wxresources.load_xrc_resource('alldb.xrc')
		self._load_controls(parent)
		self._create_bindings()
		self._setup(db)

	def run(self):
		res = self.wnd.ShowModal()
		self.wnd.Destroy()
		return res

	@property
	def selected_category(self):
		if self.lc_classes.GetSelectedItemCount() == 0:
			return None
		item_idx = self.lc_classes.GetNextItem(-1, wx.LIST_NEXT_ALL,
				wx.LIST_STATE_SELECTED)
		return self.lc_classes.GetItemData(item_idx)

	def _load_controls(self, parent):
		self.wnd = self.res.LoadDialog(parent, 'dlg_classes')
		assert self.wnd is not None
		self.lc_classes = xrc.XRCCTRL(self.wnd, 'lc_classes')
		self.button_delete = xrc.XRCCTRL(self.wnd, 'wxID_DELETE')
		self.button_edit = xrc.XRCCTRL(self.wnd, 'button_edit')
		self.button_export = xrc.XRCCTRL(self.wnd, 'button_export')
		self.button_import = xrc.XRCCTRL(self.wnd, 'button_import')

	def _create_bindings(self):
		wnd = self.wnd
		wnd.Bind(wx.EVT_BUTTON, self._on_btn_close, id=wx.ID_CLOSE)
		wnd.Bind(wx.EVT_BUTTON, self._on_btn_new, id=wx.ID_ADD)
		wnd.Bind(wx.EVT_BUTTON, self._on_btn_delete, id=wx.ID_DELETE)
		wnd.Bind(wx.EVT_BUTTON, self._on_btn_edit, id=xrc.XRCID('button_edit'))
		wnd.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_list_classes_deselect,
				self.lc_classes)
		wnd.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_list_classes_selected,
				self.lc_classes)
		wnd.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_classes_activate,
				self.lc_classes)
		self.button_import.Bind(wx.EVT_BUTTON, self._on_btn_import)
		self.button_export.Bind(wx.EVT_BUTTON, self._on_btn_export)

	def _setup(self, db):
		self._db = db
		self._current_cls = None
		self.fill_classes()
		self._set_buttons_state()

	def fill_classes(self):
		self.lc_classes.DeleteAllItems()
		for no, cls in enumerate(self._db.classes):
			self.lc_classes.InsertStringItem(no, str(cls.name))
			self.lc_classes.SetItemData(no, cls.oid)

	def _edit_class(self, cls_oid):
		cls = self._db.get_class(cls_oid) if cls_oid else objects.ADObjectClass()
		cls_names = [c.name for c in self._db.classes if c.oid != cls_oid]
		dlg = DlgEditClass(self.wnd, cls, cls_names)
		if dlg.run():
			self._db.put_class(cls)
			self.fill_classes()

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

	def _on_btn_new(self, event):
		self._edit_class(None)

	def _on_btn_edit(self, event):
		oid = self.selected_category
		if oid:
			self._edit_class(oid)

	def _on_btn_delete(self, event):
		if self.lc_classes.GetSelectedItemCount() == 0:
			return
		res = msgbox.message_box_delete_confirm(self.wnd,
				_('selected category and ALL items'))
		if res:
			item_idx = self.lc_classes.GetNextItem(-1, wx.LIST_NEXT_ALL,
					wx.LIST_STATE_SELECTED)
			oid = self.lc_classes.GetItemData(item_idx)
			self._db.del_class(oid)
			self.fill_classes()

	def _on_btn_close(self, event):
		self.wnd.EndModal(wx.ID_CLOSE)

	def _on_btn_import(self, event):
		try:
			clss = exporting.import_category(self.wnd)
		except RuntimeError, err:
			msgbox.message_box_error_ex(self.wnd, _('Cannot import file'), err)
		else:
			if clss is None:
				return
			cls_names = [c.name for c in self._db.classes]
			for cls in clss:
				cls.oid = None
				if cls.name in cls_names:
					cls.name = cls.name + "_" + time.asctime()
				cls_names.append(cls.name)
				self._db.put_class(cls)
			self.fill_classes()

	def _on_btn_export(self, event):
		oid = self.selected_category
		if oid is None:
			return
		cls = self._db.get_class(oid)
		exporting.export_category(self.wnd, cls)

	def _set_buttons_state(self):
		item_selected = self.lc_classes.GetSelectedItemCount() > 0
		self.button_edit.Enable(item_selected)
		self.button_delete.Enable(item_selected)
		self.button_export.Enable(item_selected)


# vim: encoding=utf8: ff=unix:
