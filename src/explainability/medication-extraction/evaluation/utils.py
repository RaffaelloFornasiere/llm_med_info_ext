import json5

from llama_cpp_client.utils import *
import json
import re


def join_ann_name_only(array):
    annotation = ' '.join([v for k, v in array.items() if k == 'medication_name' and v is not None]).lower()
    return re.sub('[^.A-Za-z0-9]+', '', annotation)


def join_ann_line_only(array):
    annotation = ' '.join([str(v) for k, v in array.items() if k == 'line' and v is not None]).lower()
    return re.sub('[^.A-Za-z0-9]+', '', annotation)


def tokenize_fn(string: str):
    string = string.lower()
    return json.loads(embed('147.189.192.78:8080', string).text)['embedding']


def join_ann(array):
    value = array['medication_name']
    value = re.sub('[^.A-Za-z0-9]+', '', value).lower()
    return {'value': value, 'line': array['line'] if 'line' in array else None}
