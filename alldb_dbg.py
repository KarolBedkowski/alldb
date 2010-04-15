#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
"""
from __future__ import with_statement

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski 2006-2010'
__revision__ = '$Id$'
__all__ = []


import sys
sys.argv.append('-d')



def _profile():
	''' profile app '''
	import cProfile
	print 'Profiling....'
	cProfile.run('from alldb.main import run; run()', 'profile.tmp')
	import pstats
	import time
	with open('profile_result_%d.txt' % int(time.time()), 'w') as out:
		stat = pstats.Stats('profile.tmp', stream=out)
		#s.strip_dirs()
		stat.sort_stats('cumulative').print_stats('alldb', 50)
		out.write('\n\n----------------------------\n\n')
		stat.sort_stats('time').print_stats('alldb', 50)


def _memprofile():
	''' mem profile app '''
	from alldb.main import run
	run()
	import gc
	gc.collect()
	while gc.collect() > 0:
		print 'collect'

	import objgraph
	objgraph.show_most_common_types(20)

	import pdb
	pdb.set_trace()


if '--profile' in sys.argv:
	sys.argv.remove('--profile')
	_profile()
elif '--memprofile' in sys.argv:
	sys.argv.remove('--memprofile')
	_memprofile()
elif '--version' in sys.argv:
	from photocat import version
	print version.INFO
else:
	from alldb.main import run
	run()

# vim: encoding=utf8: ff=unix:
