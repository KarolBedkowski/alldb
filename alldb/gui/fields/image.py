# -*- coding: utf-8 -*-

"""
"""
from __future__ import with_statement

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-05-24"


import cStringIO

import wx
import wx.lib.imagebrowser as imgbr
import wx.lib.newevent

from alldb.gui.dialogs import message_boxes as msgbox
from alldb.gui.fields._field import Field


(UpdatedEvent, EVT_UPDATED) = wx.lib.newevent.NewEvent()


class ImageField(Field):
	field_type = 'image'
	result_type = 'blob'
	_on_change_event = EVT_UPDATED

	def __init__(self, parent, name, options, default, result_obj):
		self._btn_select = None
		self._btn_clear = None
		Field.__init__(self, parent, name, options, default, result_obj)
		self._blob = None

	def _create_widget(self, parent, options, _result_obj):
		width_height = (int(options.get('width', 100)),
				int(options.get('height', 100)))
		self._panel = panel = wx.Panel(parent, -1)
		ctrl = wx.StaticBitmap(panel, -1, size=width_height)
		ctrl.Bind(wx.EVT_CONTEXT_MENU, self._on_image_context_menu)
		self._btn_select = btn = wx.Button(panel, -1, _('Select'))
		btn.Bind(wx.EVT_BUTTON, self._on_btn_image_select)
		return ctrl

	def set_object(self, obj):
		self._blob = obj.get_blob(self.name)
		self._widget_set_value(self._blob)

	def bind_on_change(self, method):
		self.widget.Bind(self._on_change_event, method)

	def _widget_get_value(self):
		return self._blob

	def _widget_set_value(self, value):
		img = None
		if value:
			img = wx.ImageFromStream(cStringIO.StringIO(value))
		if img is None or not img.IsOk():
			img = None
			self._widget.Show(False)
		else:
			bmp = img.ConvertToBitmap()
			self._widget.SetBitmap(bmp)
			self._widget.Show(True)
			self._widget.SetSize((img.GetWidth(), img.GetHeight()))
		self._btn_select.Show(img is None)
		self._panel.GetParent().Layout()
		self._panel.GetParent().Refresh()

	def _widget_del_value(self):
		self._widget_set_value(None)

	def _on_btn_image_select(self, _evt):
		dlg = imgbr.ImageDialog(self._widget)
		if dlg.ShowModal() == wx.ID_OK:
			filename = dlg.GetFile()
			img = wx.Image(filename)
			if img:
				opt = self.options
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
				self._blob = output.getvalue()
				self._widget_set_value(self._blob)
				wx.PostEvent(self._widget, UpdatedEvent())
		dlg.Destroy()

	def _on_btn_image_clear(self, _evt):
		if msgbox.message_box_delete_confirm(self._widget, _("image")):
			self._blob = None
			self._widget_set_value(None)
			self._btn_select.Show(True)
			wx.PostEvent(self._widget, UpdatedEvent())

	def _on_image_context_menu(self, _evt):
		menu = wx.Menu()
		item = wx.MenuItem(menu, 10001, _("Clear"))
		menu.AppendItem(item)
		self._widget.Bind(wx.EVT_MENU, self._on_btn_image_clear, id=10001)
		self._widget.PopupMenu(menu)
		menu.Destroy()


# vim: encoding=utf8: ff=unix:
