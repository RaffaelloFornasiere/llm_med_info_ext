import json
from step.step import *
from utilities.utilities import *


def map_input_1(inputs: list = None) -> dict:
    return {'document': inputs[0].output.value['text']}


def map_input_step_2(inputs: list = None) -> dict:
    return {'history': inputs[0].output.value}


def map_output_step_1(model_input, output) -> dict:
    output = Step.map_output(model_input, output)
    return model_input + output


def map_output_2(model_input, output) -> dict:
    return model_input[model_input.rfind('['):] + output
