# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__revision__	= '2009-11-12'


import os
import gettext
import locale

import wx

from gui.FrameMain import FrameMain

from libs.appconfig import AppConfig


def run():
	config = AppConfig(__file__, 'alldb')
	db_filename = os.path.join(config.path_share, 'alldb.db')

	gettext.install("alldb", unicode=True)
	try:
		locale.setlocale(locale.LC_ALL, "")
	except locale.Error, e:
		print e

	app = wx.PySimpleApp(0)
	wx.InitAllImageHandlers()
	main_frame = FrameMain(db_filename)
	app.SetTopWindow(main_frame)
	main_frame.Show()
	app.MainLoop()






# vim: encoding=utf8: ff=unix:
