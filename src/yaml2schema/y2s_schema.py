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
        sy.Optional('paths'): sy.Map({
            sy.Optional('/'): sy.Any()
        })
    })


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
