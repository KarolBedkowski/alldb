# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-20'

import operator

import wx

from alldb.model.db import Db

from _MainFrame import _MainFrame
from _PanelInfo import PanelInfo
from ClassesDlg import ClassesDlg

class MainFrame(_MainFrame):
	def __init__(self):
		_MainFrame.__init__(self, None, -1)
		self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_ACTIVEBORDER))
		self.window_1.SetSashPosition(200)

		self._db = Db('test.db')
		self._current_class = None
		self._current_obj = None
		self._current_info_panel = None
		self._current_items = []

		self.fill_classes()
		self.list_items.InsertColumn(0, _('No'), wx.LIST_FORMAT_RIGHT, 40)
		self.list_items.InsertColumn(1, _('Title'))

		self._set_buttons_status()

		self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self._on_search, self.searchbox)
		self.Bind(wx.EVT_TEXT_ENTER, self._on_search, self.searchbox)
		self.Bind(wx.EVT_TEXT, self._on_search, self.searchbox)

	def on_menu_exit(self, event):
		self.Close()
		event.Skip()

	def fill_classes(self):
		self.choice_klasa.Clear()
		for cls in self._db.classes:
			self.choice_klasa.Append(cls.name, cls.oid)

	def fill_items(self, cls=None):
		self.list_items.DeleteAllItems()

		if cls:
			self._current_items = cls.objects
		elif not self._current_items:
			return

		search = self.searchbox.GetValue()
		items = self._current_items
		if search:
			items = ( item for item in items if item.title.find(search) > -1 )

		for num, item in enumerate(sorted(items, key=operator.attrgetter('title'))):
			self.list_items.InsertStringItem(num, str(num+1))
			self.list_items.SetStringItem(num, 1, str(item.title))
			self.list_items.SetItemData(num, item.oid)

		self.list_items.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		self.list_items.SetColumnWidth(1, wx.LIST_AUTOSIZE)

		items_count = self.list_items.GetItemCount()
		self.label_info.SetLabel(_('Items: %d') % items_count)

	def _set_buttons_status(self):
		record_showed = self._current_obj is not None
		self.button_apply.Enable(record_showed)
		self.button_cancel.Enable(record_showed)
		self.button_new_item.Enable(self._current_class is not None)
		if self._current_info_panel:
			self._current_info_panel.Show(record_showed)

	def _show_object(self, oid):
		self._current_obj = self._db.get(oid)
		self._current_info_panel.update(self._current_obj)

	def _on_class_select(self, evt):
		oid = evt.GetClientData()
		next_class = self._db.get(oid)
		if not self._current_class or self._current_class.oid != oid:
			if self._current_info_panel:
				self._current_info_panel.Destroy()
			self._current_info_panel = PanelInfo(self.panel_info, next_class)
			panel_info_sizer = self.panel_info.GetSizer()
			panel_info_sizer.Add(self._current_info_panel, 1, wx.EXPAND)
			panel_info_sizer.Layout()
			self._current_obj = None
		self._current_class = next_class
		self.fill_items(next_class)
		self._set_buttons_status()
		evt.Skip()

	def _on_item_deselect(self, event):
		if self.list_items.GetSelectedItemCount() == 0:
			self._current_obj = None
			self._set_buttons_status()

	def _on_item_select(self, evt):
		oid = evt.GetData()
		self._show_object(oid)
		self._set_buttons_status()
		evt.Skip()

	def _on_btn_new(self, event): 
		self._current_obj = self._current_class.create_object()
		self._current_info_panel.update(self._current_obj)
		self._set_buttons_status()
		event.Skip()

	def _on_btn_apply(self, event):
		data = self._current_info_panel.get_values()
		self._current_obj.data.update(data)
		self._current_obj.save()
		self._db.sync()
		self.fill_items(self._current_class)
		event.Skip()

	def _on_btn_cancel(self, event):
		oid = self._current_obj.oid
		self._show_object(oid)
		event.Skip()

	def _on_search(self, evt):
		self.fill_items()

	def _on_menu_categories(self, event):
		classes_dlg = ClassesDlg(self, self._db)
		if classes_dlg.ShowModal() == wx.ID_OK:
			pass
		classes_dlg.Destroy()
		self.fill_classes()


# vim: encoding=utf8: ff=unix:
