"""Contains functions that read yaml (anvil.yaml or openapi.yaml) and generates model files.
Main does:
    - Reads in anvil.yaml and generates same in openapi.yaml format
    - Reads in yaml and generate a file of pydantic models.
    - Reads in yaml and generate a pydal definition of the database schema."""
from typing import Optional

import strictyaml as sy
import datamodel_code_generator as dcg
import pathlib
from collections import OrderedDict

OPENAPI_TYPES = {'string': 'string',
                 'datetime': 'string',
                 'date': 'string',
                 'number': 'integer',
                 'bool': 'boolean',
                 'link_single': 'object',
                 'simpleObject': 'array',  # 'object',
                 'link_multiple': 'array',
                 }
OPENAPI_FORMATS = {'date': 'date',
                   'datetime': 'date-time'}


def build_path(filename, directory='source') -> pathlib.Path:
    root = pathlib.Path.cwd() / directory / filename
    return root


def readfile(filename: str, directory: str = 'source') -> tuple[str, list[str]]:
    """Reads a file and outputs the text and an array of newline characters
    used at the end of each line.

    Parameters
    ----------
    filename : str
    directory : str, optional
        Directory of the file. The default is current directory.

    Returns
    -------
    text :
        File as a str
    n : TYPE
        List of strings that contain the types of new_line characters used in the file.
    """
    fn = build_path(filename, directory)
    n = []
    with fn.open("r") as f:
        lines = f.readlines()
        text = ''.join(lines)  # list(f))
        n.extend(f.newlines)
    return text, n


def openapi_schema() -> sy.Map:
    """Schema of openapi in the strictyaml format."""
    string_schema = sy.Map({
        sy.Optional("type"): sy.Enum(OPENAPI_TYPES.values()),
        sy.Optional("format"): sy.Enum(OPENAPI_FORMATS.values()),
        sy.Optional("$ref"): sy.Str()
    })

    type_schema = sy.Map({
        sy.Optional("type"): sy.Enum(OPENAPI_TYPES.values()),
        sy.Optional("format"): sy.Enum(OPENAPI_FORMATS.values()),
        sy.Optional("items"): string_schema,
        sy.Optional("$ref"): sy.Str(),
        sy.Optional('nullable'): sy.Bool(),
        sy.Optional('description'): sy.Str()
    })
    schemas = sy.Map({
        'schemas': sy.MapPattern(
            sy.Str(), sy.Map({
                sy.Optional('required'): sy.Seq(sy.Str()),  # FUTURE : not implemented
                'properties': sy.MapPattern(
                    sy.Str(), type_schema
                )
            })
        )
    })

    components = sy.Map({'components': schemas})
    return components


def openapi_preamble_schema():
    return sy.Map({
        sy.Optional('openapi'): sy.Str(),
        sy.Optional('info'): sy.Map({
            sy.Optional('title'): sy.Str(),
            sy.Optional('description'): sy.Str(),
            sy.Optional('termsOfService'): sy.Str(),
            sy.Optional('version'): sy.Str()
        }),
        sy.Optional('paths'):sy.Map({
            sy.Optional('/'): sy.Any()
        })
    })


def openapi_preamble():
    return """
openapi: 3.0.3
info:
    title: Example openapi file
    description: File can be used as an input to 'yaml2schema'.
    termsOfService: https://unlicense.org
    version: 0.0.1
paths:
    /:
"""


def anvil_yaml_schema() -> sy.Map:
    """
    Reads a block of string (`anvil.yaml`) and parses it
    into a strictyaml object. All done by strictyaml package.

    Returns
    -------
        An instance of the strictyaml class usually as an OrderedDict
    """
    # schema used by strictyaml to parse the text
    schema = sy.Map({
        'db_schema': sy.MapPattern(
            sy.Str(),
            sy.Map({
                'title': sy.Str(),
                'client': sy.Str(),
                'server': sy.Str(),
                'columns': sy.Seq(sy.Map({
                    'name': sy.Str(),
                    'admin_ui': sy.Any(),
                    'type': sy.Str(),
                    sy.Optional('target'): sy.Str()
                }))
            })
        ),
        'renamed': sy.Bool()
    })
    # anvil.yaml uses 'flow style' in certain places.
    return schema


def convert_anvil_to_openapi_yaml(anvil_yaml: sy.YAML) -> sy.YAML:
    """
    Converts `strictyaml` that was parsed from anvil.yaml to openapi format.

    Parameters
    ----------
    anvil_yaml
        Parsed anvil.yaml

    Returns
    -------
    sy.YAML
        open api format of the database schema
    """
    # change first anvil keyword to openapi keyword
    openapi_dict = {'schemas': {}}  # contains final version of the openapi schema
    an_yaml = anvil_yaml['db_schema']  # the input to be converted
    for key_ in an_yaml:
        o_key = key_.text  # an_yaml[key_]['title']  # db table name
        # the basic structure of the openapi table
        openapi_dict['schemas'].update({str(o_key): OrderedDict(
            {  # 'required': [],
                'properties': {}
            })})

        # add an id column
        # key_col = "id"  # column name
        # type_col = {'nullable': True}  # type of column
        # property_dict = openapi_dict['schemas'][o_key]['properties']
        # property_dict.update({key_col:  type_col})

        # for the rest of the columns listed in the anvil.yaml file
        for col in an_yaml[key_]['columns']:  # for each column in the anvil table
            key_col = str(col['name'])  # column name
            # openapi_dict['schemas'][o_key]['required'].append(key_col)  # openapi listing columns
            type_col = str(col['type'])  # what is the type of the column
            format_col = None
            property_dict = openapi_dict['schemas'][o_key]['properties']
            if type_col in OPENAPI_FORMATS:  # translate tha anvil type to openapi type
                format_col = OPENAPI_FORMATS[type_col]
            if type_col == 'link_single':  # reference to another table row
                if col['target'] in an_yaml:
                    table_name = col['target'].text  # str(an_yaml[col['target']]['title'])
                    prop_ref = {'$ref': "#/components/schemas/" + table_name}
                    property_dict.update({key_col: prop_ref})
            elif type_col == 'link_multiple':  # reference to multiple table rows
                if col['target'] in an_yaml:
                    property_dict.update({key_col: {'type': 'array'}})
                    table_name = col['target'].text  # str(an_yaml[col['target']]['title'])
                    prop_ref = {'$ref': "#/components/schemas/" + table_name}
                    property_dict[key_col].update({'items': prop_ref})
            elif type_col == 'simpleObject':
                # is it a link of integer?
                list_of = key_col.split('_')[-1]
                if list_of[:4] == "list":
                    if list_of == 'listint':
                        item_property = {'type': 'integer'}
                    elif list_of == 'liststr':
                        item_property = {'type': 'string'}
                    else:
                        item_property = {'type': 'INVALID'}
                    property_dict.update({key_col: {'type': 'array'}})
                    property_dict[key_col].update({'items': item_property})
            else:
                type_col = OPENAPI_TYPES[type_col]

                property_dict.update({key_col: {'type': type_col}})
                if format_col:
                    property_dict[key_col].update({'format': format_col})

            # add None types to the columns
            # property_dict[key_col].update({'nullable': 'true'})
        # add info

    return sy.as_document({'components': openapi_dict}, openapi_schema(), 'Openapi')


def yaml_recursive_add_to_table(
        tables_in_order: list[str],
        table_name: str,
        do_later: list[dict]):
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


def key_of_value(dict_: dict, value) -> str:
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
    else:
        type_of = sy_dict['type'].text
    return type_of


def extract_type_of_field(db_field: sy.YAML) -> tuple[str, str]:
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
    else:
        type_of = find_type_of_string(db_field)
    return type_of, reference


def reorder_tables(openapi_yaml: sy.YAML) -> list[sy.Str]:
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


def reorder_openapi_yaml(openapi_yaml: sy.YAML, tables_in_order: list[sy.Str]) -> sy.YAML:
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


def main():
    input_yaml = "input/anvil.yaml"
    try:
        anvil_yaml, newline_list = readfile(input_yaml, "")
        db_str = anvil_yaml[anvil_yaml.find('db_schema'):]
        parsed_yaml = sy.dirty_load(yaml_string=db_str, schema=anvil_yaml_schema(), allow_flow_style=True)
        # convert to OPENAPI strict YAML
        open_api_yaml = convert_anvil_to_openapi_yaml(parsed_yaml)
    except FileNotFoundError:
        input_yaml = "input/openapi.yaml"
        open_yaml, newline_list = readfile(input_yaml, "")
        db_str = open_yaml[open_yaml.find('components'):]
        open_api_yaml = sy.dirty_load(yaml_string=db_str, schema=openapi_schema(), allow_flow_style=False)
        # open_api_yaml = sy.dirty_load(yaml_string=db_str, schema=openapi_preamble_schema(), allow_flow_style=False)

    # reorder so that no table is referenced before it is defined
    ordered_openapi_yaml = reorder_openapi_yaml(open_api_yaml,
                                                reorder_tables(open_api_yaml))
    # write the openapi yaml to a file
    preamble_yaml = sy.load(yaml_string=openapi_preamble(), schema=openapi_preamble_schema())
    with open("output/anvil_openapi.yaml", "w") as f_out:
        f_out.write(preamble_yaml.as_yaml())
        f_out.write(ordered_openapi_yaml.as_yaml())

    dcg.generate(
        open_api_yaml.as_yaml(),
        input_file_type=dcg.InputFileType.OpenAPI,
        input_filename="input/anvil.yaml",
        output=build_path("output/db_models.py", "."))
    # base_class="SQLModel",     future work
    pydal_def = openapi_to_pydal(ordered_openapi_yaml)
    with open("output/pydal_def.py", "w") as f_out:
        f_out.write('\n'.join(pydal_def))

    # yaml_file = sy.as_document(openapi_preamble(), openapi_preamble_schema())
    # yaml_file['components'] = compyaml
    # return yaml_file


if __name__ == '__main__':
    try:
        main()
    except:
        comment = """
Input:  input/anvil.yaml
        OR
        input/openapi.yaml
Output: output/anvil_openapi.yaml  # conversion to openapi standard yaml
        output/db_models.py  # pydantic type models
        output/pydal_def.py  # database definition for pyDAL

Can convert the following:\n"""
        doc_type = "anvil.works : openapi\n"
        for key in OPENAPI_TYPES:
            if key not in {"datetime", "date"}:
                doc_type += f"{key} : {OPENAPI_TYPES[key]}\n"
        for key in OPENAPI_FORMATS:
            doc_type += f"{key} : {OPENAPI_FORMATS[key]}\n"
        comment_1 = """
pyDAL and openapi have list:integer and list:string as a column type in databases.
anvil.works uses 'simpleObject' for these types as well as json. In order for 'list:integer'
and 'list:string' to be implemented, you need to name the column `mycolumn_listint`. This
'_listint' part of the name will indicate to this program that it should use a type
of 'list:integer'. Similarly, '_liststr' at the end of the column name with a type
of simplObject, will produce openapi and pyDAL type of 'list:string'. 

TODO:
simpleObject to json"""
        print(comment + doc_type + comment_1)
        raise Exception("Need standard input files.")
