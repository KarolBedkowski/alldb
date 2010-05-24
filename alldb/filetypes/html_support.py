# -*- coding: utf-8 -*-

"""
AllDb
Eksportowanie danych do pliku csv
"""
from __future__ import with_statement

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-05-24"


from xml.etree.ElementTree import Element, ElementTree, SubElement

from alldb.model import objects


def export_html(filename, cls, items):
	''' exportowanie danych
		@filename ścieżka do pliku
		@cls klasa do eksportu
		@items lista elementów do eksportu'''
	root = Element('html')
	head = SubElement(root, 'head')
	head.append(Element('meta', {'http-equiv': 'Content-Type',
		'content': "text/html; charset=UTF-8"}))
	body = SubElement(root, 'body')
	table = SubElement(body, 'table', border='1', cellspacing='0',
			cellpadding='5')
	row = SubElement(SubElement(table, 'thead'), 'tr')
	for field in cls.fields:
		SubElement(row, 'th').text = str(field[0])
	tbody = SubElement(table, 'tbody')
	for item in items:
		row = SubElement(tbody, 'tr')
		for field in cls.fields:
			SubElement(row, 'td').text = str(objects.get_field_value_human(
					item.get_value(field[0]))) or '-'
	ElementTree(root).write(filename, 'UTF-8')


# vim: encoding=utf8: ff=unix:
