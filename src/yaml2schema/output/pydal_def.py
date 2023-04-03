
import pathlib

from pydal import DAL, Field

db = None
logged_in_user = None
abs_path = pathlib.Path(__file__).parent / 'database'
if abs_path.exists() is False:
    abs_path.mkdir()

def define_tables_of_db():
    global db
    global abs_path
    if db is None:
        db = DAL('sqlite://storage.sqlite', folder=abs_path)
    # in following definitions, delete 'ondelete=..' parameter and CASCADE will be ON.

    if 'users' not in db.tables:
        db.define_table('users'
            , Field('email', type='string', default=None)
            , Field('enabled', type='boolean', default=None)
            , Field('uid', type='string', default=None)
            , Field('owner_ref', type='string', default=None)
            , Field('signed_up', type='datetime', default=None)
            , Field('password_hash', type='string', default=None)
            , Field('confirmed_email', type='boolean', default=None)
            , Field('email_confirmation_key', type='string', default=None)
            , Field('last_login', type='datetime', default=None)
            , Field('remembered_logins', type='json', default=None)
            , Field('n_password_failures', type='integer', default=None)
        )
    if 'categories' not in db.tables:
        db.define_table('categories'
            , Field('name', type='string', default=None)
        )
    if 'articles' not in db.tables:
        db.define_table('articles'
            , Field('title', type='string', default=None)
            , Field('content', type='string', default=None)
            , Field('image_name', type='upload', uploadfield='image')
            , Field('image', type='blob', default=None)
            , Field('created', type='datetime', default=None)
            , Field('updated', type='datetime', default=None)
            , Field('category', type='reference categories', default=None, ondelete='NO ACTION')
        )
    return

if __name__ == '__main__':
    define_tables_of_db()
