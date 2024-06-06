from llama_cpp_client.utils import embed
import json
import re


def join_ann(array):
    annotation = ' '.join([v for k, v in array.items() if k == 'medication_name' and v is not None]).lower()
    return re.sub('[^.A-Za-z0-9]+', '', annotation)


def join_ann_embed(dictionary):
    return ' '.join([v for k, v in dictionary.items() if k != 'line']).lower()


def embed_fn(string: str):
    string = string.lower()
    return json.loads(embed('147.189.192.78:8080', string).text)['embedding']
