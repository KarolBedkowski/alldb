# -*- coding: utf-8 -*-

"""
AllDb
Eksportowanie danych do pliku csv
"""
from __future__ import with_statement

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-05-03"


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


def import_csv(filename, cls, mapping, skip_header=False):
	with codecs.open(filename, 'rt', 'utf-8') as fcsv:
		fields_types = dict(fieldinfo[:2] for fieldinfo in cls.fields)
		for idx, row in enumerate(csv.reader(fcsv)):
			if len(row) == 0:
				continue
			if idx == 0 and skip_header:
				continue
			item_data = {}
			for col, field in mapping.iteritems():
				if fields_types[field] == 'bool':
					item_data[field] = bool(row[col])
				else:
					item_data[field] = unicode(row[col])
			item = cls.create_object()
			item.data.update(item_data)
			yield item


def load_cvs_header(filename):
	with codecs.open(filename, 'rt', 'utf-8') as fcsv:
		for idx, row in enumerate(csv.reader(fcsv)):
			if idx > 9:
				return
			yield map(unicode, row)



# vim: encoding=utf8: ff=unix:
