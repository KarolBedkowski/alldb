# -*- coding: utf-8 -*-

"""
AllDb
Eksportowanie danych do pliku csv
"""
from __future__ import with_statement

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2009'
__version__ = '0.1'
__release__ = '2009-11-12'


from xml.etree.ElementTree import Element, ElementTree

from alldb.model import objects


def export_html(filename, cls, items):
	''' exportowanie danych
		@filename ścieżka do pliku
		@cls klasa do eksportu
		@items lista elementów do eksportu'''
	root = Element('html')
	head = Element('head')
	head.append(Element('meta', {'http-equiv': 'Content-Type',
		'content': "text/html; charset=UTF-8"}))
	root.append(head)
	body = Element('body')
	root.append(body)
	table = Element('table', {'border': '1', "cellspacing": '0',
			"cellpadding": '5'})
	body.append(table)
	row = Element('tr')
	for f in cls.fields:
		td = Element('td')
		td.text = str(f[0])
		row.append(td)
	table.append(row)
	for item in items:
		row = Element('tr')
		for f in cls.fields:
			td = Element('td')
			td.text = str(objects.get_field_value_human(item.get_value(f[0])))
			row.append(td)
		table.append(row)

	etree = ElementTree(root)
	etree.write(filename, 'UTF-8')


# vim: encoding=utf8: ff=unix:
