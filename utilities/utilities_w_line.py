from utilities.utilities import map_output, map_input, map_input_few_shot, get_most_representative_example
import json5 as json
import os
from step.step import Step

def add_line_numbers(doc):
    lines = doc.split('\n')
    lines.insert(0, 'line | text')
    lines = [f"{i + 1:03d} | {line}" for i, line in enumerate(lines)]
    return '\n'.join(lines)


def map_input_w_line(inputs: list = None) -> dict:
    return {'document': add_line_numbers(inputs[0].output.value['text'])}


def map_output_step_1(model_input, output) -> dict:
    output = Step.map_output(model_input, output)
    return model_input + output


def map_input_step_2(inputs: list = None) -> dict:
    return {'history': inputs[0].output.value}


def map_table_to_json_w_line(inputs: list = None) -> list:
    table = inputs[0].output.value
    table = [
        {
            'line': row[0],
            'medication_name': row[1] if len(row) > 1 else '',
            'dosage': row[2] if len(row) > 2 else '',
            'mode': row[3] if len(row) > 3 else '',
            'frequency': row[4] if len(row) > 4 else ''
        }
        for row in table if len(row) > 0 and ''.join(row).strip() != '']
    return table


def map_ita_json_to_json_w_line(inputs: list = None):
    json = inputs[0].output.value
    json = [
        {
            'medication_name': row['nome_farmaco'] if 'nome_farmaco' in row else None,
            'dosage': row['dosaggio'] if 'dosaggio' in row else None,
            'mode': row['modalità'] if 'modalità' in row else None,
            'frequency': row['frequenza'] if 'frequenza' in row else None,
            'line': row['linea'] if 'linea' in row else None,
        }
        for row in json]
    return json


def add_examples_csv_chunks_w_line(inputs: list = None, **kwargs):
    document = inputs[0].input.value['text']
    document = add_line_numbers(document)
    example_files = os.listdir(kwargs['examples_dir'])
    examples = [json.load(open(kwargs['examples_dir'] + file, 'r')) for file in example_files]
    for example in examples:
        example['text'] = add_line_numbers(example['text'])

    chunk_size = 15
    chunks = get_most_representative_example(examples, chunk_size)

    examples = ''
    for i, chunk in enumerate(chunks):
        examples += '```example_document' + str(i + 1) + '.txt\n'
        examples += chunk['text'] + '\n'
        examples += '```\n'
        examples += '``` example_extraction_' + str(i + 1) + '.csv\n'
        examples += 'line;medication_name;dosage;mode;frequency\n'
        for ann in chunk['annotations']:
            examples += ';'.join([ann['line'], ann['medication_name'], ann['medication_dosage'], ann['mode'],
                                  ann['frequency']
                                  ]) + '\n'
        examples += '```\n---\n'

    return {'examples': examples, 'document': document}


def add_examples_json_chunks_w_line(inputs: list = None, **kwargs):
    document = inputs[0].input.value['text']
    document = add_line_numbers(document)
    example_files = os.listdir(kwargs['examples_dir'])
    examples = [json.load(open(kwargs['examples_dir'] + file, 'r')) for file in example_files]
    for example in examples:
        example['text'] = add_line_numbers(example['text'])
    chunk_size = 10
    chunks = get_most_representative_example(examples, chunk_size)
    examples = ''
    for i, chunk in enumerate(chunks):
        examples += '``` example_document' + str(i + 1) + '.txt\n'
        examples += chunk['text'] + '\n'
        examples += '```\n'
        examples += '``` example_extraction_' + str(i + 1) + '.json\n'
        annotations = chunk['annotations']
        annotations = [{k: v for k, v in ann.items()} for ann in annotations]
        examples += json.dumps(annotations, indent=4) + '\n'
        examples += '```\n---\n'

    return {'examples': examples, 'document': document}


def add_examples_csv_w_line(inputs: list = None, **kwargs):
    document = inputs[0].input.value['text']
    document = add_line_numbers(document)
    example = json.load(open(kwargs['examples_dir'] + os.listdir(kwargs['examples_dir'])[0], 'r'))
    example_doc = example['text']
    example_doc = add_line_numbers(example_doc)
    example_csv = '\n'.join(
        [';'.join([value for value in list(row.values())]) for row in example['annotations']])
    return {'example_doc': example_doc, 'example_csv': example_csv, 'document': document}


def add_examples_json_w_line(inputs: list = None, **kwargs):
    document = inputs[0].input.value['text']
    example = json.load(open(kwargs['examples_dir'] + os.listdir(kwargs['examples_dir'])[0], 'r'))
    example_doc = example['text']
    example_doc = add_line_numbers(example_doc)

    example_json = [{k: v for k, v in item.items()} for item in example['annotations']]
    example_json = json.dumps(example_json, indent=4)
    return {'example_doc': example_doc, 'example_json': example_json, 'document': document}
