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
