# -*- coding: utf-8 -*-

"""
AllDb
Eksportowanie danych do pliku pdf
"""
from __future__ import with_statement

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2009-2010"
__version__ = "2010-06-11"


import logging
from cStringIO import StringIO

from alldb.model import objects
from alldb.libs.appconfig import AppConfig

_LOG = logging.getLogger(__name__)


# próba załadowania reportlab
try:
	from reportlab.platypus import (SimpleDocTemplate, Table, Paragraph,
			TableStyle, Spacer, Image)
	from reportlab.rl_config import defaultPageSize
	from reportlab.lib import colors
	from reportlab.lib.units import cm, inch
	from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
	from reportlab.lib.enums import TA_CENTER, TA_LEFT
	from reportlab.pdfbase import pdfmetrics
	from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
	_LOG.warn('reportlab not available')
	PDF_AVAILABLE = False
else:
	_LOG.info('reportlab loaded')
	PDF_AVAILABLE = True


_MARGIN_TOP = 0.5 * cm
_MARGIN_BOTTOM = 1 * cm
_MARGIN_LEFT = _MARGIN_RIGHT = 0.5 * cm


def _my_page(canvas, doc):
	# strona - numer
	canvas.saveState()
	canvas.setFont('FreeSans', 6)
	canvas.drawString(defaultPageSize[0] / 2, _MARGIN_BOTTOM, "%d" % doc.page)
	canvas.restoreState()


def export_pdf_list(filename, cls, items):
	''' exportowanie danych
		@filename ścieżka do pliku
		@cls klasa do eksportu
		@items lista elementów do eksportu'''
	_create_document(filename, cls, items, _create_pdf_list)


def export_pdf_all(filename, cls, items):
	''' exportowanie danych
		@filename ścieżka do pliku
		@cls klasa do eksportu
		@items lista elementów do eksportu'''
	_create_document(filename, cls, items, _create_pdf_all)


def _prepare_styles():
	styles = {}
	stylesheet = getSampleStyleSheet()

	style = ParagraphStyle("Normal", stylesheet['Normal'])
	style.alignment = TA_LEFT
	style.fontSize = 6
	style.fontName = 'FreeSans'
	style.leading = 8
	styles['Normal'] = style

	style = ParagraphStyle("ItemTitle", stylesheet['Heading1'])
	style.alignment = TA_LEFT
	style.fontSize = 8
	style.fontName = 'FreeSansBold'
	style.fontSize = 10
	styles['ItemTitle'] = style

	style = ParagraphStyle("Heading", stylesheet['Heading2'])
	style.alignment = TA_CENTER
	style.fontSize = 6
	style.fontName = 'FreeSansBold'
	styles['Heading'] = style

	style = ParagraphStyle("FieldHead", stylesheet['Heading2'])
	style.alignment = TA_LEFT
	style.fontSize = 6
	style.fontName = 'FreeSansBold'
	style.leading = 8
	styles['FieldHead'] = style

	return styles


def _create_document(filename, cls, items, method):
	try:
		appconfig = AppConfig()
		pdfmetrics.registerFont(TTFont('FreeSans',
				appconfig.get_data_file('fonts/freesans.ttf')))
		pdfmetrics.registerFont(TTFont('FreeSansBold',
				appconfig.get_data_file('fonts/freesansbold.ttf')))

		doc = SimpleDocTemplate(filename, leftMargin=_MARGIN_LEFT,
				rightMargin=_MARGIN_RIGHT, topMargin=_MARGIN_TOP,
				bottomMargin=_MARGIN_BOTTOM, pageCompression=9)

		pages = list(method(cls, items))

		doc.build(pages, onLaterPages=_my_page, onFirstPage=_my_page)
	except RuntimeError:
		_LOG.exception('create_pdf error. file=%s', filename)
		raise


def _create_pdf_list(cls, items):
	styles = _prepare_styles()
	style_header = styles['Heading']
	style_normal = styles['Normal']

	fields = list(cls.fields_in_list)
	data = [[Paragraph(objects.get_field_name_human(field), style_header)
			for field in fields]]
	for item in items:
		row = [Paragraph(objects.get_field_value_human(item.get_value(
				field)), style_normal) for field in fields]
		data.append(row)

	table_style = [('ALIGN', (0, 0), (-1, 0), 'CENTER'),
			('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
			('GRID', (0, 0), (-1, -1), 0.25, colors.black)]
	table = Table(data)
	table.setStyle(TableStyle(table_style))
	yield table


def _create_pdf_all(cls, items):
	styles = _prepare_styles()
	style_header = styles['FieldHead']
	style_normal = styles['Normal']
	style_title = styles['ItemTitle']

	fields = cls.fields
	table_style = TableStyle([('GRID', (0, 0), (-1, -1), 0.25, colors.black)])

	for item in items:
		if cls.title_show:
			yield Paragraph(item.title, style_title)

		rows = []
		for field_name, field_type, dummy, dummy in fields:
			row = [Paragraph(objects.get_field_value_human(field_name),
					style_header)]
			if field_type == 'image':
				blob = item.get_blob(field_name)
				if blob:
					img = Image(StringIO(blob), lazy=2)
					img.drawWidth = img.drawWidth / 150. * inch
					img.drawHeight = img.drawHeight / 150. * inch
					row.append(img)
			else:
				row.append(Paragraph(objects.get_field_value_human(
					item.get_value(field_name)), style_normal))
			rows.append(row)
		yield Table(rows, [5 * cm, None], style=table_style)
		yield Spacer(0.5 * cm, 0.5 * cm)




# vim: encoding=utf8: ff=unix:
