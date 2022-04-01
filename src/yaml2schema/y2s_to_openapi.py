import strictyaml as sy
from collections import OrderedDict

from y2s_constants import OPENAPI_FORMATS, OPENAPI_TYPES
from y2s_schema import openapi_schema


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
            else:
                type_col = OPENAPI_TYPES[type_col]

                property_dict.update({key_col: {'type': type_col}})
                if format_col:
                    property_dict[key_col].update({'format': format_col})

            # add None types to the columns
            # property_dict[key_col].update({'nullable': 'true'})
        # add info
        if len(openapi_dict.keys()) == 0:
            # there are no database tables!!!
            print("No database tables in anvil.yaml!! Exiting.")
            exit(0)
    return sy.as_document({'components': openapi_dict}, openapi_schema(), 'Openapi')
