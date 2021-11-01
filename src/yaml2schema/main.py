"""Contains functions that read yaml (anvil.yaml or openapi.yaml) and generates model files.
Main does:
    - Reads in anvil.yaml and generates same in openapi.yaml format
    - Reads in yaml and generate a file of pydantic models.
    - Reads in yaml and generate a pydal definition of the database schema."""

import datamodel_code_generator as dcg

from y2s_reorder import reorder_openapi_yaml, reorder_tables
from y2s_to_openapi import convert_anvil_to_openapi_yaml
from y2s_to_pydal import openapi_to_pydal
from y2s_constants import OPENAPI_TYPES, OPENAPI_FORMATS, Openapi_preamble
from y2s_file_io import build_path, readfile
from y2s_schema import openapi_schema, openapi_preamble_schema, anvil_yaml_schema
import strictyaml as sy


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
    preamble_yaml = sy.load(yaml_string=Openapi_preamble, schema=openapi_preamble_schema())
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
    except Exception:
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
