# -*- coding: utf-8 -*-

"""
"""
from __future__ import with_statement

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (C) Karol Będkowski, 2009-2010"
__version__ = "2010-05-06"


import os.path
import time
import cStringIO

import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.newevent
import wx.lib.imagebrowser as imgbr
import wx.gizmos as gizmos
from wx.lib import masked

from alldb.gui.dlg_select_tags import DlgSelectTags
from alldb.gui.fields import FieldsFactory
from alldb.libs.textctrlautocomplete import TextCtrlAutoComplete


(RecordUpdatedEvent, EVT_RECORD_UPDATED) = wx.lib.newevent.NewEvent()
(SelectRecordEvent, EVT_SELECT_RECORD) = wx.lib.newevent.NewEvent()


class PanelInfo(scrolled.ScrolledPanel):
	def __init__(self, window, parent, obj_class, result, *argv, **kwarg):
		scrolled.ScrolledPanel.__init__(self, parent, -1,
				style=wx.FULL_REPAINT_ON_RESIZE)
		self._window = window
		self._obj = None
		self._obj_cls = obj_class
		self._fields = {}
		self._blobs = {}
		self._first_field = None
		self._last_dir = os.path.expanduser('~')
		self._update_timer = None
		self._obj_showed = False
		self._result = result

		self._COLOR_HIGHLIGHT_BG = wx.SystemSettings.GetColour(
				wx.SYS_COLOUR_HIGHLIGHT)
		self._COLOR_HIGHLIGHT_FG = wx.SystemSettings.GetColour(
				wx.SYS_COLOUR_HIGHLIGHTTEXT)

		main_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid.Add(self._create_fields_head(), 0, wx.EXPAND)
		grid = self._create_fields()
		main_grid.Add(grid, 0, wx.EXPAND | wx.ALL, 6)
		main_grid.Add(self._create_fields_tail(), 0, wx.EXPAND)
		self._main_grid = main_grid

		self.SetSizer(main_grid)
		self.SetAutoLayout(1)
		self.SetupScrolling()

	def update(self, obj):
		self._obj = obj
		self._obj_showed = False
		self.Freeze()
		if obj:
			self._fill_fields_from_obj()
		else:
			self._fill_fields_clear()
		self.SetupScrolling()
		if wx.Platform == '__WXMSW__':
			for field in self._fields.itervalues():
				field[0].widget.SetFocus()
		self.set_focus()
		self.Thaw()

	def update_base_info(self, obj):
		if self._obj.oid != obj.oid:
			return
		self.tc_title.SetLabel(obj.title or '')
		if obj.oid:
			self.lb_created.SetLabel(format_date(obj.created))
		else:
			self.lb_created.SetLabel(_('not saved'))
		self.lb_modified.SetLabel(format_date(obj.updated))
		self.lb_id.SetLabel(str(obj.oid or _("new")))

	def get_values(self):
		data = {}
		blobs = {}
		for name, (field, ftype, _default, options) in self._fields.iteritems():
			if field:
				value = field.value
				if field.result_type == 'blob':
					blobs[name] = value
				else:
					data[name] = value
		tags = self.tc_tags.GetValue()
		return data, tags, blobs

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
		for idx, (name, ftype, default, options) in enumerate(
				self._obj_cls.fields):
			grid.Add(wx.StaticText(self, -1, "%s:" % format_label(name)), 0,
					wx.ALIGN_CENTER_VERTICAL)
			field = FieldsFactory.get_class(ftype)(self, name, options, default,
					self._result)
			field.bind_on_change(self._on_field_update)
			field.bind(wx.EVT_CHAR, self._on_key_down)
			self._fields[name] = (field, ftype, default, options)

			if field:
				grid.Add(field.panel, 1, wx.EXPAND)
			else:
				grid.Add((1, 1))

			if not self._first_field:
				self._first_field = field.widget

		grid.Add(wx.StaticText(self, -1, _("Tags:")), 0, wx.ALIGN_CENTER_VERTICAL)
		grid.Add(self._create_fields_tag(self), 1, wx.EXPAND)
		return grid

	def _create_fields_tag(self, parent):
		box = wx.BoxSizer(wx.HORIZONTAL)
		box1 = wx.BoxSizer(wx.VERTICAL)
		self.tc_tags = wx.TextCtrl(parent, -1)
		box1.Add(self.tc_tags, 1, wx.EXPAND)
		box.Add(box1, 1, wx.ALIGN_CENTER_VERTICAL)
		box.Add((6, 6))
		btn_choice_tags = wx.Button(parent, -1, _('Select'))
		box.Add(btn_choice_tags)
		self.Bind(wx.EVT_BUTTON, self._on_btn_choice_tags, btn_choice_tags)
		self.tc_tags.Bind(wx.EVT_TEXT, self._on_field_update)
		return box

	def _fill_fields_from_obj(self):
		obj = self._obj
		for name, (field, ftype, _default, options) in self._fields.iteritems():
			field.set_object(obj)
		self.tc_tags.SetValue(obj.tags_str)
		self.update_base_info(obj)
		self._obj_showed = True

	def _fill_fields_clear(self):
		self._blobs = {}
		self._obj_showed = False
		for field, ftype, _default, options in self._fields.itervalues():
			field.clear()
		self.tc_title.SetValue('')
		self.tc_tags.SetValue('')
		self.lb_modified.SetLabel('')
		self.lb_created.SetLabel('')
		self.lb_id.SetLabel('')

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
			dlg = DlgSelectTags(self, tag_list, item_tags)
			if dlg.run():
				self.tc_tags.SetValue(', '.join(sorted(dlg.selected)))

	def _on_field_update(self, evt):
		if self._obj_showed:
			if self._update_timer:
				self._update_timer.Stop()
			self._update_timer = wx.CallLater(500, self._on_timer_update)
		evt.Skip()

	def _on_timer_update(self):
		try:
			wx.PostEvent(self._window.wnd, RecordUpdatedEvent(obj=self._obj))
		finally:
			pass

	def _on_key_down(self, event):
		if event.GetModifiers() == wx.MOD_CONTROL:
			keycode = event.GetKeyCode()
			try:
				if keycode == wx.WXK_UP:
					wx.PostEvent(self._window.wnd, SelectRecordEvent(
							direction=-1))
					return
				elif keycode == wx.WXK_DOWN:
					wx.PostEvent(self._window.wnd, SelectRecordEvent(
							direction=1))
					return
			finally:
				pass
		event.Skip()


def _create_label(parent, label, colour=None):
	label = wx.StaticText(parent, -1, label)
	if colour:
		label.SetForegroundColour(colour)
	font = label.GetFont()
	font.SetWeight(wx.FONTWEIGHT_BOLD)
	label.SetFont(font)
	return label


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
