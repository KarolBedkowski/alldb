# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009'
__revision__ = '2009-11-12'


import os
import gettext
import locale

import logging
_LOG = logging.getLogger(__name__)

from alldb.gui.FrameMain import FrameMain
from alldb.libs import appconfig
from alldb.libs.logging_setup import logging_setup
from alldb.model.db import Db

import sys
reload(sys)
try:
	sys.setappdefaultencoding("utf-8")
except Exception, _:
	sys.setdefaultencoding("utf-8")

# logowanie
DEBUG = sys.argv.count('-d') > 0
if DEBUG:
	sys.argv.remove('-d')
logging_setup('alldb.log', DEBUG)


def _setup_locale():
	''' setup locales and gettext '''
	use_home_dir = sys.platform != 'winnt'
	app_config = appconfig.AppConfig('alldb.cfg', __file__, use_home_dir=use_home_dir,
			app_name='alldb')
	locales_dir = app_config.locales_dir
	package_name = 'alldb'
	_LOG.info('run: locale dir: %s' % locales_dir)
	try:
		locale.bindtextdomain(package_name, locales_dir)
		locale.bind_textdomain_codeset(package_name, "UTF-8")
	except:
		pass
	default_locale = locale.getdefaultlocale()
	locale.setlocale(locale.LC_ALL, '')
	os.environ['LC_ALL'] = os.environ.get('LC_ALL') or default_locale[0]
	gettext.install(package_name, localedir=locales_dir, unicode=True,
			names=("ngettext",))
	gettext.bindtextdomain(package_name, locales_dir)
	gettext.bind_textdomain_codeset(package_name, "UTF-8")

	_LOG.info('locale: %s' % str(locale.getlocale()))


_setup_locale()


if not appconfig.is_frozen():
	try:
		import wxversion
		try:
			wxversion.select('2.8')
		except wxversion.AlreadyImportedError:
			pass
	except ImportError, err:
		print 'No wxversion.... (%s)' % str(err)

import wx


def run():
	config = appconfig.AppConfig(__file__, 'alldb')
	config.load()
	config.debug = DEBUG
	db_filename = os.path.join(config.path_share, 'alldb.db')

	app = wx.PySimpleApp(0)

	db = Db(db_filename)
	db.open()

	config['_DB'] = db

	wx.InitAllImageHandlers()
	main_frame = FrameMain(db)
	app.SetTopWindow(main_frame)
	main_frame.Show()
	app.MainLoop()

	db.close()
	config.save()






# vim: encoding=utf8: ff=unix:
