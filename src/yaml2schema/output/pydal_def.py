import os
import inspect

from pydal import DAL, Field

db = None
logged_in_user = None
abs_path = os.path.dirname(inspect.getfile(lambda: 0))


def define_tables_of_db():
    global db
    global abs_path
    if db is None:
        db = DAL('sqlite://storage.sqlite', folder=abs_path+'/database')

    if 'users' not in db.tables:
        db.define_table('users'
            , Field('email', type='string', default=None)
            , Field('enabled', type='boolean', default=None)
            , Field('signed_up', type='datetime', default=None)
            , Field('password_hash', type='string', default=None)
            , Field('confirmed_email', type='boolean', default=None)
            , Field('email_confirmation_key', type='string', default=None)
        )
    if 'email' not in db.tables:
        db.define_table('email'
            , Field('address', type='string', default=None)
            , Field('created_by', type='reference users', default=None)
            , Field('created_on', type='datetime', default=None)
        )
    if 'phone' not in db.tables:
        db.define_table('phone'
            , Field('number', type='string', default=None)
            , Field('created_by', type='reference users', default=None)
            , Field('created_on', type='datetime', default=None)
        )
    if 'contact' not in db.tables:
        db.define_table('contact'
            , Field('name', type='string', default=None)
            , Field('phone', type='reference phone', default=None)
            , Field('email', type='list:reference email', default=None)
            , Field('age', type='double', default=None)
            , Field('created_by', type='reference users', default=None)
            , Field('created_on', type='datetime', default=None)
            , Field('family', type='list:integer', default=None)
            , Field('uid', type='bigint', default=None)
            , Field('father', type='reference contact', default=None)
        )
    return