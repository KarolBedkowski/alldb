
import db
import objects


storage = db.Db('test')

cls = objects.ObjectClass(name='cls1')
cls.fields = [('f1', 'str', '', None), ('f2', 'int', '', None)]
storage.put(cls)

storage.sync()

o = cls.create_object(title='test')
storage.put(o)
storage.sync()

print storage._print_all()

print storage[10001]

print storage.classes
