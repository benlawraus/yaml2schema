"""Contains functions that read yaml (anvil.yaml or openapi.yaml) and generates model files.
Main does:
    - Reads in anvil.yaml and generates same in openapi.yaml format
    - Reads in (anvil or openapi) yaml and generate a file of pydantic models.
    - Reads in (anvil or openapi) yaml and generate a pydal definition of the database schema."""
from y2s_reorder import reorder_openapi_yaml, reorder_tables
from y2s_to_openapi import convert_anvil_to_openapi_yaml
from y2s_to_pydal import openapi_to_pydal
from y2s_constants import OPENAPI_TYPES, OPENAPI_FORMATS, Openapi_preamble
from y2s_file_io import build_path, readfile
from y2s_schema import openapi_schema, openapi_preamble_schema, anvil_yaml_schema
from y2s_modify import update_field_type, snip_out
import strictyaml as sy

CLASS_MODELS = True
try:
    import datamodel_code_generator as dcg
except ImportError:
    print("Not generating class models.")
    CLASS_MODELS = False


def main():
    input_dir = "tests/yaml/in/"
    output_dir = "tests/yaml/out/"
    input_yaml = input_dir + "anvil.yaml"
    input_refined = input_dir + "anvil_refined.yaml"
    try:
        # if there is anvil.yaml, converts to openapi.yaml
        anvil_yaml, newline_list = readfile(input_yaml, "")
        db_str = snip_out(anvil_yaml, 'db_schema')
        if '{}' in db_str and len(db_str)<20:
            print("!!!!!!!!!!!No database tables in anvil.yaml!!!!!!!!!!!")
            db_str = readfile(input_dir+"user.yaml","")
        parsed_yaml = sy.dirty_load(yaml_string=db_str, schema=anvil_yaml_schema(), allow_flow_style=True)
        # convert to OPENAPI strict YAML
        open_api_yaml = convert_anvil_to_openapi_yaml(parsed_yaml)
        # is there more to add in anvil_refined.yaml?
        try:
            anvil_yaml_refined, newline_list = readfile(input_refined, "")
            db_str = anvil_yaml_refined[anvil_yaml_refined.find('components'):]
            refined_yaml = sy.dirty_load(yaml_string=db_str, schema=openapi_schema(), allow_flow_style=False)
            update_field_type(open_api_yaml, refined_yaml)
        except FileNotFoundError:
            pass
    except FileNotFoundError:
        # if no anvil.yaml, read in the openapi.yaml
        input_yaml = input_dir + "openapi.yaml"
        open_yaml, newline_list = readfile(input_yaml, "")
        db_str = open_yaml[open_yaml.find('components'):]
        open_api_yaml = sy.dirty_load(yaml_string=db_str, schema=openapi_schema(), allow_flow_style=False)

    # reorder so that no table is referenced before it is defined
    ordered_openapi_yaml = reorder_openapi_yaml(open_api_yaml,
                                                reorder_tables(open_api_yaml))
    # write the openapi yaml to a file
    preamble_yaml = sy.load(yaml_string=Openapi_preamble, schema=openapi_preamble_schema())
    with open(output_dir + "anvil_openapi.yaml", "w") as f_out:
        f_out.write(preamble_yaml.as_yaml())
        f_out.write(ordered_openapi_yaml.as_yaml())
    if CLASS_MODELS:
        dcg.generate(
            open_api_yaml.as_yaml(),  # do not need ordered yaml here as dcg will also order it.
            input_file_type=dcg.InputFileType.OpenAPI,
            input_filename=input_dir+"anvil.yaml",
            output=build_path(output_dir+"db_models.py", "."))
    # generate the pyDAL schema definitions
    pydal_def = openapi_to_pydal(ordered_openapi_yaml)
    with open(output_dir + "pydal_def.py", "w") as f_out:
        f_out.write('\n'.join(pydal_def))
    return True


if __name__ == '__main__':
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

    if not main():
        print(comment + doc_type)
        exit(1)
    exit(0)
