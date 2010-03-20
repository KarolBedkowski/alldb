#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import os.path
import time
import sys

try:
	from setuptools import setup
except:
	from distutils.core import setup

if sys.platform == 'win32':
	try:
		import py2exe
	except:
		pass

from alldb import version, configuration

build = time.asctime()


def is_package(filename):
	return (os.path.isdir(filename) \
			and os.path.isfile(os.path.join(filename, '__init__.py')))


def packages_for(filename, basePackage=""):
	"""Find all packages in filename"""
	packages = {}
	for item in os.listdir(filename):
		dir = os.path.join(filename, item)
		if is_package(dir):
			if basePackage:
				moduleName = basePackage + '.' + item
			else:
				moduleName = item
			packages[moduleName] = dir
			packages.update(packages_for(dir, moduleName))
	return packages


def find_files(directory, base):
	for name, subdirs, files in os.walk(directory):
		if files:
			yield (os.path.join(base, name), \
					[os.path.join(name, fname) for fname in files])


packages = packages_for(".")

def get_data_files():
	if sys.platform == 'win32':
		doc_dir = locales_dir = data_dir = '.'
	else:
		doc_dir = configuration.LINUX_DOC_DIR
		locales_dir = configuration.LINUX_LOCALES_DIR
		data_dir = configuration.LINUX_DATA_DIR

	yield (doc_dir, ['AUTHORS', 'README', "TODO", "COPYING", "LICENCE_EXIFpy.txt",
			"LICENCE_python.txt", "LICENCE_wxPython.txt", 'ChangeLog',
			'LICENCE_ICONS.txt'])

	for x in find_files('data', data_dir):
		yield x

	for x in find_files('locale', locales_dir):
		yield x


target = {
	'script': "alldb.py",
	'name': "alldb",
	'version': version.VERSION,
	'description': "%s - %s (%s, build: %s)" \
			% (version.NAME, version.DESCRIPTION, version.RELEASE, build),
	'company_name': "Karol Będkowski",
	'copyright': version.COPYRIGHT,
	'icon_resources': [(0, "data/art/icon.ico")],
	'other_resources': [("VERSIONTAG", 1, build)] }


setup(
	name='alldb',
	version=version.VERSION,
	author=target['company_name'],
	author_email='karol.bedkowski@gmail.com',
	description=target['description'],
	long_description='-',
	license='GPL v2',
	url='-',
	download_url='-',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Win32 (MS Windows)',
		'Environment :: X11 Applications',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Database :: Desktop',
	],
	packages=packages.keys(),
	package_dir=packages,
	data_files=list(get_data_files()),
	include_package_data=True,
	scripts=['alldb.py'],
	install_requires=['wxPython>=2.6.0', ],
	options={"py2exe": {
		"compressed": 1,
		"optimize": 2,
		"ascii": 0,
		"bundle_files": 2}},
	zipfile=r"modules.dat",
	windows = [target],
)


# vim: encoding=utf8:
