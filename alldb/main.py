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

from alldb.gui.FrameMain import FrameMain
from alldb.libs.appconfig import AppConfig
from alldb.model.db import Db


def run():
	config = AppConfig(__file__, 'alldb')
	config.load()
	db_filename = os.path.join(config.path_share, 'alldb.db')

	gettext.install("alldb", unicode=True)
	try:
		locale.setlocale(locale.LC_ALL, "")
	except locale.Error, e:
		print e
	wxlocale = wx.Locale(wx.LANGUAGE_DEFAULT)
	wxlocale.AddCatalog('alldb')

	db = Db(db_filename)
	db.open()

	config['_DB'] = db

	app = wx.PySimpleApp(0)
	wx.InitAllImageHandlers()
	main_frame = FrameMain(db)
	app.SetTopWindow(main_frame)
	main_frame.Show()
	app.MainLoop()

	db.close()
	config.save()






# vim: encoding=utf8: ff=unix:
