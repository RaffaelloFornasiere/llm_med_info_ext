from llama_cpp_client.utils import embed
import json


def join_ann(array):
    return ' '.join([v for k, v in array.items() if k != 'line'])


def embed_fn(string: str):
    string = string.lower()
    return json.loads(embed('147.189.192.78:8080', string).text)['embedding']
