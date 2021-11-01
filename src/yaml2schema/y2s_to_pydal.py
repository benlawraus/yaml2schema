
import strictyaml as sy

from y2s_reorder import extract_type_of_field


def openapi_to_pydal(ordered_openapi_yaml: sy.YAML) -> list[str]:
    """Converts open api yaml describing the database into a pydal definition string such as:
        db.define_table("my_table",Field("my_column","")

    Parameters
    ----------
    ordered_openapi_yaml
        Database schema in openapi format

    Returns
    -------
    list of lines
        pydal definition string of the database schema
    """
    tab1 = "    "

    openapi_dict = ordered_openapi_yaml['components']
    # _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
    # a list of strings for each line in the file
    file_lines = [
        """import os
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
"""
    ]

    for table in openapi_dict['schemas']:
        # _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
        # create the table in pyDal
        table_def_lines = [tab1 + f"if '{table}' not in db.tables:",
                           tab1 * 2 + f"db.define_table('{table}'"]
        # add fields
        table_dict = openapi_dict['schemas'][table]['properties']
        for field_name in table_dict:
            # dict of this table description
            db_field = table_dict[field_name]
            # add field to the table string? Let's find out what type
            type_of, reference = extract_type_of_field(db_field)
            # _#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
            # line of the Column aka Field definition
            table_def_lines.append(tab1 * 3 + f", Field('{field_name}', type='{type_of}', default=None)")
        # last parenthesis of table definition
        table_def_lines.append(tab1 * 2 + ')')
        file_lines.extend(table_def_lines)
    file_lines.append(tab1 + "return")
    return file_lines
