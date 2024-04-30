import os
import json
import genesis_cloud.utils as u
from tqdm import tqdm
from step.step import *
import importlib
import sys


def run(config_file='config.json', verbose: bool = False):
    config = json.load(open(config_file, 'r'))
    experiment_name = config['experiment_name']

    dataset_config = config['dataset']
    model_config = config['model']
    model = LLamaCppModel(model_config['url'])

    dataset_files = os.listdir(dataset_config['dir'])
    dataset = []
    for file in dataset_files:
        with open(dataset_config['dir'] + file) as f:
            obj = json.load(f)
            obj['file'] = file
            dataset.append(obj)

    def read_args(key, value):
        file_type = key.split('.')[-1]
        arg_name = key.split('.')[0]
        if file_type == 'json':
            return {arg_name: json.load(open(value, 'r'))}
        elif file_type == 'txt':
            return {arg_name: open(value, 'r').read()}
        elif file_type == 'py':
            function = getattr(importlib.import_module(arg_name), value['function_name'])
            return {value['arg_name']: function}
        elif arg_name == 'model':
            return {arg_name: model}
        else:
            return {arg_name: value}

    steps_config = config['steps']
    steps = []
    for step_config in steps_config:
        args = step_config['args']
        file_args = [read_args(k, v) for k, v in args.items()]
        args = {k: v for d in file_args for k, v in d.items()}

        if 'inputs' in args:
            inputs = list(map(lambda x: x['id'], steps))
            inputs = [steps[inputs.index(_input)]['step'] for _input in args['inputs']]
            args['inputs'] = inputs

        step = {
            'id': step_config['id'],
            'step': globals()[step_config['stepClass']](**args),
        }
        steps.append(step)

    steps = [step['step'] for step in steps]

    pipeline = Pipeline(steps[-1])
    ans = []
    for data in tqdm(dataset):
        steps[0].input.value = data
        res = pipeline()
        ans.append({'file': data['file'], 'out': res})

    result = {
        'experiment_name': experiment_name,
        'inputs': [file['file'] for file in dataset],
        'outputs': ans,
    }
    json.dump(result, open(config['outputFileName'], 'w'))
