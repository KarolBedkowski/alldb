# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009'
__version__ = '0.1'
__release__ = '2009-12-20'


import wx
from wx import xrc

from alldb.libs import wxresources
from alldb.gui.dialogs import message_boxes as msgbox

from .dlg_edit_field import DlgEditField


class DlgEditClass(object):
	def __init__(self, parent, cls, cls_names):
		self.res = wxresources.load_xrc_resource('alldb.xrc')
		self._load_controls(parent)
		self._create_bindings()
		self._setup(cls, cls_names)

	def run(self):
		res = self.wnd.ShowModal() == wx.ID_OK
		self.wnd.Destroy()
		return res

	def _load_controls(self, parent):
		self.wnd = self.res.LoadDialog(parent, 'dlg_edit_class')
		assert self.wnd is not None
		self.lc_fields = xrc.XRCCTRL(self.wnd, 'lc_fields')
		self.tc_name = xrc.XRCCTRL(self.wnd, 'tc_name')
		self.tc_title = xrc.XRCCTRL(self.wnd, 'tc_title')
		self.cb_show_title = xrc.XRCCTRL(self.wnd, 'cb_show_title')
		self.cb_title_auto = xrc.XRCCTRL(self.wnd, 'cb_title_auto')
		self.cb_title_in_list = xrc.XRCCTRL(self.wnd, 'cb_title_in_list')
		self.btn_del_field = xrc.XRCCTRL(self.wnd, 'wxID_DELETE')
		self.btn_add_field = xrc.XRCCTRL(self.wnd, 'wxID_ADD')
		self.btn_up = xrc.XRCCTRL(self.wnd, 'wxID_UP')
		self.btn_down = xrc.XRCCTRL(self.wnd, 'wxID_DOWN')

	def _setup(self, cls, cls_names):
		self._cls = cls
		self._cls_names = cls_names

		self._type_names = {
				'str': _('string'),
				'bool': _('boolean'),
				'date': _('date'),
				'multi': _('multi line'),
				'list': _('list'),
				'choice': _('choice'),
				'image': _('image')}

		lc_fields = self.lc_fields
		lc_fields.InsertColumn(0, _('No'))
		lc_fields.InsertColumn(1, _('Name'))
		lc_fields.InsertColumn(2, _('Type'))
		lc_fields.InsertColumn(3, _('Default value'))
		lc_fields.InsertColumn(4, _('Options'))

		self._show_class(cls)
		self._set_buttons_status()
		self.wnd.Centre(wx.BOTH)

	def _create_bindings(self):
		wnd = self.wnd
		wnd.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
		wnd.Bind(wx.EVT_BUTTON, self._on_close, id=wx.ID_CANCEL)
		wnd.Bind(wx.EVT_CHECKBOX, self._on_item_have_title_checkbox,
				self.cb_show_title)
		wnd.Bind(wx.EVT_CHECKBOX, self._on_title_auto, self.cb_title_auto)
		wnd.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_fields_deselected,
				self.lc_fields)
		wnd.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_fields_selected, self.lc_fields)
		wnd.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_fields_activated,
				self.lc_fields)
		wnd.Bind(wx.EVT_BUTTON, self._on_btn_add_field, id=wx.ID_ADD)
		wnd.Bind(wx.EVT_BUTTON, self._on_btn_del_field, id=wx.ID_DELETE)
		wnd.Bind(wx.EVT_BUTTON, self._on_button_up, id=wx.ID_UP)
		wnd.Bind(wx.EVT_BUTTON, self._on_button_down, id=wx.ID_DOWN)

	def _show_class(self, cls):
		self.tc_name.SetValue(str(cls.name or ''))
		self.tc_title.SetValue(str(cls.title_expr))
		self._refresh_list(cls)
		self._show_title(cls)
		self.cb_show_title.SetValue(cls.title_show)
		self.cb_title_auto.SetValue(cls.title_auto)
		self.cb_title_auto.Enable(cls.title_show)
		self.cb_title_in_list.Enable(cls.title_show)
		self.tc_title.Enable(not cls.title_auto and cls.title_show)

	def _show_title(self, cls):
		if cls['title_auto']:
			self.tc_title.Enable(True)
			self.cb_title_auto.SetValue(cls.title_auto)
			self.tc_title.Enable(False)
		self.tc_title.Enable(not cls.title_auto)

	def _refresh_list(self, cls):
		lc_fields = self.lc_fields
		lc_fields.DeleteAllItems()
		for no, (name, ftype, default, options) in enumerate(cls.fields):
			lc_fields.InsertStringItem(no, str(no + 1))
			lc_fields.SetStringItem(no, 1, str(name))
			lc_fields.SetStringItem(no, 2, str(self._type_names.get(ftype, ftype)))
			lc_fields.SetStringItem(no, 3, str(default or ''))
			if options:
				opt_str = _options2string(options)
				lc_fields.SetStringItem(no, 4, opt_str)
		lc_fields.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		lc_fields.SetColumnWidth(1, wx.LIST_AUTOSIZE)
		lc_fields.SetColumnWidth(2, wx.LIST_AUTOSIZE)
		lc_fields.SetColumnWidth(3, wx.LIST_AUTOSIZE)
		lc_fields.SetColumnWidth(4, wx.LIST_AUTOSIZE)

	def _on_item_have_title_checkbox(self, event):
		have_title = self.cb_show_title.IsChecked()
		self.cb_title_auto.Enable(have_title)
		self.cb_title_in_list.Enable(have_title)
		if have_title:
			title_auto = self.cb_title_auto.IsChecked()
			self.tc_title.Enable(not title_auto)
		else:
			self.tc_title.Enable(False)

	def _on_btn_title_refresh(self, event):
		if self._cls.fields:
			self.tc_title.SetValue('%%%s' % self._cls.fields[0][0])

	def _on_title_auto(self, event):
		title_auto = self.cb_title_auto.IsChecked()
		self._cls.title_auto = title_auto
		if title_auto:
			self.tc_title.SetValue(self._cls.gen_auto_title())
		self.tc_title.Enable(not title_auto)

	def _on_fields_deselected(self, event):
		self._set_buttons_status()

	def _on_fields_selected(self, event):
		self._set_buttons_status()

	def _on_fields_activated(self, event):
		item_idx = self._get_selected_field_idx()
		if item_idx < 0:
			return
		field = self._cls.fields[item_idx]
		name = field[0]
		data = dict(name=name, type=field[1], default=field[2], options=field[3])
		data['_fields_names'] = [field[0] for field in self._cls.fields
				if field[0] != name]
		dlg = DlgEditField(self.wnd, data)
		if dlg.run():
			field = (data['name'], data['type'], data['default'], data['options'])
			self._cls.fields[item_idx] = field
			self._refresh_list(self._cls)
			self._on_title_auto(None)

	def _on_btn_add_field(self, event):
		data = {}
		data['_fields_names'] = [field[0] for field in self._cls.fields]
		dlg = DlgEditField(self.wnd, data)
		if dlg.run():
			field = (data['name'], data['type'], data['default'], data['options'])
			self._cls.fields.append(field)
			self._refresh_list(self._cls)
			self._on_title_auto(None)

	def _on_btn_del_field(self, event):
		item_idx = self._get_selected_field_idx()
		if item_idx < 1:
			return
		if msgbox.message_box_delete_confirm(self.wnd, _('field')):
			self._cls.fields.pop(item_idx)
			self._refresh_list(self._cls)
			self._on_title_auto(None)

	def _on_button_up(self, event):
		item_idx = self._get_selected_field_idx()
		if item_idx < 1:
			return
		fields = self._cls.fields
		fields[item_idx], fields[item_idx - 1] = (fields[item_idx - 1],
				fields[item_idx])
		self._refresh_list(self._cls)
		self.lc_fields.SetItemState(item_idx - 1, wx.LIST_STATE_SELECTED,
				wx.LIST_STATE_SELECTED)
		self._on_title_auto(None)

	def _on_button_down(self, event):
		item_idx = self._get_selected_field_idx()
		if item_idx < 0 or item_idx == self.lc_fields.GetItemCount() - 1:
			return
		fields = self._cls.fields
		fields[item_idx], fields[item_idx + 1] = (fields[item_idx + 1],
				fields[item_idx])
		self._refresh_list(self._cls)
		self.lc_fields.SetItemState(item_idx + 1, wx.LIST_STATE_SELECTED,
				wx.LIST_STATE_SELECTED)
		self._on_title_auto(None)

	def _on_ok(self, evt):
		name = self.tc_name.GetValue()
		title_expr = self.tc_title.GetValue()
		if not (name and title_expr):
			msgbox.message_box_error_ex(self.wnd, _('Name and title fields are empty.'),
					_('Both fields must have defined values.'))
		if name in self._cls_names:
			msgbox.message_box_error_ex(self.wnd, _('Cannot save class'),
					_('Category with this name already exists.\nPlease specify other name.'))
			return
		self._cls.name = name
		self._cls.title_expr = title_expr
		self._cls.title_show = self.cb_show_title.IsChecked()
		self.wnd.EndModal(wx.ID_OK)

	def _on_close(self, event):
		self.wnd.EndModal(wx.ID_CLOSE)

	def _get_selected_field_idx(self):
		if self.lc_fields.GetSelectedItemCount() == 0:
			return -1
		return self.lc_fields.GetNextItem(-1, wx.LIST_NEXT_ALL,
				wx.LIST_STATE_SELECTED)

	def _set_buttons_status(self):
		selected_item = self.lc_fields.GetSelectedItemCount() > 0
		self.btn_del_field.Enable(selected_item)
		self.btn_up.Enable(selected_item)
		self.btn_down.Enable(selected_item)


def _options2string(options):
	result = []
	if options.get('in_title'):
		result.append(_('in title'))
	if options.get('in_list'):
		result.append(_('show in list'))
	return ', '.join(result)


# vim: encoding=utf8: ff=unix:
