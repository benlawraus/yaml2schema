import strictyaml as sy

from y2s_constants import OPENAPI_TYPES, OPENAPI_FORMATS


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
        'schemas': sy.EmptyDict() | sy.MapPattern(
            sy.Str(), sy.Map({
                sy.Optional('required'): sy.EmptyDict() | sy.Seq(sy.Str()),  # FUTURE : not implemented
                sy.Optional('properties'): sy.EmptyDict() | sy.MapPattern(
                    sy.Str(), type_schema
                )
            })
        )
    })

    components = sy.Map({'components': sy.EmptyDict() | schemas})
    return components
    # return sy.Map({'components': sy.EmptyDict() | sy.Any()})


def openapi_preamble_schema():
    return sy.Map({
        sy.Optional('openapi'): sy.Str(),
        sy.Optional('info'): sy.Map({
            sy.Optional('title'): sy.Str(),
            sy.Optional('description'): sy.Str(),
            sy.Optional('termsOfService'): sy.Str(),
            sy.Optional('version'): sy.Str()
        }),
        sy.Optional('paths'): sy.Map({
            sy.Optional('/'): sy.Any()
        })
    })


# def anvil_yaml_schema() -> sy.Map:
#     """
#     Generates a strictyaml schema
#
#     Returns
#     -------
#         Schema object
#     """
#     # schema used by strictyaml to parse the text
#     schema = sy.Map({
#         'db_schema': sy.MapPattern(
#             sy.Str(),
#             sy.Map({
#                 'title': sy.Str(),
#                 'client': sy.Str(),
#                 'server': sy.Str(),
#                 'columns': sy.Seq(sy.Map({
#                     'name': sy.Str(),
#                     'admin_ui': sy.Any(),
#                     'type': sy.Str(),
#                     sy.Optional('target'): sy.Str()
#                 }))
#             })
#         )
#     })
#     # anvil.yaml uses 'flow style' in certain places.
#     return schema

def anvil_yaml_schema() -> sy.MapPattern:
    """
    Generates a strictyaml schema

    Returns
    -------
        Schema object
    """
    # schema used by strictyaml to parse the text
    schema = sy.MapPattern(sy.Str(), sy.Any())
    return schema
