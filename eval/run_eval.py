from eval.eval import *
import re
import json
import os
import importlib

def read_args(arg_name, value):
    if type(value) is not dict:
        return {arg_name: value}
    else:
        arg_type = value['type']
        if arg_type == 'json':
            return {arg_name: json.load(open(value['file'], 'r'))}
        elif arg_type == 'txt':
            return {arg_name: open(value['file'], 'r').read()}
        elif arg_type == 'function':
            function = getattr(importlib.import_module(value['module']), value['function_name'])
            return {arg_name: function}
        else:
            return {arg_name: value}



def run(config: str):
    config = json.load(open(config, 'r'))
    experiments_dir = config['experiments_dir']
    experiments_file_pattern = config['experiments_file_pattern']
    evaluations = config['evaluations']

    # recursively search for all experiment files
    experiment_files = []
    for root, dirs, files in os.walk(experiments_dir):
        for file in files:
            if re.match(experiments_file_pattern, file):
                experiment_files.append(os.path.join(root, file))

    for file in experiment_files:
        current_dir = os.getcwd()
        eval_json = json.load(open(file, 'r'))

        dataset_dir = str(eval_json['dataset_dir'])
        outputs = eval_json['outputs']
        data = []
        os.chdir(os.path.dirname(file))
        print(os.getcwd())
        for output in outputs:
            with open(os.path.join(dataset_dir, output['file']), 'r') as f:
                obj = json.load(f)
                obj['file'] = output['file']
                obj['extraction'] = output['out']
                data.append(obj)

        _aggregate_metrics = []
        for sample in data:
            if 'error' in sample['extraction']:
                sample['metrics'] = {
                    'precision': 0,
                    'recall': 0,
                    'f1_score': 0,
                }
                _aggregate_metrics.append(sample)
                continue
            extracted = sample['extraction']

            annotations = sample['annotations']
            original_text = sample['text']

            eval_metrics = {}
            for eval_conf in evaluations:
                args = {}
                for arg_name, arg_value in eval_conf['args'].items():
                    args.update(read_args(arg_name, arg_value))
                evalClass = globals()[eval_conf['className']](
                    annotations=annotations,
                    extracted=extracted,
                    original_text=original_text,
                    **args
                )
                evalClass.evaluate()
                metrics = evalClass.get_metrics()
                eval_metrics[eval_conf['className']] = metrics

            sample['metrics'] = eval_metrics
            _aggregate_metrics.append(sample)

        aggregate_metrics = {}
        for _eval in evaluations:
            aggregate_metrics[_eval['className']] = {
                'precision': sum(
                    [sample['metrics'][_eval['className']]['precision'] for sample in _aggregate_metrics]) / len(
                    _aggregate_metrics),
                'recall': sum([sample['metrics'][_eval['className']]['recall'] for sample in _aggregate_metrics]) / len(
                    _aggregate_metrics),
                'f1_score': sum(
                    [sample['metrics'][_eval['className']]['f1_score'] for sample in _aggregate_metrics]) / len(
                    _aggregate_metrics),
            }

        os.chdir(current_dir)
        json.dump(aggregate_metrics, open(file.replace('.json', '_eval.json'), 'w'), indent=4)
