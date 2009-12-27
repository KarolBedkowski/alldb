# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-12-20'


import time
import wx
import wx.lib.scrolledpanel as scrolled


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
		if obj:
			self._fill_fields_from_obj()
		else:
			self._fill_fields_clear()

	def get_values(self):
		data = {}
		for name, (field, ftype, _default, options) in self._fields.iteritems():
			if field:
				if ftype == 'date':
					data[name] = wxdate2strdate(field.GetValue())
				else:
					data[name] = field.GetValue()
		tags = self.tc_tags.GetValue()
		return data, tags

	def _create_fields(self):
		grid = wx.FlexGridSizer(len(self._obj_cls.fields), 2, 3, 6)
		grid.AddGrowableCol(1)
		for name, ftype, _default, options in self._obj_cls.fields:
			grid.Add(wx.StaticText(self, -1, "%s:" % format_label(name)), 0, 
					wx.ALIGN_CENTER_VERTICAL)
			ctrl = None
			if ftype == 'bool':
				ctrl = wx.CheckBox(self, -1)
			elif ftype == 'multi':
				ctrl = wx.TextCtrl(self, -1, 
						style=wx.TE_MULTILINE|wx.TE_WORDWRAP|wx.HSCROLL)
			elif ftype == 'date':
				ctrl = wx.DatePickerCtrl(self, -1, 
						style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY|wx.DP_ALLOWNONE)
			else:
				ctrl = wx.TextCtrl(self,  -1)
			self._fields[name] = (ctrl, ftype, _default, options)

			if ctrl:
				grid.Add(ctrl, 1, wx.EXPAND)
			else:
				grid.Add((1, 1))

		grid.Add(wx.StaticText(self, -1, _("Tags:")), 0, wx.ALIGN_CENTER_VERTICAL)
		self.tc_tags = wx.TextCtrl(self, -1)
		grid.Add(self.tc_tags, 1, wx.EXPAND)

		grid.Add(wx.StaticText(self, -1, _("C. / M.:")), 0, wx.ALIGN_CENTER_VERTICAL)
		self.lb_created_modified = wx.StaticText(self, -1, '')
		grid.Add(self.lb_created_modified, 1, wx.EXPAND)

		return grid

	def _fill_fields_from_obj(self):
		for name, (field, ftype, _default, options) in self._fields.iteritems():
			if not field:
				continue
			value = self._obj.data.get(name)
			if ftype == 'bool':
				field.SetValue(bool(value))
			elif ftype == 'date':
				date = strdate2wxdate(value)
				field.SetValue(date)
			else:
				field.SetValue(str(value or ''))
		self.tc_tags.SetValue(self._obj.tags_str)
		date_created, date_modified = '-', '-'
		if self._obj.date_created:
			date_created = time.strftime('%x %X',
					time.localtime(self._obj.date_created))
		if self._obj.date_modified:
			date_modified = time.strftime('%x %X',
					time.localtime(self._obj.date_modified))
		self.lb_created_modified.SetLabel(date_created + ' / ' + date_modified)

	def _fill_fields_clear(self):
		for field, ftype, _default, options in self._fields.itervalues():
			if field:
				if ftype == 'bool':
					field.SetValue(bool(_default))
				elif ftype == 'date':
					date = strdate2wxdate(_default)
					field.SetValue(date)
				else:
					field.SetValue(str(_default))
		self.tc_tags.SetValue('')
		self.lb_created_modified.SetLabel('')


def strdate2wxdate(strdate):
	date = wx.DateTime()
	try:
		date.ParseDate(strdate)
	except Exception, err:
		print err
	return date


def wxdate2strdate(wxdate):
	return wxdate.Format()


def format_label(label):
	label = label.strip()
	label = label[0].upper() + label[1:]
	label.replace('_', ' ')
	return label

# vim: encoding=utf8: ff=unix:
