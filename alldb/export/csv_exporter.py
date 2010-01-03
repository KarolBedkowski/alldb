# -*- coding: utf-8 -*-

"""
AllDb
Eksportowanie danych do pliku csv
"""
from __future__ import with_statement

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2009'
__version__		= '0.1'
__release__		= '2009-11-12'


import csv


def export2csv(filename, cls, items):
	''' exportowanie danych
		@filename ścieżka do pliku
		@cls klasa do eksportu
		@items lista elementów do eksportu
	'''
	fields = [ f[0] for f in cls.fields ]
	itemsdata = ( i.data for i in items )
	with open(filename, 'wt') as fcsv:
		writer = csv.DictWriter(fcsv, fields, extrasaction='ignore')
		writer.writerow(dict(( (f,f) for f in fields )))
		writer.writerows(itemsdata)




# vim: encoding=utf8: ff=unix:
