
from __future__ import with_statement

import sys

import db
import objects


def run():
	storage = db.Db('test')

	cls = objects.ObjectClass(name='cls1')
	cls.fields = [('f1', 'str', '', None), ('f2', 'int', '', None)]
	cls.save(storage)

	storage.sync()

	for x in xrange(10):
		o = cls.create_object(title=('test_%d' % x))
		o.data.update({'f1': 'alalal', 'f2': 10201})
		o.save()

	storage.sync()

	print storage._print_all()

	print storage.get(10001)

	print storage.classes
	print
	print cls.objects


if '--profile' in sys.argv:
	sys.argv.remove('--profile')
	import cProfile
	print 'Profiling....'
	cProfile.run('run()', 'profile.tmp')
	import pstats
	import time
	with open('profile_result_%d.txt' % int(time.time()), 'w') as out:
		s = pstats.Stats('profile.tmp', stream=out)
#		s.strip_dirs()
		s.sort_stats('cumulative').print_stats('', 50)

		out.write('\n\n----------------------------\n\n')

		s.sort_stats('time').print_stats('', 50)

else:
	run()
