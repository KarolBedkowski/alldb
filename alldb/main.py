# -*- coding: utf-8 -*-

"""
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-05-24"


import os
import gettext
import locale
import optparse
import logging

import sys
reload(sys)
try:
	sys.setappdefaultencoding("utf-8")
except AttributeError:
	sys.setdefaultencoding("utf-8")


_LOG = logging.getLogger(__name__)


def show_version(*_args, **_kwargs):
	from alldb import version
	print version.INFO
	exit(0)


def _parse_opt():
	optp = optparse.OptionParser()
	optp.add_option('--debug', '-d', action="store_true", default=False,
			help='enable debug messages')
	optp.add_option('--version', action="callback", callback=show_version,
		help='show information about application version')
	return optp.parse_args()[0]

_OPTIONS = _parse_opt()

# logowanie
from alldb.libs.logging_setup import logging_setup
logging_setup('alldb.log', _OPTIONS.debug)


from alldb.libs import appconfig


def _setup_locale():
	''' setup locales and gettext '''
	app_config = appconfig.AppConfig('alldb.cfg', 'alldb')
	locales_dir = app_config.locales_dir
	package_name = 'alldb'
	_LOG.info('run: locale dir: %s' % locales_dir)
	try:
		locale.bindtextdomain(package_name, locales_dir)
		locale.bind_textdomain_codeset(package_name, "UTF-8")
	except AttributeError:
		pass
	default_locale = locale.getdefaultlocale()
	locale.setlocale(locale.LC_ALL, '')
	os.environ['LC_ALL'] = os.environ.get('LC_ALL') or default_locale[0]
	gettext.install(package_name, localedir=locales_dir, unicode=True,
			names=("ngettext",))
	gettext.bindtextdomain(package_name, locales_dir)
	gettext.bindtextdomain('wxstd', locales_dir)
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

from alldb.gui.frame_main import FrameMain
from alldb.gui.splash import AllDbSplash
from alldb.model.db import Db
from alldb.libs import iconprovider


def run():
	config = appconfig.AppConfig()
	config.load()
	config.debug = _OPTIONS.debug

	def try_path(path):
		file_path = os.path.join(path, 'alldb.db')
		if os.path.isfile(file_path):
			return file_path
		return None

	db_filename = try_path(config.main_dir)
	if not db_filename:
		db_filename = try_path(os.path.join(config.main_dir, 'db'))
	if not db_filename:
		db_dir = os.path.join(config.main_dir, 'db')
		if os.path.isdir(db_dir):
			db_filename = os.path.join(db_dir, 'alldb.db')
	if not db_filename:
		db_filename = os.path.join(config.user_share_dir, 'alldb.db')

	app = wx.PySimpleApp(0)
	wx.InitAllImageHandlers()

	splash = AllDbSplash()
	splash.Show()

	if sys.platform == 'win32':
		wx.Locale.AddCatalogLookupPathPrefix(config.locales_dir)
		wxloc = wx.Locale(wx.LANGUAGE_DEFAULT)
		wxloc.AddCatalog('wxstd')

	iconprovider.init_icon_cache(None, config.data_dir)

	config['_DB'] = database = Db(db_filename)
	database.open()

	main_frame = FrameMain(database)
	app.SetTopWindow(main_frame.wnd)
	main_frame.wnd.Show()
	app.MainLoop()

	database.close()
	config.save()


# vim: encoding=utf8: ff=unix:
