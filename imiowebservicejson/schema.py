# -*- coding: utf-8 -*-

import os
import json


def get_schemas(name, version):
    """ Returns the input and output schemas for the given name an version """
    current_dir = os.path.dirname(__file__)
    schema_path = os.path.join(current_dir, 'schema', name, version)
    if os.path.exists(schema_path) is False:
        return None, None
    input_file = open(os.path.join(schema_path, 'in.json'), 'r')
    output_file = open(os.path.join(schema_path, 'out.json'), 'r')

    input = json.load(input_file)
    input[u'version'] = version
    input[u'name'] = name
    input_file.close()
    output = json.load(output_file)
    output[u'version'] = version
    output[u'name'] = name
    output_file.close()
    return input, output
