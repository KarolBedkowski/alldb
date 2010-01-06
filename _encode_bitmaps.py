#!/usr/bin/python

"""
This is a way to save the startup time when running img2py on lots of
files...
"""

import sys, os

from wx.tools import img2py

os.chdir('alldb/icons')
try:
	os.unlink('icons.py')
except:
	pass


command_lines = [ '-u -n _%s_ %s icons.py' % (name[:-4], name) 
		for name in os.listdir('.')
		if name.endswith('.png') or name.endswith('.ico')
]

for lp, line in enumerate(command_lines):
	args = line.split()
	if lp > 0:
		args.insert(0, '-a')
	img2py.main(args)

