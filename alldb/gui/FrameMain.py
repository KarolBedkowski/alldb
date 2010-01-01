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
from alldb.libs.appconfig import AppConfig

from .FrameMainWx import FrameMainWx
from .PanelInfo import PanelInfo
from .DlgClasses import DlgClasses

class FrameMain(FrameMainWx):
	''' Klasa głównego okna programu'''	
	def __init__(self, db):
		FrameMainWx.__init__(self, None, -1)
		self.SetBackgroundColour(wx.SystemSettings.GetColour(
			wx.SYS_COLOUR_ACTIVEBORDER))
		self.SetAutoLayout(True)

		self._db = db
		self._curr_class = None
		self._curr_obj = None
		self._curr_info_panel = None
		self._curr_tags = {}

		self.list_items.InsertColumn(0, _('No'), wx.LIST_FORMAT_RIGHT, 40)
		self.list_items.InsertColumn(1, _('Title'))

		self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self._on_search, self.searchbox)
		self.Bind(wx.EVT_TEXT_ENTER, self._on_search, self.searchbox)
		self.Bind(wx.EVT_TEXT, self._on_search, self.searchbox)
		self.Bind(wx.EVT_CHECKLISTBOX, self._on_clb_tags, self.clb_tags)
		self.Bind(wx.EVT_CLOSE, self._on_close)

		self._set_buttons_status()
		fclass_oid = self._fill_classes()
		if fclass_oid is not None:
			self.choice_klasa.SetSelection(0)
			self._show_class(fclass_oid)

		self._set_size_pos()

	def _set_size_pos(self):
		appconfig = AppConfig()
		size = appconfig.get('frame_main', 'size', (800, 600))
		if size:
			self.SetSize(size)

		position = appconfig.get('frame_main', 'position')
		if position:
			self.Move(position)

		self.window_1.SetSashPosition(appconfig.get('frame_main', 'win1', 200))
		self.window_2.SetSashPosition(appconfig.get('frame_main', 'win2', -200))

	def _fill_classes(self, select=None):
		''' wczytenie listy klas i wypełnienie choicebox-a 
			@select - oid klasy do zaznaczenia lib None
		'''
		self.choice_klasa.Clear()
		cls2select = None
		classes = self._db.classes
		if classes:
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
		if self._curr_info_panel:
			self._curr_info_panel.Destroy()
		panel = PanelInfo(self.panel_info, cls)
		panel_info_sizer = self.panel_info.GetSizer()
		panel_info_sizer.Add(panel, 1, wx.EXPAND)
		panel_info_sizer.Layout()
		self._curr_info_panel = panel
		return panel

	def _show_class(self, class_oid):
		''' wyświetlenie klasy - listy tagów i obiektów '''
		curr_class_oid = (self._curr_class.oid if self._curr_class
				else None)

		next_class = self._db.get(class_oid)
		if not curr_class_oid or curr_class_oid != class_oid:
			self._create_info_panel(next_class)
			self._curr_obj = None
		self._curr_class = next_class
		self._fill_tags((curr_class_oid != class_oid), reload_tags=True)
		self._fill_items()
		self._set_buttons_status()

	def _fill_items(self, select=None):
		''' wyświetlenie listy elemtów aktualnej klasy, opcjonalne zaznaczenie 
			jednego '''
		cls = self._curr_class
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
		if reload_tags or self._curr_class is None:
			self._curr_tags = self._curr_class.get_all_items_tags()
		selected_tags = [] if clear_selection else self.selected_tags
		self.clb_tags.Clear()
		for tag, count in sorted(self._curr_tags.iteritems()):
			num = self.clb_tags.Append(
					_('%(tag)s (%(items)d)') % dict(tag=tag, items=count))
			if wx.Platform != '__WXMSW__':
				self.clb_tags.SetClientData(num, tag)
			if tag in selected_tags:
				self.clb_tags.Check(num, True)

	def _set_buttons_status(self, new_record=False):
		record_showed =  (self.list_items.GetSelectedItemCount() > 0) or \
				new_record
		self.button_apply.Enable(record_showed)
		self.button_new_item.Enable(self._curr_class is not None)
		if self._curr_info_panel:
			self._curr_info_panel.Show(record_showed)
			self.panel_info.GetSizer().Layout()

	def _save_object(self, ask_for_save=False, update_lists=True, select=None):
		if not self._curr_obj:
			return
		data, tags = self._curr_info_panel.get_values()
		curr_obj = self._curr_obj
		if curr_obj.check_for_changes(data, tags):
			if ask_for_save:
				dlg = wx.MessageDialog(self, _('Save changes?'),
						_('AllDb'), wx.YES_NO|wx.YES_DEFAULT|wx.ICON_WARNING)
				dont_save = dlg.ShowModal() == wx.ID_NO
				dlg.Destroy()
				if dont_save:
					return

			curr_obj.data.update(data)
			curr_obj.set_tags(tags)
			curr_obj.save()
			oid = curr_obj.oid
			self._db.sync()
			if update_lists:
				self._fill_tags(reload_tags=True)
				self._fill_items(select=(select or oid))

	def _on_close(self, evt):
		appconfig = AppConfig()
		appconfig.set('frame_main','size', self.GetSizeTuple())
		appconfig.set('frame_main','position', self.GetPositionTuple())
		appconfig.set('frame_main','win1', self.window_1.GetSashPosition())
		appconfig.set('frame_main','win2', self.window_2.GetSashPosition())
		evt.Skip()

	def _on_class_select(self, evt):
		oid = evt.GetClientData()
		if oid != (self._curr_class.oid if self._curr_class else None):
			self._save_object(True, False)
			self._show_class(oid)

	def _on_item_deselect(self, event):
		pass

	def _on_item_select(self, evt):
		oid = evt.GetData()
		if oid == (self._curr_obj.oid if self._curr_obj else None):
			return
		self._save_object(True, True, oid)
		self._curr_obj = self._db.get(oid)
		self._curr_info_panel.update(self._curr_obj)
		self._set_buttons_status()

	def _on_btn_new(self, event): 
		self._save_object(True, True)
		self._curr_obj = self._curr_class.create_object()
		self._curr_info_panel.update(self._curr_obj)
		self._set_buttons_status(True)
		self._curr_info_panel.set_focus()

	def _on_btn_apply(self, event):
		self._save_object()
		self._curr_info_panel.update(self._curr_obj)

	def _on_clb_tags(self, evt):
		self._fill_items()
		evt.Skip()

	def _on_search(self, evt):
		self._fill_items()

	def _on_menu_exit(self, event):
		self._save_object(True, False)
		self.Close()
		event.Skip()

	def _on_menu_item_new(self, event):
		if self._curr_class:
			self._on_btn_new(event)

	def _on_menu_item_delete(self, event):
		if self._curr_obj:
			dlg = wx.MessageDialog(self, _('Delete current object?'),
					_('Delete'), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_HAND)
			if dlg.ShowModal() == wx.ID_YES:
				self._db.delete(self._curr_obj)
				self._db.sync()
				self._curr_obj = None
				self._fill_tags(reload_tags=True)
				self._fill_items()
			dlg.Destroy()

	def _on_menu_item_duplicate(self, event):
		if self._curr_obj:
			self._curr_obj = self._curr_obj.duplicate()
			self._curr_info_panel.update(self._curr_obj)
			self._set_buttons_status()
			self._curr_info_panel.set_focus()

	def _on_menu_categories(self, event):
		current_class_oid = (self._curr_class.oid if self._curr_class else None)
		dlg = DlgClasses(self, self._db)
		dlg.ShowModal()
		dlg.Destroy()
		if self._curr_info_panel:
			self._curr_info_panel.Destroy()
			self._curr_info_panel = None
		self._curr_class = None
		current_class_oid = self._fill_classes(current_class_oid)
		self._show_class(current_class_oid)

	@property
	def selected_tags(self):
		cbl = self.clb_tags
		if wx.Platform == '__WXMSW__':
			checked =  [ cbl.GetString(num)
					for num in xrange(cbl.GetCount())
					if cbl.IsChecked(num) ]
			checked = [ text[:text.rfind(' (')] for text in checked ]
		else:
			checked =  [ cbl.GetClientData(num)
					for num in xrange(cbl.GetCount())
					if cbl.IsChecked(num) ]
		return checked




# vim: encoding=utf8: ff=unix:
