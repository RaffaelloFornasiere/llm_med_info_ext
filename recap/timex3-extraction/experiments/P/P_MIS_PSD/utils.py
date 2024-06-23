import json
from step.step import *


def map_input(inputs: list = None) -> dict:
    return {'document': inputs[0].output.value['text']}


def map_input_2(inputs: list = None) -> dict:
    return {'history': inputs[0].output.value}


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


def map_output_1(model_input, output) -> dict:
    output = Step.map_output(model_input, output)
    return model_input + output


def map_output(model_input, output) -> dict:
    return model_input[model_input.rfind('['):] + output
