# Experiments List

Models testes: Mistral [MIS], Mixtral8x7b [MIX], Vicuna [VIC], llama3 [LL3]
<br>
Datasets: n2c2-2009 [N2C2], Policlinico San Donato [PSD], i2b2-2012 [I2B2]


Techniques: 
- Simple Zero-shot [SZS]
- Few-shot [FS]
  - full examples [FSF]
  - chunks [FSC]
- Pipeline [P]
  - 2 steps (extraction + formatting) [P2]
    - multiple formatting?
  - 3 steps (counting + extraction + formatting ) [P3]
  - 4 steps (counting + extraction + double check + formatting) [P4]
  - Multi Prompt [MP]


experiments naming:  XXXX[_ISL]_YYYY_ZZZZ_TTTT
- XXXX: experiment_name
  - ISL: if the experiment is in the ISL setting
- YYYY: model_name
- ZZZZ: dataset_name
- TTTT: output_format

# How to run the experiments
In each leaf folder there is a `run.py` file that takes as input a `.json` file with all the specifications of the experiment. 
The `run.py` file will run the experiment and save the results in the same folder under the name specified in the `.json` file.
If no `.json` file is provided, the `run.py` file will assume that  `config_json.json` and `config_csv.json` files are present in the folder.


## `Config.json`
In the `config.json` file you can specify almost anything you want to run the experiment.
The minimal information you need to provide is:
- `experiment_name`: the name of the experiment
- `dataset`: the dataset you want to use
- `model`: the model you want to use
- `steps`: the steps you want to run
- `output_file`: the output file where you want to save the results

### `dataset`
the field `dataset` is a dictionary that contains the following fields:
- `name`: the name of the dataset
- `code`: a unique code of the dataset
- `path`: the path to the dataset

the dataset samples must follow the following structure: 
```
{
  "text": "text of the sample",
  "annotations": [
    {
      ... fields of the annotation
      'line': line of the annotation
    }
  ]
}
```

### `model`
the field `model` is a dictionary that contains the following fields:
- `name`: the name of the model
- `code`: a unique code of the model
- `url`: the url to the model
- `openai_api`: a boolean that specifies if the model uses the openai api

**Note:** The `openai_api` is not used in the current version of the code.



### `steps`
This field contains a list of steps from library Step. Each step has the following minimal structure:
- `id`: the id of the step
- `stepClass`: the name of the step class
- `args`: the arguments of the step

the id of the step is used to reference that step in other steps input.
The args may vary depending on the step class.








