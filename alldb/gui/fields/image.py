# -*- coding: utf-8 -*-

"""
"""
from __future__ import with_statement

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-05-14"


import cStringIO

import wx
import wx.lib.imagebrowser as imgbr

from alldb.gui.fields._field import Field


class ImageField(Field):
	field_type = 'image'
	result_type = 'blob'

	def __init__(self, parent, name, options, default, result_obj):
		Field.__init__(self, parent, name, options, default, result_obj)
		self._blob = None

	def _create_widget(self, parent, options, result_obj):
		width_height = (int(options.get('width', 100)),
				int(options.get('height', 100)))
		ctrl = wx.StaticBitmap(parent, -1, size=width_height)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(ctrl, 1, wx.EXPAND)
		box.Add((6, 6))
		bbox = wx.FlexGridSizer(3, 1, 6, 6)
		bbox.AddGrowableRow(0)
		bbox.Add((1, 1), 1)
		btn = wx.Button(parent, -1, _('Select'))
		btn.Bind(wx.EVT_BUTTON, self._on_btn_image_select)
		bbox.Add(btn)
		btn = wx.Button(parent, -1, _('Clear'))
		btn.Bind(wx.EVT_BUTTON, self._on_btn_image_clear)
		bbox.Add(btn)
		box.Add(bbox, 0, wx.EXPAND)
		self._panel = box
		return ctrl

	def set_object(self, obj):
		self._blob = obj.get_blob(self.name)
		self._widget_set_value(self._blob)

	def _widget_get_value(self):
		return self._blob

	def _widget_set_value(self, value):
		img = None
		if value:
			img = wx.ImageFromStream(cStringIO.StringIO(value))
		if img is None or not img.IsOk():
			img = wx.EmptyImage(1, 1)
			self._widget.Show(False)
		else:
			bmp = img.ConvertToBitmap()
			self._widget.SetBitmap(bmp)
			self._widget.Show(True)
			self._widget.SetSize((img.GetWidth(), img.GetHeight()))
			self._widget.GetParent().Layout()
			self._widget.GetParent().Refresh()

	def _widget_del_value(self):
		self._widget_set_value(None)

	def _on_btn_image_select(self, evt):
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
		dlg.Destroy()

	def _on_btn_image_clear(self, evt):
		self._blob = None
		self._widget_set_value(None)


# vim: encoding=utf8: ff=unix:
