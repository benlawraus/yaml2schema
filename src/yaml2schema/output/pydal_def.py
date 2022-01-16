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

    if 'owner' not in db.tables:
        db.define_table('owner'
            , Field('name', type='string', default=None)
            , Field('settings', type='json', default=None)
            , Field('permission', type='integer', default=None)
        )
    if 'email' not in db.tables:
        db.define_table('email'
            , Field('address', type='string', default=None)
            , Field('place', type='integer', default=None)
            , Field('other_place', type='string', default=None)
            , Field('owner_ref', type='reference owner', default=None, ondelete='NO ACTION')
        )
    if 'location' not in db.tables:
        db.define_table('location'
            , Field('address', type='string', default=None)
            , Field('place', type='integer', default=None)
            , Field('owner_ref', type='reference owner', default=None, ondelete='NO ACTION')
            , Field('other_place', type='string', default=None)
        )
    if 'users' not in db.tables:
        db.define_table('users'
            , Field('email', type='string', default=None)
            , Field('enabled', type='boolean', default=None)
            , Field('signed_up', type='datetime', default=None)
            , Field('password_hash', type='string', default=None)
            , Field('confirmed_email', type='boolean', default=None)
            , Field('email_confirmation_key', type='string', default=None)
            , Field('last_login', type='datetime', default=None)
            , Field('remembered_logins', type='json', default=None)
            , Field('name', type='string', default=None)
            , Field('owner_ref', type='reference owner', default=None, ondelete='NO ACTION')
            , Field('uuid', type='integer', default=None)
            , Field('owner_relation', type='integer', default=None)
        )
    if 'group' not in db.tables:
        db.define_table('group'
            , Field('name', type='string', default=None)
            , Field('description', type='string', default=None)
            , Field('created_by', type='reference users', default=None, ondelete='NO ACTION')
        )
    if 'note' not in db.tables:
        db.define_table('note'
            , Field('text', type='string', default=None)
            , Field('created_on', type='datetime', default=None)
            , Field('created_by', type='reference users', default=None, ondelete='NO ACTION')
            , Field('modified_on', type='date', default=None)
            , Field('modified_by', type='reference users', default=None, ondelete='NO ACTION')
        )
    if 'phone' not in db.tables:
        db.define_table('phone'
            , Field('address', type='string', default=None)
            , Field('text_able', type='boolean', default=None)
            , Field('place', type='integer', default=None)
            , Field('other_place', type='string', default=None)
            , Field('owner_ref', type='reference owner', default=None, ondelete='NO ACTION')
        )
    if 'company' not in db.tables:
        db.define_table('company'
            , Field('name', type='string', default=None)
            , Field('address', type='string', default=None)
            , Field('phone', type='string', default=None)
            , Field('phone_ref', type='reference phone', default=None, ondelete='NO ACTION')
            , Field('url', type='string', default=None)
            , Field('created_by', type='reference users', default=None, ondelete='NO ACTION')
        )
    if 'contact' not in db.tables:
        db.define_table('contact'
            , Field('name', type='string', default=None)
            , Field('created_by', type='reference users', default=None, ondelete='NO ACTION')
            , Field('owner_ref', type='reference owner', default=None, ondelete='NO ACTION')
            , Field('email_list', type='list:reference email', default=None, ondelete='NO ACTION')
            , Field('how_related', type='integer', default=None)
            , Field('location_list', type='list:reference location', default=None, ondelete='NO ACTION')
            , Field('how_related_label', type='string', default=None)
            , Field('phone_list', type='list:reference phone', default=None, ondelete='NO ACTION')
            , Field('modified_on', type='datetime', default=None)
            , Field('last_used', type='datetime', default=None)
            , Field('family', type='list:integer', default=None)
            , Field('age', type='double', default=None)
            , Field('uid', type='bigint', default=None)
        )
    if 'group_member' not in db.tables:
        db.define_table('group_member'
            , Field('group_ref', type='reference group', default=None, ondelete='NO ACTION')
            , Field('created_by', type='reference users', default=None, ondelete='NO ACTION')
            , Field('contact_ref', type='reference contact', default=None, ondelete='NO ACTION')
            , Field('user_ref', type='reference users', default=None, ondelete='NO ACTION')
            , Field('parent', type='boolean', default=None)
            , Field('child', type='boolean', default=None)
            , Field('grandparent', type='boolean', default=None)
            , Field('grandchild', type='boolean', default=None)
            , Field('other', type='boolean', default=None)
        )
    if 'shared_contact' not in db.tables:
        db.define_table('shared_contact'
            , Field('created_by', type='reference users', default=None, ondelete='NO ACTION')
            , Field('shared_with', type='reference users', default=None, ondelete='NO ACTION')
            , Field('contact_ref', type='reference contact', default=None, ondelete='NO ACTION')
            , Field('permission', type='integer', default=None)
            , Field('owner_ref', type='reference owner', default=None, ondelete='NO ACTION')
            , Field('last_used', type='datetime', default=None)
        )
    if 'project' not in db.tables:
        db.define_table('project'
            , Field('name', type='string', default=None)
            , Field('description', type='string', default=None)
            , Field('family_ref', type='reference group', default=None, ondelete='NO ACTION')
            , Field('created_by', type='reference users', default=None, ondelete='NO ACTION')
            , Field('users_ref', type='list:reference users', default=None, ondelete='NO ACTION')
            , Field('contacts_ref', type='list:reference contact', default=None, ondelete='NO ACTION')
            , Field('companies_ref', type='list:reference company', default=None, ondelete='NO ACTION')
        )
    if 'connection' not in db.tables:
        db.define_table('connection'
            , Field('contact_ref', type='reference contact', default=None, ondelete='NO ACTION')
            , Field('created_by', type='reference users', default=None, ondelete='NO ACTION')
            , Field('relation', type='string', default=None)
            , Field('created_on', type='datetime', default=None)
            , Field('note', type='string', default=None)
        )
    if 'meeting' not in db.tables:
        db.define_table('meeting'
            , Field('summary', type='string', default=None)
            , Field('note', type='string', default=None)
            , Field('when', type='datetime', default=None)
            , Field('project_ref', type='reference project', default=None, ondelete='NO ACTION')
            , Field('created_by', type='reference users', default=None, ondelete='NO ACTION')
            , Field('location', type='string', default=None)
        )
    if 'participant' not in db.tables:
        db.define_table('participant'
            , Field('contact_ref', type='reference contact', default=None, ondelete='NO ACTION')
            , Field('meeting_ref', type='reference meeting', default=None, ondelete='NO ACTION')
            , Field('note_ref', type='reference note', default=None, ondelete='NO ACTION')
            , Field('communicated', type='integer', default=None)
            , Field('created_by', type='reference users', default=None, ondelete='NO ACTION')
            , Field('other_label', type='string', default=None)
        )
    if 'shared_meeting' not in db.tables:
        db.define_table('shared_meeting'
            , Field('meeting_ref', type='reference meeting', default=None, ondelete='NO ACTION')
            , Field('shared_with', type='reference users', default=None, ondelete='NO ACTION')
            , Field('created_by', type='reference users', default=None, ondelete='NO ACTION')
            , Field('owner_ref', type='reference owner', default=None, ondelete='NO ACTION')
            , Field('permission', type='integer', default=None)
            , Field('last_used', type='datetime', default=None)
        )
    return

if __name__ == '__main__':
    define_tables_of_db()
