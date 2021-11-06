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
    # in following definitions, delete 'ondelete=..' parameter and CASCADE will be ON.

    if 'users' not in db.tables:
        db.define_table('users'
            , Field('email', type='string', default=None, ondelete='NO ACTION')
            , Field('enabled', type='boolean', default=None, ondelete='NO ACTION')
            , Field('signed_up', type='datetime', default=None, ondelete='NO ACTION')
            , Field('password_hash', type='string', default=None, ondelete='NO ACTION')
            , Field('confirmed_email', type='boolean', default=None, ondelete='NO ACTION')
            , Field('email_confirmation_key', type='string', default=None, ondelete='NO ACTION')
        )
    if 'email' not in db.tables:
        db.define_table('email'
            , Field('address', type='string', default=None, ondelete='NO ACTION')
            , Field('created_by', type='reference users', default=None, ondelete='NO ACTION')
            , Field('created_on', type='datetime', default=None, ondelete='NO ACTION')
        )
    if 'phone' not in db.tables:
        db.define_table('phone'
            , Field('number', type='string', default=None, ondelete='NO ACTION')
            , Field('created_by', type='reference users', default=None, ondelete='NO ACTION')
            , Field('created_on', type='datetime', default=None, ondelete='NO ACTION')
        )
    if 'contact' not in db.tables:
        db.define_table('contact'
            , Field('name', type='string', default=None, ondelete='NO ACTION')
            , Field('phone', type='reference phone', default=None, ondelete='NO ACTION')
            , Field('email', type='list:reference email', default=None, ondelete='NO ACTION')
            , Field('age', type='double', default=None, ondelete='NO ACTION')
            , Field('created_by', type='reference users', default=None, ondelete='NO ACTION')
            , Field('created_on', type='datetime', default=None, ondelete='NO ACTION')
            , Field('family', type='list:integer', default=None, ondelete='NO ACTION')
            , Field('uid', type='bigint', default=None, ondelete='NO ACTION')
            , Field('father', type='reference contact', default=None, ondelete='NO ACTION')
        )
    return