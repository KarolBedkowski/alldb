# -*- coding: utf-8 -*-

"""
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-05-24"


import wx
from wx import xrc

from alldb.libs import wxresources
from alldb.gui.dialogs import message_boxes as msgbox


class DlgSelectTags(object):
	def __init__(self, parent, all_tags, selected_tags):
		self.res = wxresources.load_xrc_resource('alldb.xrc')
		self._load_controls(parent)
		self._create_bindings()
		self._setup(all_tags, selected_tags)

	def run(self):
		res = self.wnd.ShowModal() == wx.ID_OK
		self.wnd.Destroy()
		return res

	@property
	def selected(self):
		for idx, item in enumerate(self._clb_tags.GetItems()):
			if self._clb_tags.IsChecked(idx):
				yield item

	def _load_controls(self, parent):
		self.wnd = self.res.LoadDialog(parent, 'dlg_select_tags')
		assert self.wnd is not None
		self._clb_tags = xrc.XRCCTRL(self.wnd, 'clb_tags')
		self._tc_new_tag = xrc.XRCCTRL(self.wnd, 'tc_new_tag')
		self._btn_add_tag = xrc.XRCCTRL(self.wnd, 'btn_add_tag')

	def _create_bindings(self):
		wnd = self.wnd
		xrc.XRCCTRL(wnd, 'wxID_OK').Bind(wx.EVT_BUTTON, self._on_ok)
		xrc.XRCCTRL(wnd, 'wxID_CANCEL').Bind(wx.EVT_BUTTON, self._on_cancel)
		wnd.Bind(wx.EVT_BUTTON, self._on_btn_add_tag, self._btn_add_tag)

	def _setup(self, all_tags, selected_tags):
		for tag in all_tags:
			idx = self._clb_tags.Append(tag)
			if tag in selected_tags:
				self._clb_tags.Check(idx)

	def _on_ok(self, _event):
		self.wnd.EndModal(wx.ID_OK)

	def _on_cancel(self, _event):
		self.wnd.EndModal(wx.ID_CANCEL)

	def _on_btn_add_tag(self, _event):
		tag = self._tc_new_tag.GetValue().strip()
		if tag:
			if tag in self._clb_tags.GetItems():
				msgbox.message_box_info_ex(self.wnd, _('Can not add this tag'),
						_('Entered tag already exists on the list.'))
				return
			idx = self._clb_tags.Append(tag)
			self._clb_tags.Check(idx)
		self._tc_new_tag.SetValue('')




# vim: encoding=utf8: ff=unix:
