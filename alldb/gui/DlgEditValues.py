# -*- coding: utf-8 -*-
import wx
import wx.gizmos as gizmos


class DlgEditValues(wx.Dialog):
	def __init__(self, parent, data):
		wx.Dialog.__init__(self, parent, -1, 
				style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME)
		self.SetTitle(_("Values"))

		self._data = data

		grid = wx.BoxSizer(wx.VERTICAL)
		self._elb = gizmos.EditableListBox(self, -1, size=(100, 300),
				style=gizmos.EL_ALLOW_NEW|gizmos.EL_ALLOW_EDIT|gizmos.EL_ALLOW_DELETE)
		grid.Add(self._elb, 1, wx.EXPAND|wx.ALL, 6)
		grid.Add(self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL), 
				0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 6)
		self.SetSizer(grid)
		self.Center(wx.BOTH)
		
		self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)

		self._elb.SetStrings(data.get('values') or [])

	def _on_ok(self, evt):
		self._data['values'] = self._elb.GetStrings()
		self.EndModal(wx.ID_OK)






