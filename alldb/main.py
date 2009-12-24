# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__revision__	= '2009-11-12'


import gettext
import wx

from gui.MainFrame import MainFrame


def run():
	gettext.install("alldb")

	app = wx.PySimpleApp(0)
	wx.InitAllImageHandlers()
	main_frame = MainFrame()
	app.SetTopWindow(main_frame)
	main_frame.Show()
	app.MainLoop()






# vim: encoding=utf8: ff=unix:
