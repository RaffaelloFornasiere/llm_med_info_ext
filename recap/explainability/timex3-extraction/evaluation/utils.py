import json5

from llama_cpp_client.utils import *
import json
import re


def join_ann_value(array):
    return array['date_value'] if 'date_value' in array else ''


def clean_ann(array):
    # remove annotations with same medication_name
    medication_names = list(set([v['medication_name'].strip() for v in array if v['medication_name'] is not None]))
    new_array = []
    for ann in array:
        if ann['medication_name'] in medication_names:
            new_array.append(ann)
            medication_names.remove(ann['medication_name'])
    return new_array


def join_ann(array):
    annotation = ' '.join([v for k, v in array.items() if isinstance(v, str)][:-1]).lower()
    return re.sub('[^.A-Za-z0-9]+', '', annotation)


def join_ann_embed(dictionary):
    return ' '.join([v for k, v in dictionary.items() if k != 'line']).lower()


def embed_fn(string: str):
    string = string.lower()
    return json.loads(embed('147.189.192.78:8080', string).text)['embedding']


prompt = """
<|begin_of_text|><|start_header_id|>user<|end_header_id|>
```extracted.json
{extracted}
```

```ground_truth.json
{ground_truth}
```

Do they refer to the same medication? answer only yes or no
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""


def callback_model(extracted, ground_truth):
    _prompt = prompt.format(extracted=json.dumps(extracted, indent=2), ground_truth=json.dumps(ground_truth, indent=2))

    res = []
    for i in range(1):
        out = call_model('147.189.192.78:8080', _prompt, n_predict=2048, temperature=0.7, cache_prompt=False,
                         stop=['<|im_end|>', '<|eot_id|>', '```'])
        out = 'yes' in out.lower()
        res.append(out)
        if len(res) > 2 and all(res):
            break
    res = sum([1 if r else -1 for r in res])
    return res > 0
