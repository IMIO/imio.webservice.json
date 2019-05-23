# -*- coding: utf-8 -*-

import os
import json


def get_schemas(name, version):
    """ Returns the input and output schemas for the given name an version """
    schema_path = get_schema_path(name, version)
    if os.path.exists(schema_path) is False:
        return None, None

    input = get_schema_content(schema_path, "in")
    output = get_schema_content(schema_path, "out")

    if input:
        input[u"version"] = version
        input[u"name"] = name
    if output:
        output[u"version"] = version
        output[u"name"] = name
    return input, output


def get_schema_path(name, version, subdirectory=None):
    """Return the schema directory path"""
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, "schema", name, version)


def get_schema_content(path, filename):
    filepath = os.path.join(path, "%s.json" % filename)
    if os.path.exists(filepath):
        f = open(filepath, "r")
        schema = json.load(f)
        f.close()
        return schema
