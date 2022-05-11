OPENAPI_TYPES = {'string': 'string',
                 'datetime': 'string',
                 'date': 'string',
                 'number': 'integer',
                 'number2': 'number',
                 'bool': 'boolean',
                 'link_single': 'object',
                 'simpleObject': 'object',
                 'link_multiple': 'array',
                 'media': 'string',
                 }
OPENAPI_FORMATS = {'date': 'date',
                   'datetime': 'date-time',
                   'integer': 'int32',
                   'bigint': 'int64',
                   'number2': 'float',
                   'text': 'text',  # for pydal's large strings
                   'media': 'byte'
                   }

Openapi_preamble = """openapi: 3.0.3
info:
    title: Example openapi file
    description: File can be used as an input to 'yaml2schema'.
    termsOfService: https://unlicense.org
    version: 0.0.1
paths:
    /:
"""
