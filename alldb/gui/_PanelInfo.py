# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-20'


import wx
import  wx.lib.scrolledpanel as scrolled


class PanelInfo(scrolled.ScrolledPanel):
	def __init__(self, parent, obj_class, *argv, **kwarg):
		scrolled.ScrolledPanel.__init__(self, parent, -1, *argv, **kwarg)
		self._obj = None
		self._obj_cls = obj_class
		self._fields = {}

		main_grid = wx.BoxSizer(wx.VERTICAL)

		grid = self._create_fields()
		main_grid.Add(grid, 1, wx.EXPAND|wx.ALL, 6)

		self.SetSizer(main_grid)
		self.SetAutoLayout(1)
		self.SetupScrolling()

	def update(self, obj):
		self._obj = obj
		self._fill_fields()

	def get_values(self):
		data = {}
		for name, field in self._fields.iteritems():
			if field:
				data[name] = field.GetValue()
		return data

	def _create_fields(self):
		grid = wx.FlexGridSizer(len(self._obj_cls.fields), 2, 3, 6)
		grid.AddGrowableCol(1)
		for name, ftype, _default, options in self._obj_cls.fields:
			grid.Add(wx.StaticText(self, -1, "%s:" % name), 0, wx.ALIGN_CENTER_VERTICAL)
			ctrl = None
			if ftype == 'bool':
				pass
			else:
				ctrl = wx.TextCtrl(self,  -1)
			self._fields[name] = ctrl

			if ctrl:
				grid.Add(ctrl, 1, wx.EXPAND)
			else:
				grid.Add((1, 1))
		
		return grid

	def _fill_fields(self):
		if self._obj:
			for name, field in self._fields.iteritems():
				if not field:
					continue

				field.SetValue(str(self._obj.data.get(name) or ''))
		else:
			for field in self._fields.itervalues():
				if field:
					field.SetValue('')





# vim: encoding=utf8: ff=unix:
