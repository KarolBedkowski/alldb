# -*- coding: utf-8 -*-

"""
"""
from __future__ import with_statement

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009'
__version__ = '0.1'
__release__ = '2009-12-20'


import os.path
import time
import cStringIO
import threading

import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.newevent
import wx.lib.imagebrowser as imgbr
import wx.gizmos as gizmos
from wx.lib.expando import ExpandoTextCtrl, EVT_ETC_LAYOUT_NEEDED

from alldb.gui.dlg_select_tags import DlgSelectTags


(RecordUpdatedEvent, EVT_RECORD_UPDATED) = wx.lib.newevent.NewEvent()


class PanelInfo(scrolled.ScrolledPanel):
	def __init__(self, window, parent, obj_class, *argv, **kwarg):
		scrolled.ScrolledPanel.__init__(self, parent, -1, *argv, **kwarg)
		self._window = window
		self._obj = None
		self._obj_cls = obj_class
		self._fields = {}
		self._blobs = {}
		self._first_field = None
		self._last_dir = os.path.expanduser('~')
		self._update_timer = None
		self._obj_showed = False

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
		self._obj_showed = False
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
				elif ftype == 'image':
					value = len(self._blobs[name]) if self._blobs[name] else 0
				else:
					value = field.GetValue()
				data[name] = value
		tags = self.tc_tags.GetValue()
		return data, tags, self._blobs

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
		for idx, (name, ftype, _default, options) in enumerate(self._obj_cls.fields):
			grid.Add(wx.StaticText(self, -1, "%s:" % format_label(name)), 0,
					wx.ALIGN_CENTER_VERTICAL)
			ctrl = None
			box = None
			if ftype == 'bool':
				ctrl = wx.CheckBox(self, -1)
				ctrl.Bind(wx.EVT_CHECKBOX , self._on_field_update)
			elif ftype == 'multi':
				ctrl = ExpandoTextCtrl(self, -1, size=(-1, 50))
				ctrl.Bind(wx.EVT_TEXT, self._on_field_update)
				ctrl.Bind(EVT_ETC_LAYOUT_NEEDED, self._on_expand_text)
				grid.AddGrowableRow(idx)
			elif ftype == 'date':
				ctrl = wx.DatePickerCtrl(self, -1,
						style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE)
			elif ftype == 'list':
				ctrl = gizmos.EditableListBox(self, -1)
			elif ftype == 'choice':
				values = options.get('values') or []
				ctrl = wx.Choice(self, -1, choices=values)
				ctrl.Bind(wx.EVT_CHOICE, self._on_field_update)
			elif ftype == 'image':
				ctrl, box = self._create_field_image(name, options)
			else:
				ctrl = wx.TextCtrl(self, -1)
				ctrl.Bind(wx.EVT_TEXT, self._on_field_update)
			self._fields[name] = (ctrl, ftype, _default, options)

			if ctrl:
				if box is None:
					box = ctrl
				grid.Add(box, 1, wx.EXPAND)
			else:
				grid.Add((1, 1))

			if not self._first_field:
				self._first_field = ctrl

		grid.Add(wx.StaticText(self, -1, _("Tags:")), 0, wx.ALIGN_CENTER_VERTICAL)
		grid.Add(self._create_fields_tag(self), 1, wx.EXPAND)
		return grid

	def _create_field_image(self, name, options):
		width_height = int(options.get('width', 100)), int(options.get('height', 100))
		ctrl = wx.StaticBitmap(self, -1, size=width_height)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(ctrl, 1, wx.EXPAND)
		box.Add((6, 6))
		bbox = wx.FlexGridSizer(3, 1, 6, 6)
		bbox.AddGrowableRow(0)
		bbox.Add((1, 1), 1)
		btn = wx.Button(self, -1, _('Select'))
		btn._ctrl = (name, ctrl)
		btn.Bind(wx.EVT_BUTTON, self._on_btn_image_select)
		bbox.Add(btn)
		btn = wx.Button(self, -1, _('Clear'))
		btn._ctrl = (name, ctrl)
		btn.Bind(wx.EVT_BUTTON, self._on_btn_image_clear)
		bbox.Add(btn)
		box.Add(bbox, 0, wx.EXPAND)
		return ctrl, box

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
			elif ftype == 'image':
				img = obj.get_blob(name)
				self._show_image(field, img, options)
				self._blobs[name] = img
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
		self._obj_showed = True

	def _fill_fields_clear(self):
		self._blobs = {}
		self._obj_showed = False

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
				elif ftype == 'image':
					self._show_image(field, None, options)
				else:
					field.SetValue(str(_default))

		self.tc_title.SetValue('')
		self.tc_tags.SetValue('')
		self.lb_modified.SetLabel('')
		self.lb_created.SetLabel('')
		self.lb_id.SetLabel('')

	def _show_image(self, ctrl, img, options):
		if img:
			img = wx.ImageFromStream(cStringIO.StringIO(img))
		if img is None or not img.IsOk():
			img = wx.EmptyImage(1, 1)
			ctrl.Show(False)
		else:
			bmp = img.ConvertToBitmap()
			ctrl.SetBitmap(bmp)
			ctrl.Show(True)
			ctrl.SetSize((img.GetWidth(), img.GetHeight()))
		self.Layout()
		self.Refresh()

	def _on_expand_text(self, evt):
		self.Layout()
		self.GetParent().Refresh()
		self.SetupScrolling()
		evt.Skip()

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

	def _on_btn_image_select(self, evt):
		btn = evt.GetEventObject()
		name, ctrl = btn._ctrl
		dlg = imgbr.ImageDialog(self, self._last_dir)
		if dlg.ShowModal() == wx.ID_OK:
			filename = dlg.GetFile()
			data = None
			img = wx.Image(filename)
			if img:
				opt = self._fields[name][3] or {}
				width, height = opt.get('width'), opt.get('height')
				if width and height:
					width, height = int(width), int(height)
					if width < img.GetWidth() or height < img.GetHeight():
						scale = min(float(width) / img.GetWidth(),
								float(height) / img.GetHeight())
						img = img.Scale(int(img.GetWidth() * scale),
								int(img.GetHeight() * scale))
				output = cStringIO.StringIO()
				img.SaveStream(output, wx.BITMAP_TYPE_JPEG)
				data = self._blobs[name] = output.getvalue()
				self._show_image(ctrl, data, opt)
			self._last_dir = os.path.dirname(filename)
		dlg.Destroy()

	def _on_btn_image_clear(self, evt):
		btn = evt.GetEventObject()
		name, ctrl = btn._ctrl
		self._blobs[name] = None
		self._show_image(ctrl, None, self._fields[name][3])

	def _on_field_update(self, evt):
		if self._update_timer is not None:
			self._update_timer.cancel()
		if not self._obj_showed:
			return
		self._update_timer = threading.Timer(0.5, self._on_timer_update)
		self._update_timer.start()

	def _on_timer_update(self):
		try:
			wx.PostEvent(self._window.wnd, RecordUpdatedEvent(obj=self._obj))
		finally:
			pass


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
