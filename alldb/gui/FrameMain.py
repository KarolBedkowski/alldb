# -*- coding: utf-8 -*-

"""
Główne okno programu
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009,2010'
__version__ = '0.1'
__release__ = '2009-12-20'

import wx

from alldb.libs.appconfig import AppConfig
from alldb.filetypes.csv_support import export2csv, import_csv

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
		self._curr_obj = None
		self._curr_info_panel = None
		self._result = None
		self._cols = []
		self._current_sorting_col = 0
		self._items = None

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

	@property
	def current_class_id(self):
		return self._result.cls.oid if self._result else None

	@property
	def current_obj_id(self):
		return self._curr_obj.oid if self._curr_obj else None

	@property
	def current_tags(self):
		return self._result.tags if self._result else []

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
		panel = PanelInfo(self, self.panel_info, cls)
		panel_info_sizer = self.panel_info.GetSizer()
		panel_info_sizer.Add(panel, 1, wx.EXPAND)
		panel_info_sizer.Layout()
		self._curr_info_panel = panel
		return panel

	def _create_columns_in_list(self, cls):
		self.list_items.ClearAll()
		self.list_items.InsertColumn(0, _('No'), wx.LIST_FORMAT_RIGHT, 40)
		self._cols = cls.fields_in_list
		for col, field in enumerate(self._cols):
			if field == '__title':
				field = _('Title')
			elif field.startswith('__'):
				field = field[2:]
			self.list_items.InsertColumn(col+1, field)
		self._current_sorting_col = 1

	def _show_class(self, class_oid):
		''' wyświetlenie klasy - listy tagów i obiektów '''
		curr_class_oid = self.current_class_id

		result = self._db.load_class(class_oid)
		if not curr_class_oid or curr_class_oid != class_oid \
				or self._curr_info_panel is None:
			self._create_info_panel(result.cls)
			self._curr_obj = None
		self._result = result
		self._create_columns_in_list(result.cls)
		self._fill_tags((curr_class_oid != class_oid))
		self._fill_items()
		self._set_buttons_status()

	def _fill_items(self, select=None, do_filter=True, do_sort=True):
		''' wyświetlenie listy elemtów aktualnej klasy, opcjonalne zaznaczenie
			jednego '''
		list_items = self.list_items
		list_items.Freeze()
		list_items.DeleteAllItems()
		search = self.searchbox.GetValue()
		selected_tags = self.selected_tags

		if do_filter:
			items = self._result.filter_items(search, selected_tags, self._cols)
		if do_sort:
			items = self._result.sort_items(self._current_sorting_col)

		item2select = None
		for num, item in enumerate(items):
			oid, cols = item
			list_items.InsertStringItem(num, str(num+1))
			for colnum, col in enumerate(cols):
				list_items.SetStringItem(num, colnum+1, unicode(col))
			list_items.SetItemData(num, int(oid))
			if oid == select:
				item2select = num

		for x in xrange(len(self._cols) + 2):
			list_items.SetColumnWidth(x, wx.LIST_AUTOSIZE)

		items_count = self.list_items.GetItemCount()
		self.label_info.SetLabel(_('Items: %d') % items_count)

		if item2select is not None:
			list_items.SetItemState(item2select, wx.LIST_STATE_SELECTED,
				wx.LIST_STATE_SELECTED)
		list_items.Thaw()

	def _fill_tags(self, clear_selection=False):
		''' wczytanie tagów dla wszystkich elementów i wyświetlenie
			ich na liście.
			@clear_selection - wyczyszczenie zaznaczonych tagów
			@reload_tags - ponowne wczytanie tagów
		'''
		selected_tags = [] if clear_selection else self.selected_tags
		self.clb_tags.Clear()
		for tag, count in sorted(self._result.tags.iteritems()):
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
		self.button_new_item.Enable(self._result is not None)
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
			reload_items = True
			if update_lists:
				if self._items:
					ind = [idx for idx, (ioid, item) in enumerate(self._items) if ioid == oid]
					if ind:
						indx = ind[0]
						info = get_object_info(self._result.cls, curr_obj, self._cols)
						self._items[ind[0]] = info
						for col, val in enumerate(info[1]):
							self.list_items.SetStringItem(indx, col+1, str(val))
						reload_items = False
			
			self._result = self._db.load_class(self._result.cls.oid)
			self._fill_tags()
			if reload_items:
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
		if oid != self.current_class_id:
			self._save_object(True, False)
			self._show_class(oid)

	def _on_item_deselect(self, event):
		pass

	def _on_item_select(self, evt):
		oid = evt.GetData()
		if oid == self.current_obj_id:
			return
		self._save_object(True, True, oid)
		self._curr_obj = self._db.get_object(oid)
		self._curr_info_panel.update(self._curr_obj)
		self._set_buttons_status()

	def _on_items_col_click(self, event):
		self._current_sorting_col = event.m_col
		self._fill_items(self.current_obj_id, do_filter=False)

	def _on_btn_new(self, event):
		self._save_object(True, True)
		self._curr_obj = self._result.cls.create_object()
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
		self._fill_items(do_sort=False)

	def _on_menu_exit(self, event):
		self._save_object(True, False)
		self.Close()
		event.Skip()

	def _on_menu_item_new(self, event):
		if self._result:
			self._on_btn_new(event)

	def _on_menu_item_delete(self, event):
		litems = self.list_items
		cnt = litems.GetSelectedItemCount()
		if cnt == 0:
			return

		dlg = wx.MessageDialog(self, _('Delete %d object/s?') % cnt, _('Delete'),
				wx.YES_NO | wx.NO_DEFAULT | wx.ICON_HAND)
		if dlg.ShowModal() == wx.ID_YES:
			items_to_delete = []
			itemid = -1
			while True:
				itemid = litems.GetNextItem(itemid, wx.LIST_NEXT_ALL,
						wx.LIST_STATE_SELECTED)
				if itemid == -1:
					break
				items_to_delete.append(litems.GetItemData(itemid))

			self._db.del_objects(items_to_delete)
			self._curr_obj = None
			self._result = self._db.load_class(self._result.cls.oid)
			self._fill_tags()
			self._fill_items()
		dlg.Destroy()

	def _on_menu_item_duplicate(self, event):
		if self._curr_obj:
			self._curr_obj = self._curr_obj.duplicate()
			self._curr_info_panel.update(self._curr_obj)
			self._set_buttons_status()
			self._curr_info_panel.set_focus()

	def _on_menu_categories(self, event):
		current_class_oid = self.current_class_id
		dlg = DlgClasses(self, self._db)
		dlg.ShowModal()
		dlg.Destroy()
		if self._curr_info_panel:
			self._curr_info_panel.Destroy()
			self._curr_info_panel = None
		current_class_oid = self._fill_classes(current_class_oid)
		self._show_class(current_class_oid)

	def _on_menu_import_csv(self, event):
		dlg = wx.FileDialog(self, _('Choice a file'),
				wildcard=_('CSV files (*.csv)|*.csv|All files|*.*'),
				style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
		if dlg.ShowModal() == wx.ID_OK:
			filepath = dlg.GetPath()
			cls = self._result.cls
			items = list(import_csv(filepath, cls))
			self._db.put_object(items)

		dlg.Destroy()
		current_class_oid = self._fill_classes(self._result.cls.oid)
		self._show_class(current_class_oid)

	def _on_menu_export_csv(self, event):
		dlg = wx.FileDialog(self, _('Choice a file'),
				wildcard=_('CSV files (*.csv)|*.csv|All files|*.*'),
				style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() == wx.ID_OK:
			filepath = dlg.GetPath()
			cls = self._result.cls
			items = self._result.items
			export2csv(filepath, cls, items)

		dlg.Destroy()

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


def get_object_info(self, cls, item, cols=None):
	info = None
	if cols:
		info = (item.oid, [item.get_value(col) for col in cols])
	else:
		if cls.title_show:
			info = (item.oid, [item.title])
		else:
			info = (item.oid, ['='.join((key, str(val))) 
				for key, val in item.data.iteritems()])
	return info


# vim: encoding=utf8: ff=unix:
