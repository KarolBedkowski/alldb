# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009'
__revision__ = '2009-11-12'


import os
import gettext
import locale
import optparse
import logging

from alldb.gui.frame_main import FrameMain
from alldb.libs import appconfig
from alldb.libs.logging_setup import logging_setup
from alldb.model.db import Db
from alldb.libs.iconprovider import IconProvider

import sys
reload(sys)
try:
	sys.setappdefaultencoding("utf-8")
except Exception, _:
	sys.setdefaultencoding("utf-8")


_LOG = logging.getLogger(__name__)


def show_version(ption, opt_str, value, parser, *args, **kwargs):
	from alldb import version
	print version.INFO
	exit(0)


p = optparse.OptionParser()
p.add_option('--debug', '-d', action="store_true", default=False,
		help='enable debug messages')
p.add_option('--version', action="callback", callback=show_version,
		help='show information about application version')
options, arguments = p.parse_args()

# logowanie
logging_setup('alldb.log', options.debug)


def _setup_locale():
	''' setup locales and gettext '''
	app_config = appconfig.AppConfig('alldb.cfg', 'alldb')
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
	config = appconfig.AppConfig()
	config.load()
	config.debug = options.debug
	db_filename = os.path.join(config.user_share_dir, 'alldb.db')

	app = wx.PySimpleApp(0)

	IconProvider(None, config.data_dir)

	config['_DB'] = db = Db(db_filename)
	db.open()

	wx.InitAllImageHandlers()
	main_frame = FrameMain(db)
	app.SetTopWindow(main_frame.wnd)
	main_frame.wnd.Show()
	app.MainLoop()

	db.close()
	config.save()


# vim: encoding=utf8: ff=unix:
