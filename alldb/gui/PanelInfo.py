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
import wx.gizmos as gizmos
from wx.lib.expando import ExpandoTextCtrl, EVT_ETC_LAYOUT_NEEDED


class PanelInfo(scrolled.ScrolledPanel):
	def __init__(self, parent, obj_class, *argv, **kwarg):
		scrolled.ScrolledPanel.__init__(self, parent, -1, *argv, **kwarg)
		self._obj = None
		self._obj_cls = obj_class
		self._fields = {}
		self._first_field = None

		self._COLOR_HIGHLIGHT_BG = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
		self._COLOR_HIGHLIGHT_FG = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)

		main_grid = wx.BoxSizer(wx.VERTICAL)

		main_grid.Add(self._create_fields_head(), 0, wx.EXPAND)
		grid = self._create_fields()
		main_grid.Add(grid, 0, wx.EXPAND|wx.ALL, 6)
		main_grid.Add(self._create_fields_tail(), 0, wx.EXPAND)

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
				elif ftype == 'list':
					data[name] = field.GetStrings()
				elif ftype == 'choice':
					data[name] = field.GetStringSelection()
				else:
					data[name] = field.GetValue()
		tags = self.tc_tags.GetValue()
		return data, tags

	def set_focus(self):
		if self._first_field:
			self._first_field.SetFocus()

	def _create_fields_head(self):
		panel = wx.Panel(self, -1)
		panel.SetBackgroundColour(self._COLOR_HIGHLIGHT_BG)

		grid = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(panel, -1, _('Title:'))
		label.SetForegroundColour(self._COLOR_HIGHLIGHT_FG)
		font = label.GetFont()
		font.SetWeight(wx.FONTWEIGHT_BOLD)
		label.SetFont(font)
		grid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 6)

		self.tc_title = wx.StaticText(panel, -1, ' ')
		self.tc_title.SetForegroundColour(self._COLOR_HIGHLIGHT_FG)
		grid.Add(self.tc_title, 1, wx.EXPAND|wx.ALL, 6)

		panel.SetSizer(grid)
		return panel

	def _create_fields_tail(self):
		panel = wx.Panel(self, -1)
		panel.SetBackgroundColour(self._COLOR_HIGHLIGHT_BG)

		grid = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(panel, -1, _('Created:'))
		label.SetForegroundColour(self._COLOR_HIGHLIGHT_FG)
		font = label.GetFont()
		font.SetWeight(wx.FONTWEIGHT_BOLD)
		label.SetFont(font)
		grid.Add(label, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 6)

		self.lb_created = wx.StaticText(panel, -1, '')
		self.lb_created.SetForegroundColour(self._COLOR_HIGHLIGHT_FG)
		grid.Add(self.lb_created, 1, wx.EXPAND|wx.ALL, 6)

		label = wx.StaticText(panel, -1, _('Modified:'))
		label.SetForegroundColour(self._COLOR_HIGHLIGHT_FG)
		font = label.GetFont()
		font.SetWeight(wx.FONTWEIGHT_BOLD)
		label.SetFont(font)
		grid.Add(label, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 6)

		self.lb_modified = wx.StaticText(panel, -1, '      ')
		self.lb_modified.SetForegroundColour(self._COLOR_HIGHLIGHT_FG)
		grid.Add(self.lb_modified, 1, wx.EXPAND|wx.ALL, 6)

		panel.SetSizer(grid)
		return panel

	def _create_fields(self):
		self._first_field = None
		grid = wx.FlexGridSizer(len(self._obj_cls.fields), 2, 3, 6)
		grid.AddGrowableCol(1)
		for name, ftype, _default, options in self._obj_cls.fields:
			grid.Add(wx.StaticText(self, -1, "%s:" % format_label(name)), 0, 
					wx.ALIGN_CENTER_VERTICAL)
			ctrl = None
			if ftype == 'bool':
				ctrl = wx.CheckBox(self, -1)
			elif ftype == 'multi':
				ctrl = ExpandoTextCtrl(self, -1)
				self.Bind(EVT_ETC_LAYOUT_NEEDED, self._on_expand_text, ctrl)
				#ctrl = wx.TextCtrl(self, -1, 
				#		style=wx.TE_MULTILINE|wx.TE_WORDWRAP|wx.HSCROLL)
			elif ftype == 'date':
				ctrl = wx.DatePickerCtrl(self, -1, 
						style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY|wx.DP_ALLOWNONE)
			elif ftype == 'list':
				ctrl = gizmos.EditableListBox(self, -1)
			elif ftype == 'choice':
				values = options.get('values') or []
				ctrl = wx.Choice(self, -1, choices=values)
			else:
				ctrl = wx.TextCtrl(self,  -1)
			self._fields[name] = (ctrl, ftype, _default, options)

			if ctrl:
				grid.Add(ctrl, 1, wx.EXPAND)
			else:
				grid.Add((1, 1))

			if not self._first_field:
				self._first_field = ctrl

		grid.Add(wx.StaticText(self, -1, _("Tags:")), 0, wx.ALIGN_CENTER_VERTICAL)
		self.tc_tags = wx.TextCtrl(self, -1)
		grid.Add(self.tc_tags, 1, wx.EXPAND)

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
			elif ftype == 'list':
				field.SetStrings(value)
			elif ftype == 'choice':
				if value:
					field.SetStringSelection(value)
				else:
					field.SetSelection(-1)
			else:
				field.SetValue(str(value or ''))
		self.tc_title.SetLabel(self._obj.title or '')
		self.tc_tags.SetValue(self._obj.tags_str)
		date_created, date_modified = '-', '-'
		if self._obj.date_created:
			date_created = time.strftime('%x %X',
					time.localtime(self._obj.date_created))
		self.lb_created.SetLabel(date_created)

		if self._obj.date_modified:
			date_modified = time.strftime('%x %X',
					time.localtime(self._obj.date_modified))
		self.lb_modified.SetLabel(date_modified)

	def _fill_fields_clear(self):
		for field, ftype, _default, options in self._fields.itervalues():
			if field:
				if ftype == 'bool':
					field.SetValue(bool(_default))
				elif ftype == 'date':
					date = strdate2wxdate(_default)
					field.SetValue(date)
				elif ftype == 'list':
					field.SetStrings([_default])
				elif ftype == 'choice':
					if _default:
						field.SetStringSelection(_default)
					else:
						field.SetSelection(-1)
				else:
					field.SetValue(str(_default))
		self.tc_title.SetValue('')
		self.tc_tags.SetValue('')
		self.lb_modified.SetLabel('')
		self.lb_created.SetLabel('')

	def _on_expand_text(self, evt):
		self.Layout()
		self.GetParent().Refresh()
		self.SetupScrolling()


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
