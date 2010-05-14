# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103
"""
Konfiguracja programu
"""

from __future__ import with_statement


__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-05-14"


import sys
import os
import imp
import logging
import ConfigParser

from .. import configuration
from .singleton import Singleton

_LOG = logging.getLogger(__name__)


class AppConfig(Singleton):
	''' konfiguracja aplikacji '''

	def _init(self, filename, app_name):
		_LOG.debug('__init__(%s)' % filename)
		self._user_home = os.path.expanduser('~')
		self.app_name = app_name
		self.main_is_frozen = is_frozen()
		self.main_dir = self._get_main_dir()
		self.config_path = self._get_config_path(app_name)
		self.data_dir = os.path.join(self.main_dir, configuration.DATA_DIR)
		self.templates_dir = os.path.join(self.data_dir, 'templates')
		self._filename = os.path.join(self.config_path, filename)
		self._config = ConfigParser.SafeConfigParser()
		self.clear()

		_LOG.debug('AppConfig.__init__: frozen=%s, main_dir=%s, config=%s' %
				(self.main_is_frozen, self.main_dir, self._filename))

	###########################################################################

	# dostęp do _runtime_params
	def __len__(self):
		return self._runtime_params.__len__()

	def __getitem__(self, key):
		return self._runtime_params.__getitem__(key)

	def __setitem__(self, key, value):
		self._runtime_params.__setitem__(key, value)

	def __delitem__(self, key):
		self._runtime_params.__delitem__(key)

	def __iter__(self):
		self._runtime_params.__iter__()

	def _get_debug(self):
		return self._runtime_params.get('DEBUG', False)

	def _set_debug(self, value):
		self._runtime_params['DEBUG'] = value

	debug = property(_get_debug, _set_debug)

	###########################################################################

	@property
	def locales_dir(self):
		if self.main_is_frozen:
			if self.main_dir == configuration.LINUX_INSTALL_DIR:
				return configuration.LINUX_LOCALES_DIR
		return os.path.join(self.main_dir, configuration.LOCALES_DIR)

	@property
	def user_share_dir(self):
		return os.path.join(self._user_home, '.local', 'share', self.app_name)

	def clear(self):
		self.last_open_files = []
		for section in self._config.sections():
			self._config.remove_section(section)
		self._runtime_params = {}

	def load(self):
		if os.path.exists(self._filename):
			_LOG.debug('load: %s', self._filename)
			try:
				with open(self._filename, 'r') as cfile:
					self._config.readfp(cfile)
			except StandardError:
				_LOG.exception('load error')
			else:
				self._after_load(self._config)
			_LOG.debug('load end')

	def save(self):
		_LOG.debug('save')
		self._before_save(self._config)
		cfile = None
		try:
			with open(self._filename, 'w') as cfile:
				self._config.write(cfile)
		except StandardError:
			_LOG.exception('save error')
		_LOG.debug('save end')

	def add_last_open_file(self, filename):
		if filename in self.last_open_files:
			self.last_open_files.remove(filename)
		self.last_open_files.insert(0, filename)
		self.last_open_files = self.last_open_files[:7]

	def get_data_file(self, filename):
		path = os.path.join(self.data_dir, filename)
		if os.path.exists(path):
			return path
		_LOG.warn('AppConfig.get_data_file(%s) not found', filename)
		return None

	def get(self, section, key, default=None):
		if self._config.has_section(section) \
				and self._config.has_option(section, key):
			try:
				return eval(self._config.get(section, key))
			except:
				_LOG.exception('AppConfig.get(%s, %s, %r)' % (section, key, default))
		return default

	def get_items(self, section):
		if self._config.has_section(section):
			try:
				items = self._config.items(section)
				if items:
					result = tuple((key, eval(val)) for key, val in items)
				return result
			except:
				_LOG.exception('AppConfig.get(%s)' % section)
		return None

	def set(self, section, key, val):
		if not self._config.has_section(section):
			self._config.add_section(section)
		self._config.set(section, key, repr(val))

	def set_items(self, section, key, items):
		config = self._config
		if config.has_section(section):
			config.remove_section(section)
		config.add_section(section)
		for idx, item in enumerate(items):
			config.set(section, '%s%05d' % (key, idx), repr(item))

	def _get_main_dir(self):
		if self.main_is_frozen:
			if os.path.abspath(os.path.dirname(__file__)).startswith(
					configuration.LINUX_INSTALL_DIR):
				return configuration.LINUX_INSTALL_DIR
			return os.path.abspath(os.path.dirname(sys.executable))
		return os.path.abspath(os.path.dirname(sys.argv[0]))

	def _get_config_path(self, app_name):
		config_path = self.main_dir
		if not sys.platform.startswith('win'):
			config_path = os.path.join(self._user_home, '.config', app_name)
			if not os.path.exists(config_path):
				try:
					os.makedirs(config_path)
				except:
					_LOG.exception('Error creating config directory: %s' \
							% self.config_path)
					config_path = self.main_dir
		return config_path

	def _after_load(self, config):
		if config.has_section('last_files'):
			self.last_open_files = [val[1] for val in config.items('last_files')]

	def _before_save(self, config):
		if config.has_section('last_files'):
			config.remove_section('last_files')
		config.add_section('last_files')
		last_open_files = self.last_open_files[:7]
		for fidn, fname in enumerate(last_open_files):
			config.set('last_files', 'file%d' % fidn, fname)


def is_frozen():
	if __file__.startswith(configuration.LINUX_INSTALL_DIR):
		return True
	return (hasattr(sys, "frozen")		# new py2exe
			or hasattr(sys, "importers")		# old py2exe
			or imp.is_frozen("__main__"))		# tools/freeze


if __name__ == '__main__':
	acfg = AppConfig('test.cfg')
	acfg.last_open_files = ['1', '2', 'q', 'w']
	print id(acfg), acfg.last_open_files
	acfg.save()

	acfg.clear()
	print id(acfg), acfg.last_open_files

	acfg = AppConfig('test.cfg')
	acfg.load()
	print id(acfg), acfg.last_open_files



# vim: encoding=utf8: ff=unix:
