# -*- coding: utf-8 -*-

"""
Główne okno programu
"""
from __future__ import with_statement

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009,2010'
__version__ = '0.1'
__release__ = '2009-12-20'


import os.path
from contextlib import contextmanager

import wx
from wx import xrc

from alldb.libs import wxresources
from alldb.libs.appconfig import AppConfig
from alldb.libs.iconprovider import IconProvider
from alldb.filetypes.csv_support import export2csv
from alldb.filetypes.html_support import export_html
from alldb.filetypes import exporting
from alldb.gui.dialogs import message_boxes as msgbox
from alldb.model import objects

from .panel_info import PanelInfo, EVT_RECORD_UPDATED
from .dlg_classes import DlgClasses
from .dlg_about import show_about_box
from .dlg_import_csv import DlgImportCsv


_ID_TIMER_CLEAR_STATUS = 1


class FrameMain(object):
	''' Klasa głównego okna programu'''
	def __init__(self, db):
		self.res = wxresources.load_xrc_resource('alldb.xrc')
		self._icon_provider = IconProvider()
		self._icon_provider.load_icons(['alldb'])

		self._load_controls()
		self._create_toolbar()
		self._create_bindings()
		self._setup(db)

	@property
	def current_class_id(self):
		return self._result.cls.oid if self._result else None

	@property
	def current_obj_id(self):
		return self._curr_obj.oid if self._curr_obj else None

	@property
	def current_tags(self):
		return self._result.tags if self._result else []

	def _setup(self, db):
		self._db = db
		self._curr_obj = None
		self._curr_info_panel = None
		self._result = None
		self._cols = []
		self._current_sorting_col = 0
		self._items = None
		self._tagslist = []
		self._status_update_timer = wx.Timer(self.wnd, _ID_TIMER_CLEAR_STATUS)

		self.wnd.SetIcon(self._icon_provider.get_icon('alldb'))

		if wx.Platform == '__WXMSW__':
			self.wnd.SetBackgroundColour(wx.SystemSettings.GetColour(
					wx.SYS_COLOUR_ACTIVEBORDER))

		self.searchbox.SetDescriptiveText(_('Search'))
		self.searchbox.ShowCancelButton(True)

		self._set_buttons_status()
		fclass_oid = self._fill_classes()
		if fclass_oid is not None:
			self.choice_klasa.SetSelection(0)
			self._show_class(fclass_oid)

		appconfig = AppConfig()
		autosave = appconfig.get('frame_main', 'autosave', 1) > 0
		self._menu_save_on_scroll.Check(autosave)

		self._set_size_pos()

	def _load_controls(self):
		self.wnd = self.res.LoadFrame(None, 'frame_main')
		assert self.wnd is not None
		self.window_1 = xrc.XRCCTRL(self.wnd, 'window_1')
		self.window_2 = xrc.XRCCTRL(self.wnd, 'window_2')
		self.list_items = xrc.XRCCTRL(self.wnd, 'list_items')
		self.label_info = xrc.XRCCTRL(self.wnd, 'label_info')
		self.clb_tags = xrc.XRCCTRL(self.wnd, 'clb_tags')
		self.choice_klasa = xrc.XRCCTRL(self.wnd, 'choice_klasa')
		self.panel_info = xrc.XRCCTRL(self.wnd, 'panel_info')
		self.choice_filter = xrc.XRCCTRL(self.wnd, 'choice_filter')

		self.searchbox = wx.SearchCtrl(self.wnd, -1)
		self.res.AttachUnknownControl('searchbox', self.searchbox, self.wnd)

		menu = self.wnd.GetMenuBar()
		self.menu_item_delete = menu.FindItemById(xrc.XRCID('menu_item_delete'))
		self.menu_item_duplicate = menu.FindItemById(xrc.XRCID(
				'menu_item_duplicate'))
		self._menu_save_on_scroll = menu.FindItemById(xrc.XRCID(
				'menu_save_on_scroll'))

	def _create_bindings(self):
		wnd = self.wnd
		wnd.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self._on_search, self.searchbox)
		wnd.Bind(wx.EVT_TEXT_ENTER, self._on_search, self.searchbox)
		wnd.Bind(wx.EVT_TEXT, self._on_search, self.searchbox)
		wnd.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self._on_search, self.searchbox)
		wnd.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self._on_search_cancel,
				self.searchbox)
		wnd.Bind(wx.EVT_CHECKLISTBOX, self._on_clb_tags, self.clb_tags)
		wnd.Bind(wx.EVT_CLOSE, self._on_close)
		wnd.Bind(wx.EVT_MENU, self._on_menu_export_csv,
				id=xrc.XRCID('menu_export_csv'))
		wnd.Bind(wx.EVT_MENU, self._on_menu_export_html,
				id=xrc.XRCID('menu_export_html'))
		wnd.Bind(wx.EVT_MENU, self._on_menu_import_csv,
				id=xrc.XRCID('menu_import_csv'))
		wnd.Bind(wx.EVT_MENU, self._on_menu_exit, id=xrc.XRCID('menu_exit'))
		wnd.Bind(wx.EVT_MENU, self._on_menu_item_new, id=xrc.XRCID('menu_item_new'))
		wnd.Bind(wx.EVT_MENU, self._on_menu_item_delete,
				id=xrc.XRCID('menu_item_delete'))
		wnd.Bind(wx.EVT_MENU, self._on_menu_item_duplicate,
				id=xrc.XRCID('menu_item_duplicate'))
		wnd.Bind(wx.EVT_MENU, self._on_menu_categories,
				id=xrc.XRCID('menu_categories'))
		wnd.Bind(wx.EVT_MENU, self._on_menu_about, id=xrc.XRCID('menu_about'))
		wnd.Bind(wx.EVT_MENU, self._on_menu_optimize_database,
				id=xrc.XRCID('menu_optimize_database'))
		wnd.Bind(wx.EVT_MENU, self._on_btn_apply, id=xrc.XRCID('menu_save_changes'))
		wnd.Bind(wx.EVT_MENU, self._on_menu_backup_create,
				id=xrc.XRCID('menu_backup_create'))
		wnd.Bind(wx.EVT_MENU, self._on_menu_backup_restore,
				id=xrc.XRCID('menu_backup_restore'))
		wnd.Bind(wx.EVT_MENU, self._on_menu_save_items,
				id=xrc.XRCID('menu_save_items'))
		wnd.Bind(wx.EVT_MENU, self._on_menu_load_items,
				id=xrc.XRCID('menu_load_items'))
		wnd.Bind(wx.EVT_CHOICE, self._on_class_select, self.choice_klasa)
		wnd.Bind(wx.EVT_CHOICE, self._on_filter_select, self.choice_filter)
		wnd.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_item_deselect,
				self.list_items)
		self.list_items.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_item_select)
		self.list_items.Bind(wx.EVT_LIST_COL_CLICK, self._on_items_col_click)
		self.wnd.Bind(EVT_RECORD_UPDATED, self._on_record_updated)
		self.wnd.Bind(wx.EVT_TIMER, self._on_timer)

	def _set_size_pos(self):
		appconfig = AppConfig()
		size = appconfig.get('frame_main', 'size', (800, 600))
		if size:
			self.wnd.SetSize(size)
		position = appconfig.get('frame_main', 'position')
		if position:
			self.wnd.Move(position)
		self.window_1.SetSashPosition(appconfig.get('frame_main', 'win1', 200))
		self.window_2.SetSashPosition(appconfig.get('frame_main', 'win2', -200))

	def _create_toolbar(self):
		toolbar = self.wnd.CreateToolBar()
		iconpr = self._icon_provider
		tbi = toolbar.AddLabelTool(-1, _('Refresh'), iconpr.get_image('refresh'),
				shortHelp=_("Refresh"), longHelp=_("Refresh items list"))
		self.wnd.Bind(wx.EVT_TOOL, self._on_refresh_all, id=tbi.GetId())
		toolbar.AddSeparator()
		tbi = toolbar.AddLabelTool(-1, _('Add Item'), wx.ArtProvider.GetBitmap(
				wx.ART_NEW, wx.ART_TOOLBAR), shortHelp=_('Add item'),
				longHelp=_('Create new item'))
		self.wnd.Bind(wx.EVT_TOOL, self._on_btn_new, id=tbi.GetId())
		tbi = toolbar.AddLabelTool(-1, _('Delete Item'), wx.ArtProvider.GetBitmap(
				wx.ART_DELETE, wx.ART_TOOLBAR), shortHelp=_('Delete item'),
				longHelp=_('Delete selected items'))
		self.wnd.Bind(wx.EVT_TOOL, self._on_menu_item_delete, id=tbi.GetId())
		toolbar.AddSeparator()
		tbi = toolbar.AddLabelTool(-1, _('Save Item'), wx.ArtProvider.GetBitmap(
				wx.ART_TICK_MARK, wx.ART_TOOLBAR), shortHelp=_('Save item'),
				longHelp=_('Save changes'))
		self.wnd.Bind(wx.EVT_TOOL, self._on_btn_apply, id=tbi.GetId())
		toolbar.AddSeparator()
		tbi = toolbar.AddLabelTool(-1, _('Quit'), wx.ArtProvider.GetBitmap(
				wx.ART_QUIT, wx.ART_TOOLBAR), shortHelp=_('Quit'),
				longHelp=_('Close application'))
		self.wnd.Bind(wx.EVT_TOOL, self._on_menu_exit, id=tbi.GetId())
		toolbar.Realize()

	@contextmanager
	def _wait_cursor(self):
		self.wnd.SetCursor(wx.HOURGLASS_CURSOR)
		try:
			yield
		finally:
			wx.SetCursor(wx.NullCursor)

	def _fill_classes(self, select=None):
		''' wczytenie listy klas i wypełnienie choicebox-a
		@select - oid klasy do zaznaczenia lib None'''
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

	def _hide_info_panel(self):
		if self._curr_info_panel:
			self._curr_info_panel.Destroy()
			self._curr_info_panel = None

	def _create_info_panel(self):
		''' utworzenie panela z polami dla podanej klasy '''
		if self._curr_info_panel is not None:
			return self._curr_info_panel
		panel = PanelInfo(self, self.panel_info, self._result.cls)
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
			field_name = get_field_human(field)
			self.list_items.InsertColumn(col + 1, field_name)
		self._current_sorting_col = 1

	def _show_class(self, class_oid):
		''' wyświetlenie klasy - listy tagów i obiektów '''
		with self._wait_cursor():
			curr_class_oid = self.current_class_id
			result = self._db.load_class(class_oid)
			if not curr_class_oid or curr_class_oid != class_oid:
				self._hide_info_panel()
				self._curr_obj = None
			self._result = result
			self._create_columns_in_list(result.cls)
			self._fill_items()
			self._set_buttons_status()
			self.choice_filter.Clear()
			for field in result.fields:
				self.choice_filter.Append(field, field)
			self.choice_filter.SetSelection(0)
			self._fill_tags((curr_class_oid != class_oid))
			self.wnd.SetTitle(_('%s - AllDB') % result.cls.name)

	def _fill_items(self, select=None, do_filter=True, do_sort=True):
		''' wyświetlenie listy elemtów aktualnej klasy, opcjonalne zaznaczenie
		jednego '''
		list_items = self.list_items
		list_items.Freeze()
		list_items.DeleteAllItems()
		search = self.searchbox.GetValue()
		selected_tags = self.selected_tags

		keyidx = self.choice_filter.GetCurrentSelection()
		key = None
		if keyidx >= 0:
			key = self.choice_filter.GetString(keyidx)
		if do_filter:
			items = self._result.filter_items(search, selected_tags, self._cols, key)
		if do_sort:
			items = self._result.sort_items(self._current_sorting_col)

		item2select = None
		self._items = []
		for num, item in enumerate(items):
			oid, cols = item
			list_items.InsertStringItem(num, str(num + 1))
			for colnum, col in enumerate(cols):
				col = objects.get_field_value_human(col)
				list_items.SetStringItem(num, colnum + 1, unicode(col))
			list_items.SetItemData(num, int(oid))
			if oid == select:
				item2select = num
			self._items.append((oid, cols))

		for x in xrange(len(self._cols) + 2):
			list_items.SetColumnWidth(x, wx.LIST_AUTOSIZE)

		items_count = self.list_items.GetItemCount()
		self.label_info.SetLabel(_('Items: %d') % items_count)

		if item2select is not None:
			list_items.EnsureVisible(item2select)
			list_items.SetItemState(item2select,
					wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
					wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
		list_items.Thaw()

	def _fill_tags(self, clear_selection=False):
		''' wczytanie tagów dla wszystkich elementów i wyświetlenie
		ich na liście.
		@clear_selection - wyczyszczenie zaznaczonych tagów
		@reload_tags - ponowne wczytanie tagów'''
		selected_tags = [] if clear_selection else self.selected_tags
		self.clb_tags.Clear()
		keyidx = self.choice_filter.GetCurrentSelection()
		if keyidx < 0:
			return
		key = self.choice_filter.GetString(keyidx)
		if key == _('Tags'):
			tags = self._result.tags.iteritems()
		else:
			tags = self._result.get_filter_for_field(key).iteritems()

		if wx.Platform == '__WXMSW__':
			self._tagslist = []

		for tag, count in sorted(tags):
			tagname = objects.get_field_value_human(tag)
			num = self.clb_tags.Append(_('%(tag)s (%(items)d)') % dict(tag=tagname,
					items=count))
			if wx.Platform == '__WXMSW__':
				self._tagslist.append(tag)
			else:
				self.clb_tags.SetClientData(num, tag)
			if tag in selected_tags:
				self.clb_tags.Check(num, True)

	def _set_buttons_status(self, new_record=False):
		record_showed = (self.list_items.GetSelectedItemCount() > 0) or new_record
		if self._curr_info_panel:
			self._curr_info_panel.Show(record_showed)
			self.panel_info.GetSizer().Layout()
		self.menu_item_delete.Enable(record_showed and not new_record)
		self.menu_item_duplicate.Enable(record_showed and not new_record)

	def _save_object(self, ask_for_save=False, update_lists=True, select=None):
		if not self._curr_obj:
			return
		if self._menu_save_on_scroll.IsChecked():
			ask_for_save = False
		data, tags, blobs = self._curr_info_panel.get_values()
		curr_obj = self._curr_obj
		if curr_obj.check_for_changes(data, tags, blobs):
			if ask_for_save:
				if not msgbox.message_box_save_confirm(self.wnd,
						_('Save changes?')):
					return

			with self._wait_cursor():
				curr_obj.data.update(data)
				curr_obj.blobs = blobs
				curr_obj.set_tags(tags)
				curr_obj.save()
				self._set_status_text(_('Saved'))
				if self._curr_info_panel:
					self._curr_info_panel.update_base_info(curr_obj)
				oid = curr_obj.oid
				reload_items = True
				if update_lists:
					if self._items:
						ind = [idx for idx, (ioid, item) in enumerate(self._items)
								if ioid == oid]
						if ind:
							indx = ind[0]
							info = get_object_info(self._result.cls, curr_obj,
									self._cols)
							self._items[indx] = info
							for col, val in enumerate(info[1]):
								val = objects.get_field_value_human(val)
								self.list_items.SetStringItem(indx, col + 1, val)
							reload_items = False

				self._result = self._db.load_class(self._result.cls.oid)
				self._fill_tags()
				if reload_items:
					self._fill_items(select=(select or oid))

	def _on_close(self, evt):
		appconfig = AppConfig()
		appconfig.set('frame_main', 'size', self.wnd.GetSizeTuple())
		appconfig.set('frame_main', 'position', self.wnd.GetPositionTuple())
		appconfig.set('frame_main', 'win1', self.window_1.GetSashPosition())
		appconfig.set('frame_main', 'win2', self.window_2.GetSashPosition())
		appconfig.set('frame_main', 'autosave',
				1 if self._menu_save_on_scroll.IsChecked() else 0)
		self.wnd.Destroy()

	def _on_class_select(self, evt):
		oid = evt.GetClientData()
		if oid != self.current_class_id:
			self._save_object(True, False)
			self._show_class(oid)

	def _on_filter_select(self, evt):
		self._fill_tags()

	def _on_item_deselect(self, event):
		pass

	def _on_item_select(self, evt):
		oid = evt.GetData()
		if oid == self.current_obj_id:
			return
		self._save_object(True, True, oid)
		self._curr_obj = self._db.get_object(oid)
		self._create_info_panel()
		self._curr_info_panel.update(self._curr_obj)
		self._set_buttons_status()

	def _on_items_col_click(self, event):
		self._current_sorting_col = event.m_col
		with self._wait_cursor():
			self._fill_items(self.current_obj_id, do_filter=False)

	def _on_btn_new(self, event):
		self._save_object(True, True)
		self._curr_obj = self._result.cls.create_object()
		self._create_info_panel()
		self._curr_info_panel.update(self._curr_obj)
		self._set_buttons_status(True)
		self._curr_info_panel.set_focus()

	def _on_btn_apply(self, event):
		self._save_object()
		self._curr_info_panel.update(self._curr_obj)

	def _on_clb_tags(self, evt):
		with self._wait_cursor():
			self._fill_items()
		evt.Skip()

	def _on_search(self, evt):
		with self._wait_cursor():
			self._fill_items(do_sort=False)

	def _on_search_cancel(self, event):
		if self.searchbox.GetValue():
			self.searchbox.SetValue('')
			with self._wait_cursor():
				self._fill_items(do_sort=False)

	def _on_menu_exit(self, event):
		self._save_object(True, False)
		self.wnd.Close()
		event.Skip()

	def _on_menu_item_new(self, event):
		if self._result:
			self._on_btn_new(event)

	def _on_menu_item_delete(self, event):
		litems = self.list_items
		cnt = litems.GetSelectedItemCount()
		if cnt == 0:
			return

		msg = ngettext('one object', '%(count)d objects', cnt)
		if msgbox.message_box_delete_confirm(self.wnd, msg % dict(count=cnt)):
			with self._wait_cursor():
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

	def _on_menu_item_duplicate(self, event):
		if self._curr_obj:
			self._curr_obj = self._curr_obj.duplicate()
			self._create_info_panel()
			self._curr_info_panel.update(self._curr_obj)
			self._set_buttons_status()
			self._curr_info_panel.set_focus()

	def _on_menu_categories(self, event):
		current_class_oid = self.current_class_id
		DlgClasses(self.wnd, self._db).run()
		self._hide_info_panel()
		current_class_oid = self._fill_classes(current_class_oid)
		self._show_class(current_class_oid)

	def _on_menu_import_csv(self, event):
		wzrg = DlgImportCsv(self.wnd, self._result.cls)
		if wzrg.run():
			self._db.put_object(wzrg.items)
		current_class_oid = self._fill_classes(self._result.cls.oid)
		self._show_class(current_class_oid)

	def _on_menu_export_csv(self, event):
		dlg = wx.FileDialog(self.wnd, _('Choice a file'),
				wildcard=_('CSV files (*.csv)|*.csv|All files|*.*'),
				style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() == wx.ID_OK:
			filepath = dlg.GetPath()
			if not os.path.splitext(filepath)[1]:
				filepath += '.csv'
			cls = self._result.cls
			items = self._result.items
			export2csv(filepath, cls, items)
		dlg.Destroy()

	def _on_menu_export_html(self, event):
		dlg = wx.FileDialog(self.wnd, _('Choice a file'),
				wildcard=_('HTML files (*.html, *.htm)|*.html;*.htm|All files|*.*'),
				style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() == wx.ID_OK:
			filepath = dlg.GetPath()
			if not os.path.splitext(filepath)[1]:
				filepath += '.html'
			cls = self._result.cls
			items = self._result.items
			export_html(filepath, cls, items)
		dlg.Destroy()

	def _on_menu_about(self, event):
		show_about_box(self.wnd)

	def _on_menu_optimize_database(self, event):
		with self._wait_cursor():
			self._db.optimize()
		msgbox.message_box_info_ex(self.wnd, _('Optimalization finished.'), None)

	def _on_menu_backup_create(self, event):
		dlg = wx.FileDialog(self.wnd, _('Choice a Backup File'),
				wildcard=_('Backup files (*.alldb_bak)|*.alldb_bak|All files|*.*'),
				style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() == wx.ID_OK:
			filepath = dlg.GetPath()
			if not os.path.splitext(filepath)[1]:
				filepath += '.alldb_bak'
			self._db.create_backup(filepath)
		dlg.Destroy()

	def _on_menu_backup_restore(self, event):
		print '_on_menu_backup_restore'

	def _on_menu_save_items(self, event):
		try:
			exporting.export_items(self.wnd, self._result.cls, self._result.items)
		except RuntimeError, err:
			msgbox.message_box_error_ex(self.wnd, _('Cannot save items.'), err)

	def _on_menu_load_items(self, event):
		try:
			items, blobs = exporting.import_items(self.wnd, self._result.cls,
					self._db)
		except RuntimeError, err:
			msgbox.message_box_error_ex(self.wnd, _('Cannot load items.'), err)
		else:
			if not items:
				return
			msgbox.message_box_info_ex(self.wnd, _("Loading items finished."),
					_("Loaded %(items)d items and %(blobs)d blobs.") % \
							{'items': items, 'blobs': blobs})
			self._on_refresh_all(None)

	def _on_record_updated(self, evt):
		if self._menu_save_on_scroll.IsChecked():
			self._save_object()

	def _on_refresh_all(self, event):
		if self._result:
			self._show_class(self._result.cls.oid)

	def _on_timer(self, event):
		if event.Id == _ID_TIMER_CLEAR_STATUS:
			self.wnd.SetStatusText('', 1)

	def _set_status_text(self, text):
		self._status_update_timer.Stop()
		self.wnd.SetStatusText(text, 1)
		self._status_update_timer.Start(2000, True)

	@property
	def selected_tags(self):
		cbl = self.clb_tags
		if wx.Platform == '__WXMSW__':
			checked = [self._tagslist[num] for num in xrange(cbl.GetCount())
					if cbl.IsChecked(num)]
		else:
			checked = [cbl.GetClientData(num) for num in xrange(cbl.GetCount())
					if cbl.IsChecked(num)]
		return checked


def get_object_info(cls, item, cols=None):
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


def get_field_human(field):
	if field == '__title':
		return _('Title')
	elif field.startswith('__'):
		field = field[2:]
	return field.capitalize()




# vim: encoding=utf8: ff=unix:
