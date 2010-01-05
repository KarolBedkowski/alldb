# -*- coding: utf-8 -*-

"""
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__revision__	= '2009-11-12'


import os
import gettext
import locale
import imp
import tempfile

import logging
_LOG = logging.getLogger(__name__)

import wx

from alldb.gui.FrameMain import FrameMain
from alldb.libs.appconfig import AppConfig
from alldb.model.db import Db

import sys
reload(sys)
try:
	sys.setappdefaultencoding("utf-8")
except Exception, _:
	sys.setdefaultencoding("utf-8")

def _is_frozen():
	return (hasattr(sys, "frozen")		# new py2exe
			or hasattr(sys, "importers")	# old py2exe
			or imp.is_frozen("__main__"))	# tools/freeze

def logging_setup(filename, debug=False):
	log_fullpath = os.path.abspath(filename)
	log_dir = os.path.dirname(log_fullpath)
	log_dir_access = os.access(log_dir, os.W_OK)

	if os.path.isabs(filename):
		if not log_dir_access:
			log_fullpath = os.path.join(tempfile.gettempdir(), filename)
	else:
		if _is_frozen() or not log_dir_access:
			log_fullpath = os.path.join(tempfile.gettempdir(), filename)

	print 'Logging to %s' % log_fullpath

	if debug:
		level_console	= logging.DEBUG
		level_file		= logging.DEBUG
	else:
		level_console	= logging.INFO
		level_file		= logging.ERROR

	logging.basicConfig(level=level_file, format='%(asctime)s %(levelname)-8s %(name)s - %(message)s',
			filename=log_fullpath, filemode='w')
	console = logging.StreamHandler()
	console.setLevel(level_console)

	console.setFormatter(logging.Formatter('%(levelname)-8s %(name)s - %(message)s'))
	logging.getLogger('').addHandler(console)

	logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
	logging.getLogger('sqlalchemy.orm.unitofwork').setLevel(logging.WARN)

	_LOG = logging.getLogger(__name__)
	_LOG.debug('logging_setup() finished')


def run():
	debug = sys.argv.count('-d') > 0
	if debug:
		sys.argv.remove('-d')
	debug =  debug or __debug__

	logging_setup('alldb.log', debug)

	config = AppConfig(__file__, 'alldb')
	config.load()
	config.debug = debug
	db_filename = os.path.join(config.path_share, 'alldb.db')

	gettext.install("alldb", unicode=True)
	try:
		locale.setlocale(locale.LC_ALL, "")
	except locale.Error, e:
		print e
	
	app = wx.PySimpleApp(0)

	wxlocale = wx.Locale(wx.LANGUAGE_DEFAULT)
	wxlocale.AddCatalog('alldb')

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
