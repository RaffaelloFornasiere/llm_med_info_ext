from step.step import Step
import json
import os


def map_output(model_input, output) -> dict:
    output = Step.map_output(model_input, output)
    return model_input[model_input.rfind('['):] + output


def map_input(inputs: list = None) -> dict:
    return {'document': inputs[0].output.value['text']}


def map_input_few_shot(inputs: list = None):
    return inputs[0].output.value


def get_most_representative_example(examples, chunk_size=15):
    chunks = []
    for example in examples:
        ann_lines = [line['line'] for line in example['annotations']]
        densities = [len([k for k in ann_lines if int(x) <= int(k) <= int(x) + chunk_size]) for x in ann_lines]
        i = int(ann_lines[densities.index(max(densities))])
        chunk = {
            'text': '\n'.join(example['text'].split('\n')[max(i-1, 0):i + chunk_size]),
            'annotations': [ann for ann in example['annotations'] if i <= int(ann['line']) <= i + chunk_size]
        }
        chunks.append(chunk)
    return chunks


def add_examples_csv_chunks(inputs: list = None, **kwargs):
    document = inputs[0].input.value['text']
    example_files = os.listdir(kwargs['examples_dir'])
    examples = [json.load(open(kwargs['examples_dir'] + file, 'r')) for file in example_files]

    chunk_size = 15
    chunks = get_most_representative_example(examples, chunk_size)

    examples = ''
    for i, chunk in enumerate(chunks):
        examples += '```esempio_documento_' + str(i + 1) + '.txt\n'
        examples += chunk['text'] + '\n'
        examples += '```\n'
        examples += '``` esempio_estrazione_' + str(i + 1) + '.csv\n'
        examples += 'farmaco;dosaggio;modalità;frequenza\n'
        for ann in chunk['annotations']:
            examples += ';'.join([value for value in list(ann.values())[:4]]) + '\n'
        examples += '```\n---\n'

    return {'examples': examples, 'document': document}


def add_examples_json_chunks(inputs: list = None, **kwargs):
    document = inputs[0].input.value['text']
    example_files = os.listdir(kwargs['examples_dir'])
    examples = [json.load(open(kwargs['examples_dir'] + file, 'r')) for file in example_files]

    chunk_size = 10
    chunks = get_most_representative_example(examples, chunk_size)
    examples = ''
    for i, chunk in enumerate(chunks):
        examples += '``` example_document' + str(i + 1) + '.txt\n'
        examples += chunk['text'] + '\n'
        examples += '```\n'
        examples += '``` example_extraction_' + str(i + 1) + '.json\n'
        annotations = chunk['annotations']
        annotations = [{k: v for k, v in ann.items() if k != 'line'} for ann in annotations]
        examples += json.dumps(annotations, indent=4) + '\n'
        examples += '```\n---\n'

    return {'examples': examples, 'document': document}


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

    example_json = [{k: v for k, v in item.items() if k != 'line'} for item in example['annotations']]
    example_json = json.dumps(example_json, indent=4)
    return {'example_doc': example_doc, 'example_json': example_json, 'document': document}
