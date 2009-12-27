# -*- coding: utf-8 -*-

"""
Główne okno programu
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-20'

import operator

import wx

from alldb.model.db import Db

from ._MainFrame import _MainFrame
from .PanelInfo import PanelInfo
from .ClassesDlg import ClassesDlg

class MainFrame(_MainFrame):
	''' Klasa głównego okna programu'''	
	def __init__(self):
		_MainFrame.__init__(self, None, -1)
		self.SetBackgroundColour(wx.SystemSettings.GetColour(
			wx.SYS_COLOUR_ACTIVEBORDER))
		self.window_1.SetSashPosition(200)

		self._db = Db('test.db')
		self._current_class = None
		self._current_obj = None
		self._current_info_panel = None
		self._current_tags = {}

		self.list_items.InsertColumn(0, _('No'), wx.LIST_FORMAT_RIGHT, 40)
		self.list_items.InsertColumn(1, _('Title'))

		self._set_buttons_status()

		self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self._on_search, self.searchbox)
		self.Bind(wx.EVT_TEXT_ENTER, self._on_search, self.searchbox)
		self.Bind(wx.EVT_TEXT, self._on_search, self.searchbox)
		self.Bind(wx.EVT_CHECKLISTBOX, self._on_clb_tags, self.clb_tags)

		fclass_oid = self._fill_classes()
		if fclass_oid is not None:
			self.choice_klasa.SetSelection(0)
			self._show_class(fclass_oid)

	def _fill_classes(self, select=None):
		''' wczytenie listy klas i wypełnienie choicebox-a 
			@select - oid klasy do zaznaczenia lib None
		'''
		cls2select = None
		self.choice_klasa.Clear()
		classes = self._db.classes
		for cls in classes:
			num = self.choice_klasa.Append(cls.name, cls.oid)
			if cls.oid == select:
				cls2select = num

		if cls2select is not None:
			self.choice_klasa.SetSelection(cls2select)
			return classes[cls2select].oid

		return classes[0].oid if classes else None

	def _create_info_panel(self, cls):
		''' utworzenie panela z polami dla podanej klasy '''
		if self._current_info_panel:
			self._current_info_panel.Destroy()
		panel = PanelInfo(self.panel_info, cls)
		panel_info_sizer = self.panel_info.GetSizer()
		panel_info_sizer.Add(panel, 1, wx.EXPAND)
		panel_info_sizer.Layout()
		self._current_info_panel = panel
		return panel

	def _show_class(self, class_oid):
		''' wyświetlenie klasy - listy tagów i obiektów '''
		curr_class_oid = (self._current_class.oid if self._current_class 
				else None)
		next_class = self._db.get(class_oid)
		if not curr_class_oid or curr_class_oid != class_oid:
			self._create_info_panel(next_class)
			self._current_obj = None
		self._current_class = next_class
		self._fill_tags((curr_class_oid != class_oid), reload_tags=True)
		self._fill_items()
		self._set_buttons_status()

	def _fill_items(self, select=None):
		''' wyświetlenie listy elemtów aktualnej klasy, opcjonalne zaznaczenie 
			jednego '''
		cls = self._current_class
		list_items = self.list_items
		list_items.DeleteAllItems()
		search = self.searchbox.GetValue()
		selected_tags = self.selected_tags

		items = cls.filter_objects(search, selected_tags)
		items = sorted(items, key=operator.attrgetter('title'))

		item2select = None
		for num, item in enumerate(items):
			list_items.InsertStringItem(num, str(num+1))
			list_items.SetStringItem(num, 1, str(item.title))
			list_items.SetItemData(num, item.oid)

			if item.oid == select:
				item2select = num

		list_items.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		list_items.SetColumnWidth(1, wx.LIST_AUTOSIZE)

		items_count = self.list_items.GetItemCount()
		self.label_info.SetLabel(_('Items: %d') % items_count)

		if item2select is not None:
			list_items.SetItemState(item2select, wx.LIST_STATE_SELECTED, 
				wx.LIST_STATE_SELECTED)

	def _fill_tags(self, clear_selection=False, reload_tags=False):
		''' wczytanie tagów dla wszystkich elementów i wyświetlenie
			ich na liście.
			@clear_selection - wyczyszczenie zaznaczonych tagów
			@reload_tags - ponowne wczytanie tagów
		'''
		if reload_tags or self._current_class is None:
			self._current_tags = self._current_class.get_all_items_tags()
		selected_tags = [] if clear_selection else self.selected_tags
		self.clb_tags.Clear()
		for tag, count in sorted(self._current_tags.iteritems()):
			num = self.clb_tags.Append(
					_('%(tag)s (%(items)d)') % dict(tag=tag, items=count))
			self.clb_tags.SetClientData(num, tag)
			if tag in selected_tags:
				self.clb_tags.Check(num, True)

	def _set_buttons_status(self):
		record_showed = self._current_obj is not None
		self.button_apply.Enable(record_showed)
		self.button_new_item.Enable(self._current_class is not None)
		if self._current_info_panel:
			self._current_info_panel.Show(record_showed)

	def _show_object(self, oid):
		self._current_obj = self._db.get(oid)
		self._current_info_panel.update(self._current_obj)

	def _on_class_select(self, evt):
		oid = evt.GetClientData()
		self._show_class(oid)
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
		self._current_info_panel.set_focus()
		event.Skip()

	def _on_btn_apply(self, event):
		data, tags = self._current_info_panel.get_values()
		self._current_obj.data.update(data)
		self._current_obj.set_tags(tags)
		self._current_obj.save()
		oid = self._current_obj.oid
		self._db.sync()
		self._fill_tags(reload_tags=True)
		self._fill_items(select=oid)

	def _on_clb_tags(self, evt):
		self._fill_items()
		evt.Skip()

	def _on_search(self, evt):
		self._fill_items()

	def _on_menu_exit(self, event):
		self.Close()
		event.Skip()

	def _on_menu_categories(self, event):
		current_class_oid = (self._current_class.oid if 
				self._current_class else None)
		classes_dlg = ClassesDlg(self, self._db)
		classes_dlg.ShowModal()
		classes_dlg.Destroy()
		current_class_oid = self._fill_classes(current_class_oid)
		self._show_class(current_class_oid)

	@property
	def selected_tags(self):
		cbl = self.clb_tags
		checked =  [ cbl.GetClientData(num)
				for num in xrange(cbl.GetCount())
				if cbl.IsChecked(num) ]
		return checked




# vim: encoding=utf8: ff=unix:
