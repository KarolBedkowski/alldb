# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009'
__version__ = '0.1'
__release__ = '2009-12-20'


import os.path

import wx
import wx.grid
from wx import xrc

from alldb.libs import wxresources
from alldb.filetypes import csv_support
from alldb.gui.dialogs import message_boxes as msgbox


class MappingTable(wx.grid.PyGridTableBase):
	def __init__(self, category, data):
		wx.grid.PyGridTableBase.__init__(self)
		self._category = category
		self._skip_msg = _('<Skip>')

		self._fields = [field[0] for field in self._category.fields]
		self._data = data
		while len(self._fields) < len(self._data[0]):
			self._fields.append(self._skip_msg)

		self._map_type = ''.join((wx.grid.GRID_VALUE_CHOICE, ":",
			self._skip_msg, ",", ','.join(self._fields)))

		g_style1 = wx.grid.GridCellAttr()
		g_style1.SetBackgroundColour(wx.Colour(255, 255, 255))
		g_style2 = wx.grid.GridCellAttr()
		g_style2.SetBackgroundColour(wx.Colour(230, 230, 255))
		self._grid_styles = (g_style1, g_style2)

	@property
	def mapping(self):
		return dict((idx, field) for idx, field in enumerate(self._fields)
				if field != self._skip_msg)

	def GetRowLabelValue(self, row):
		if row == 0:
			return _('Mapping')
		return str(row)

	def GetColLabelValue(self, col):
		return str(col + 1)

	def GetNumberRows(self):
		return len(self._data) + 1

	def GetNumberCols(self):
		return len(self._data[0])

	def GetValue(self, row, col):
		if row == 0:
			return self._fields[col] if col < len(self._fields) else ''
		return self._data[row - 1][col]

	def SetValue(self, row, col, value):
		if row == 0:
			if value != self._skip_msg:
				for idx, field in enumerate(self._fields):
					if idx != col and field == value:
						return
			self._fields[col] = value

	def CanGetValueAs(self, row, col, typeName):
		return True

	def CanSetValueAs(self, row, col, typeName):
		return row == 0

	def GetTypeName(self, row, col):
		if row == 0:
			return self._map_type
		return wx.grid.GRID_VALUE_STRING

	def IsReadOnly(self, row, col):
		return row > 0

	def GetAttr(self, row, col, kind):
		attr = self._grid_styles[0 if row else 1]
		attr.IncRef()
		return attr


class DlgImportCsv(object):
	def __init__(self, parent, category):
		self.res = wxresources.load_xrc_resource('alldb_import_dlg.xrc')
		self.filepath = None
		self._parent = parent
		self._category = category
		self.items = []

	def run(self):
		res = False
		dlg = wx.FileDialog(self._parent, _('Choice a file'),
				wildcard=_('CSV files (*.csv)|*.csv|All files|*.*'),
				style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if dlg.ShowModal() == wx.ID_OK:
			self.filepath = dlg.GetPath()
		dlg.Destroy()
		if self.filepath:
			self._init_dialog()
			res = self.wnd.ShowModal() == wx.ID_OK
			self.wnd.Destroy()
		return res

	def _init_dialog(self):
		self._load_controls()
		self._create_bindings()
		self._setup()
		self._load_header()

	def _load_controls(self):
		self.wnd = self.res.LoadDialog(self._parent, 'dlg_csv_params')
		assert self.wnd is not None
		panel_grid = xrc.XRCCTRL(self.wnd, 'panel_grid')
		grid_box = wx.BoxSizer(wx.VERTICAL)
		self._grid_mapping = wx.grid.Grid(panel_grid)
		grid_box.Add(self._grid_mapping, 1, wx.EXPAND)
		panel_grid.SetSizerAndFit(grid_box)
		self._cb_header = xrc.XRCCTRL(self.wnd, 'cb_header')

	def _create_bindings(self):
		wnd = self.wnd
		wnd.Bind(wx.EVT_BUTTON, self._on_btn_cancel, id=wx.ID_CANCEL)
		xrc.XRCCTRL(self.wnd, 'btn_import').Bind(wx.EVT_BUTTON, self._on_btn_import)

	def _setup(self):
		xrc.XRCCTRL(self.wnd, 'label_filename').SetLabel(self.filepath)
		self._cb_header.SetValue(False)

	def _load_header(self):
		header = list(csv_support.load_cvs_header(self.filepath))
		cols = 0
		if len(header) > 0:
			cols = max(len(row) for row in header)
		if cols == 0:
			msgbox.message_box_info_ex(self.wnd, _('Can not import selected file'),
					_("File %s don't contain any useful information.") % \
					os.path.basename(self.filepath))
			return
		self._mapping_table = MappingTable(self._category, header)
		self._grid_mapping.SetTable(self._mapping_table)

	def _on_btn_cancel(self, _event):
		self.wnd.EndModal(wx.ID_CANCEL)

	def _on_btn_import(self, _event):
		self._mapping = self._mapping_table.mapping
		if not self._mapping:
			msgbox.message_box_info_ex(self.wnd, _('Fields mapping is not defined'),
					_('Please define how columns in the CSV file should be mapped '
						'to fields in this category'))
			return
		skip_header = self._cb_header.IsChecked()
		self.items = list(csv_support.import_csv(self.filepath, self._category,
				self._mapping, skip_header))
		self.wnd.EndModal(wx.ID_OK)


# vim: encoding=utf8: ff=unix:
