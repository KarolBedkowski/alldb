# -*- coding: utf-8 -*-

"""
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2010"
__version__ = "2010-05-03"


import wx

from alldb import version
from alldb.libs.appconfig import AppConfig


class AllDbSplash(wx.SplashScreen):
	"""docstring for AllDbSplash"""
	def __init__(self):
		config = AppConfig()
		splash_img = wx.Image(config.get_data_file('splash.png'))
		wx.SplashScreen.__init__(self, splash_img.ConvertToBitmap(),
			wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,
			2000, None, -1)

		wnd = self.GetSplashWindow()
		wx.StaticText(wnd, -1, version.VERSION, pos=(260, 120))





# vim: encoding=utf8: ff=unix:
