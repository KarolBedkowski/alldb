# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009'
__version__ = '0.1'
__release__ = '2009-12-20'


import time
import wx
import wx.lib.scrolledpanel as scrolled
import wx.gizmos as gizmos
from wx.lib.expando import ExpandoTextCtrl, EVT_ETC_LAYOUT_NEEDED


class PanelInfo(scrolled.ScrolledPanel):
	def __init__(self, window, parent, obj_class, *argv, **kwarg):
		scrolled.ScrolledPanel.__init__(self, parent, -1, *argv, **kwarg)
		self._window = window
		self._obj = None
		self._obj_cls = obj_class
		self._fields = {}
		self._first_field = None

		self._COLOR_HIGHLIGHT_BG = wx.SystemSettings.GetColour(
				wx.SYS_COLOUR_HIGHLIGHT)
		self._COLOR_HIGHLIGHT_FG = wx.SystemSettings.GetColour(
				wx.SYS_COLOUR_HIGHLIGHTTEXT)

		main_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid.Add(self._create_fields_head(), 0, wx.EXPAND)
		grid = self._create_fields()
		main_grid.Add(grid, 0, wx.EXPAND | wx.ALL, 6)
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
					value = wxdate2strdate(field.GetValue())
				elif ftype == 'list':
					value = field.GetStrings()
				elif ftype == 'choice':
					value = field.GetStringSelection()
				else:
					value = field.GetValue()
				data[name] = value
		tags = self.tc_tags.GetValue()
		return data, tags

	def set_focus(self):
		if self._first_field:
			self._first_field.SetFocus()

	def _create_fields_head(self):
		panel = wx.Panel(self, -1)
		panel.SetBackgroundColour(self._COLOR_HIGHLIGHT_BG)

		grid = wx.BoxSizer(wx.HORIZONTAL)
		label = _create_label(panel, _('Title:'), self._COLOR_HIGHLIGHT_FG)
		grid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 6)

		self.tc_title = wx.StaticText(panel, -1, ' ')
		self.tc_title.SetForegroundColour(self._COLOR_HIGHLIGHT_FG)
		grid.Add(self.tc_title, 1, wx.EXPAND | wx.ALL, 6)

		panel.SetSizer(grid)
		panel.Show(self._obj_cls.title_show)
		return panel

	def _create_fields_tail(self):
		panel = wx.Panel(self, -1)
		panel.SetBackgroundColour(self._COLOR_HIGHLIGHT_BG)
		grid = wx.BoxSizer(wx.HORIZONTAL)

		def create(label):
			label = _create_label(panel, label, self._COLOR_HIGHLIGHT_FG)
			grid.Add(label, 0, wx.EXPAND | wx.ALL, 6)
			field = wx.StaticText(panel, -1, '          ')
			field .SetForegroundColour(self._COLOR_HIGHLIGHT_FG)
			grid.Add(field, 1, wx.EXPAND | wx.RIGHT | wx.TOP | wx.BOTTOM, 6)
			return field

		self.lb_created = create(_('Created:'))
		self.lb_modified = create(_('Modified:'))
		self.lb_id = create(_('ID:'))

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
			elif ftype == 'date':
				ctrl = wx.DatePickerCtrl(self, -1,
						style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)
			elif ftype == 'list':
				ctrl = gizmos.EditableListBox(self, -1)
			elif ftype == 'choice':
				values = options.get('values') or []
				ctrl = wx.Choice(self, -1, choices=values)
			else:
				ctrl = wx.TextCtrl(self, -1)
			self._fields[name] = (ctrl, ftype, _default, options)

			if ctrl:
				grid.Add(ctrl, 1, wx.EXPAND)
			else:
				grid.Add((1, 1))

			if not self._first_field:
				self._first_field = ctrl

		grid.Add(wx.StaticText(self, -1, _("Tags:")), 0, wx.ALIGN_CENTER_VERTICAL)
		grid.Add(self._create_fields_tag(self), 1, wx.EXPAND)

		return grid

	def _create_fields_tag(self, parent):
		box = wx.BoxSizer(wx.HORIZONTAL)
		self.tc_tags = wx.TextCtrl(parent, -1)
		box.Add(self.tc_tags, 1, wx.EXPAND)
		box.Add((6, 6))
		btn_choice_tags = wx.Button(parent, -1, _('Select'))
		box.Add(btn_choice_tags)
		self.Bind(wx.EVT_BUTTON, self._on_btn_choice_tags, btn_choice_tags)
		return box

	def _fill_fields_from_obj(self):
		obj = self._obj
		for name, (field, ftype, _default, options) in self._fields.iteritems():
			if not field:
				continue
			value = obj.data.get(name)
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
				field.SetValue(unicode(value or ''))
		self.tc_title.SetLabel(obj.title or '')
		self.tc_tags.SetValue(obj.tags_str)
		if obj.oid:
			self.lb_created.SetLabel(format_date(obj.created))
		else:
			self.lb_created.SetLabel(_('not saved'))
		self.lb_modified.SetLabel(format_date(obj.updated))
		self.lb_id.SetLabel(str(obj.oid or _("new")))

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
		self.lb_id.SetLabel('')

	def _on_expand_text(self, evt):
		self.Layout()
		self.GetParent().Refresh()
		self.SetupScrolling()

	def _on_btn_choice_tags(self, evt):
		cls_tags = self._window.current_tags.copy()
		item_tags_str = self.tc_tags.GetValue()
		item_tags = []
		if item_tags_str:
			item_tags = [t.strip() for t in item_tags_str.split(',')]
			for tag in item_tags:
				cls_tags[tag] = None

		if cls_tags:
			tag_list = sorted(cls_tags.iterkeys())
			dlg = wx.MultiChoiceDialog(self, _("Select tags"), _("Tags"), tag_list)
			selected = [idx for idx, key in enumerate(tag_list) if key in item_tags]
			dlg.SetSelections(selected)
			if dlg.ShowModal() == wx.ID_OK:
				selections = dlg.GetSelections()
				tags = ', '.join(sorted((tag_list[idx] for idx in selections)))
				self.tc_tags.SetValue(tags)
			dlg.Destroy()


def _create_label(parent, label, colour=None):
	label = wx.StaticText(parent, -1, label)
	if colour:
		label.SetForegroundColour(colour)
	font = label.GetFont()
	font.SetWeight(wx.FONTWEIGHT_BOLD)
	label.SetFont(font)
	return label


def strdate2wxdate(strdate):
	date = wx.DateTime()
	if strdate:
		try:
			date.ParseDate(strdate)
		except Exception, err:
			print err
	return date


def wxdate2strdate(wxdate):
	return wxdate.Format() if wxdate else None


def format_label(label):
	label = label.strip()
	label = label[0].upper() + label[1:]
	label.replace('_', ' ')
	return label


def format_date(date):
	if date:
		return time.strftime('%x %X', time.localtime(date))
	return '-'


def find_objs_commons(objs):
	fields = dict(objs[0].data)
	for obj in objs:
		if not obj.data:
			continue
		for key, val in obj.data.iteritems():
			if fields.get(key) is None:
				continue
			if fields[key] != val:
				fields[key] = None
	return fields



# vim: encoding=utf8: ff=unix: