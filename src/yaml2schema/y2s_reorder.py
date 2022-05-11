from typing import Optional, Dict, List, Tuple

import strictyaml as sy
from collections import OrderedDict

from y2s_constants import OPENAPI_FORMATS
from y2s_schema import openapi_schema


def key_of_value(dict_: Dict, value) -> str:
    """Returns the first key of the corresponding value in the dict.
    """
    return next((k for k, v in dict_.items() if v == value), None)


def find_type_of_string(sy_dict: sy.YAML) -> str:
    """Finds the type of the field aka column from the openapi yaml format.
    In openyaml, types like datetime are `format` of `string`.

    Parameters
    ----------
    sy_dict
        The dict containing the keys `type` and `format`

    Returns
    -------
        The string type, from the format key.
    """
    format_ = sy_dict.get('format', None)
    if format_ is not None:
        type_of = key_of_value(OPENAPI_FORMATS, format_.text)
        if type_of == 'media':
            type_of = 'blob'
    else:
        type_of = sy_dict['type'].text
    return type_of


def yaml_recursive_add_to_table(
        tables_in_order: List[str],
        table_name: str,
        do_later: List[Dict]):
    """Recursive function to move do_later tables to the tables_in_order list. Of course it only does this
    if the do_later table has all its references previously inserted into tables_in_order.

    Parameters
    ----------
    tables_in_order
        list of table names that are already ordered
    table_name
        the current table name
    do_later
        A list of dicts containing information about tables that cannot be added to
        new yaml because they have references that are not in new yaml

    Returns
    -------
    None
    """
    tables_in_order.append(table_name)
    for ix, doing_now in enumerate(do_later):
        if all([ref_name in tables_in_order for ref_name in doing_now['references']]):
            # need to nullify this table, so it is not repeatedly added to file_lines
            do_later[ix]['references'] = ['This is a dummy table name.']
            yaml_recursive_add_to_table(
                tables_in_order,
                doing_now['table_name'],
                do_later)
    return


def extract_type_of_field(db_field: sy.YAML) -> Tuple[str, str]:
    """Extracts type of field aka column in db. If type is a reference, output that too.

    Parameters
    ----------
    db_field
        Attributes snippet of the yaml file for the field.

    Returns
    -------
    type_of
        type in form of "int", "datetime" etc
    reference:
        table name if the type is a reference to another table
    """
    type_of = ''
    reference: Optional[str] = None  # one of the outputs
    # Let's find out what type of field it is
    what_is_it = db_field.get('type', None)
    if what_is_it is None:
        # must be a reference to another table
        if '$ref' in db_field:
            reference = db_field["$ref"].text.split('/')[-1]
            type_of = f"reference {reference}"
    elif what_is_it.text == 'array':
        # list of references to other tables
        if '$ref' in db_field['items']:
            reference = db_field['items']['$ref'].text.split('/')[-1]
            type_of = f"list:reference {reference}"
        elif 'type' in db_field['items']:
            if db_field['items']['type'] == 'integer':
                type_of = "list:integer"
            elif db_field['items']['type'] == 'string':
                type_of = "list:string"
            else:
                type_of = "INVALID"
        else:
            type_of = find_type_of_string(db_field['items'])
    elif what_is_it.text == 'object':
        type_of = "json"
    elif what_is_it.text == 'number':
        type_of = 'double'
        if db_field.get('format',None) is not None:
            if db_field['format'].text != 'float':
                raise TypeError("'number' type with incorrect format field. Fix anvil_refined.yaml and rerun. Thanks!")
    else:
        type_of = find_type_of_string(db_field)
    return type_of, reference


def reorder_tables(openapi_yaml: sy.YAML) -> List[sy.Str]:
    """Orders the tables so no table references another table that might be defined after.

    Parameters
    ----------
    openapi_yaml
        Contains the openapi format describing the database schema
    Returns
    -------
    tables_in_order
        A list of sy.Str of the table names in order
    """
    openapi = openapi_yaml['components']
    # list of table names already processed
    # Needed to re-order so that tables are not referenced before defined
    # a list of table names in correct order
    tables_in_order = []
    # a list of dicts for the tables that need to added after their references are in tables_in_order
    do_later = []
    for table in openapi['schemas']:
        # add fields
        table_yaml = openapi['schemas'][table]['properties']
        # for ordering
        table_references = []
        try:
            t=iter(table_yaml)
        except TypeError:
            raise TypeError(f"There is no columns in the datatable `{table.text}`")
        for field_name in table_yaml:
            # dict of this table description
            db_field = table_yaml[field_name]
            # Let's find out what type of field it is
            type_of, reference = extract_type_of_field(db_field)
            # if self referencing, ignore when re-ordering
            if reference is not None and reference != table.text:
                table_references.append(reference)
        # check if all the references are already in the list, if so, we can add this one too.
        if len(table_references) == 0 \
                or all([_t in tables_in_order for _t in table_references]):
            yaml_recursive_add_to_table(tables_in_order, table, do_later)
        else:
            do_later.append({'references': table_references,
                             'table_name': table})
    return tables_in_order


def reorder_openapi_yaml(openapi_yaml: sy.YAML, tables_in_order: List[sy.Str]) -> sy.YAML:
    """Inputs an openapi description of database schema and outputs the same but reordered
    so no tables references a table that is defined later in the yaml description.

    Parameters
    ----------
    openapi_yaml
        unordered openapi yaml where tables could be referencing other tables that appear
        later in the yaml definition
    tables_in_order
        list of the tables in proper order

    Returns
    -------
        openapi yaml so that the tables are all in proper order.

    """
    open_yaml_data = openapi_yaml.data
    new_yaml = openapi_yaml.data

    new_yaml['components']['schemas'] = OrderedDict()
    for _t in tables_in_order:
        tablename = _t.text
        new_yaml['components']['schemas'][tablename] = open_yaml_data['components']['schemas'][tablename]
    return sy.as_document(new_yaml, openapi_schema())
