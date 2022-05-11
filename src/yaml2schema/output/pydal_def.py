
import pathlib

from pydal import DAL, Field

db = None
logged_in_user = None
abs_path = pathlib.Path(__file__).parent / 'database'


def define_tables_of_db():
    global db
    global abs_path
    if db is None:
        db = DAL('sqlite://storage.sqlite', folder=abs_path)
    # in following definitions, delete 'ondelete=..' parameter and CASCADE will be ON.

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
