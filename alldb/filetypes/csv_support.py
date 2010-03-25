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


import csv
import codecs

from alldb.model import objects


def export2csv(filename, cls, items):
	''' exportowanie danych
		@filename ścieżka do pliku
		@cls klasa do eksportu
		@items lista elementów do eksportu
	'''
	fields = [f[0] for f in cls.fields]
	with open(filename, 'wt') as fcsv:
		writer = csv.DictWriter(fcsv, fields, extrasaction='ignore')
		writer.writerow(dict((f, f) for f in fields))
		for row in items:
			row_data = dict((fld, objects.get_field_value_human(val))
					for fld, val in row.data.iteritems())
			writer.writerow(row_data)


def import_csv(filename, cls):
	with codecs.open(filename, 'rt', 'utf-8') as fcsv:
		for row in csv.DictReader(fcsv):
			for field in cls.fields:
				if field[1] == 'bool':
					row[field[0]] = bool(row[field[0]])
				else:
					row[field[0]] = unicode(row[field[0]])
			item = cls.create_object()
			item.data.update(row)
			yield item


# vim: encoding=utf8: ff=unix:
