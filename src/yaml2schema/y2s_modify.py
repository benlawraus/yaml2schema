from typing import List

import strictyaml as sy
from collections import OrderedDict


def update_field_type(master: sy.YAML, change: sy.YAML):
    # Get all table names
    for table in change['components']['schemas']:
        change_prop = change['components']['schemas'][table]['properties']
        master_prop = master['components']['schemas'][table]['properties']
        for field_name in change_prop:
            master_prop[field_name] = change_prop[field_name]
    return

def snip_out(file_str:str, start_key:str)->str:
    """From an anvil.yaml file, snips out only the string you want: the database description."""
    good_string:List[str]=[]
    save_this_one = False
    for line in file_str.split('\n'):
        if line.startswith(start_key):
            good_string.append(line)
            save_this_one=True
        elif save_this_one is False:
            continue
        elif line[0]==' ' or line[0]=='\t':
            good_string.append(line)
        else:
            save_this_one=False
    return '\n'.join(good_string)

