# -*- coding: utf-8 -*-

"""
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-05-06"


import wx
from wx import xrc


def optimize_db(parent, database):
	dlg = wx.ProgressDialog(_("Optimize database"), _("Optimization started"),
			parent=parent)
	dlg.SetSize((300, -1))
	dlg.Show()
	database.optimize(dlg.Pulse)
	dlg.Destroy()

# vim: encoding=utf8: ff=unix:
