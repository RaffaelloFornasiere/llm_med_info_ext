import genesis_cloud.utils as u
import json
import json5
import inspect
from json import JSONEncoder


class Model(JSONEncoder):
    def __call__(self, prompt, **params):
        raise NotImplementedError()

    def __str__(self):
        return self.__class__.__name__


class LLamaCppModel(Model):
    def __init__(self, instance_url):
        self.instance_url = instance_url

    def __call__(self, prompt, **params):
        return u.call_model(self.instance_url, prompt, **params)


class Step:
    class Input:
        def __init__(self, value):
            self.value = value

    class Output:
        def __init__(self, value):
            self.value = value

    def __init__(self, model: Model = None, name: str = None, prompt: str = None, params=None, map_input=None,
                 map_output=None, inputs=None):
        self.model = model
        self.name = name
        self.prompt = prompt
        self.params = params
        self.map_input = map_input
        self.map_output = map_output if map_output else Step.map_output
        self.input = Step.Input(None)
        self.output = Step.Output(None)
        self.inputs = inputs

    def get_input_steps(self):
        if self.inputs is None:
            return []
        return [step for step in self.inputs if isinstance(step, Step)]

    @staticmethod
    def map_output(output):
        output = output.replace('<dummy32000>', '')
        if not output.endswith('<|im_end|>'):
            output += '<|im_end|>'
        return output

    @staticmethod
    def from_step(step):
        return Step(step.model, step.prompt, step.params, step.map_input, step.map_output, inputs=step.inputs)

    def get_model_input(self):
        input_text = self.map_input(inputs=self.inputs)
        return self.prompt.format(**input_text) if input_text else self.prompt

    def __call__(self):
        model_input = self.get_model_input()
        output = self.model(model_input, **self.params)
        self.output.value = self.map_output(output) if self.map_output else output
        return self.output.value

    def __str__(self):
        return json.dumps({k: v for k, v in {
            'name': self.name,
            'model': self.model.__class__.__name__ if self.model else None,
            'prompt': self.prompt,
            'params': self.params,
            'map_input': inspect.getsource(self.map_input) if self.map_input else None,
            'map_output': inspect.getsource(self.map_output) if self.map_output else None,
            'inputs': ', '.join([_input.name for _input in self.get_input_steps()])
        }.items() if v is not None})


class InputStep(Step):
    def __init__(self, name, input_text=''):
        super().__init__(name=name)
        self.input = Step.Input(input_text)

    def __call__(self):
        self.output.value = self.input.value
        return self.input.value


class ParseJSONStep(Step):
    def __init__(self, name, inputs):
        super().__init__(name=name, inputs=inputs)

    def __call__(self):
        output = self.inputs[0].output.value
        output = output.replace('<dummy32000>', '')
        output = output.replace('```', '')
        if output.endswith('<|im_end|>'):
            output = output[:output.index('<|im_end|>')]
        try:
            output = json5.loads(output)
        except:
            output = {'error': output}
        self.output.value = output
        return output


class MapStep(Step):
    def __init__(self, name, map_input, inputs, map_input_args = None):
        super().__init__(name=name, map_input=map_input, inputs=inputs)
        self.map_input_args = map_input_args

    def __call__(self):
        if self.map_input_args:
            output = self.map_input(self.inputs[0].output.value, **self.map_input_args)
        else:
            output = self.map_input(self.inputs[0].output.value)
        self.output.value = output
        return self.output.value


class ParseCSVStep(Step):
    def __init__(self, name, separator, inputs):
        super().__init__(name=name, inputs=inputs)
        self.separator = separator

    def __call__(self):
        output = self.inputs[0].output.value
        output = output.replace('<dummy32000>', '')
        output = output.replace('```', '')
        if output.endswith('<|im_end|>'):
            output = output[:output.index('<|im_end|>')]

        output = output.split('\n')
        output = [line.split(self.separator) for line in output]
        self.output.value = output
        return output


class ForStep(Step):
    def __init__(self, model: Model = None, name: str = None, prompt: str = None, params=None, map_input=None,
                 map_output=None, inputs=None, iterations=None):
        super().__init__(model, name, prompt, params, map_input, map_output, inputs)
        self.iterations = iterations

    def __call__(self):
        output = []
        for i, iteration in enumerate(self.iterations):
            self.inputs.append(iteration)
            model_input = self.get_model_input()
            output = self.model(model_input, **self.params)
            output.append({'iteration': i, 'output': self.map_output(output) if self.map_output else output})
            self.inputs.pop()
        self.output.value = output
        return output


class Pipeline:
    def __init__(self, last_step):
        self.steps = None
        self.edges = None
        self.build_execution_order_bfs(last_step)

    def build_execution_order_bfs(self, last_step):
        self.steps = []
        queue = [last_step]
        while queue:
            step = queue.pop(0)
            if isinstance(step, Step):
                self.steps.append(step)
                queue = step.get_input_steps() + queue
        self.steps = self.steps[::-1]
        ## remove duplicates steps, keep the first one
        self.steps = list(dict.fromkeys(self.steps))

    def print_graph_dependencies(self):
        dot = graphviz.Digraph(comment='Dependencies', graph_attr={'rankdir': 'LR'})
        for step in self.steps:
            dot.node(step.name, step.name)
            for input_step in step.get_input_steps():
                dot.edge(input_step.name, step.name)
        return dot

    def __call__(self):
        for step in self.steps:
            step()
        return self.steps[-1].output.value

    def __str__(self):
        return json.dumps([json.loads(str(step)) for step in self.steps])
