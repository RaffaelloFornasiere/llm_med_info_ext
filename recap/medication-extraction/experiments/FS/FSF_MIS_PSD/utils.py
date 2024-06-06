import json
import os


def add_examples_csv(inputs: list = None, **kwargs):
    document = inputs[0].input.value['text']
    example = json.load(open(kwargs['examples_dir'] + os.listdir(kwargs['examples_dir'])[0], 'r'))
    example_doc = example['text']
    example_csv = '\n'.join(
        [';'.join([value for value in list(row.values())[:4]]) for row in example['annotations']])
    return {'example_doc': example_doc, 'example_csv': example_csv, 'document': document}

def add_examples_json(inputs: list = None, **kwargs):
    document = inputs[0].input.value['text']
    example = json.load(open(kwargs['examples_dir'] + os.listdir(kwargs['examples_dir'])[0], 'r'))
    example_doc = example['text']

    example_json = [{k:v for k,v in item.items() if k != 'line'} for item in example['annotations']]


    return {'example_doc': example_doc, 'example_json': example_json, 'document': document}



def map_input(inputs: list = None):
    return inputs[0].output.value


def map_ita_json_to_json(inputs: list = None):
    json = inputs[0].output.value
    json = [
        {
            'medication_name': row['nome_farmaco'] if 'nome_farmaco' in row else None,
            'dosage': row['dosaggio'] if 'dosaggio' in row else None,
            'mode': row['modalità'] if 'modalità' in row else None,
            'frequency': row['frequenza'] if 'frequenza' in row else None,
        }
        for row in json]
    return json


def map_table_to_json(inputs: list = None) -> list:
    table = inputs[0].output.value
    table = [
        {
            'medication_name': row[0],
            'dosage': row[1] if len(row) > 1 else None,
            'mode': row[2] if len(row) > 2 else None,
            'frequency': row[3] if len(row) > 3 else None,
        }
        for row in table if len(row) > 0 and ''.join(row).strip() != '']
    return table
