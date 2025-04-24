
# LLM Experimentation Framework

A configurable pipeline architecture for running and evaluating large language model (LLM) experiments.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Creating an Experiment](#creating-an-experiment)
- [Running Experiments](#running-experiments)
- [Evaluating Results](#evaluating-results)
- [Advanced Configuration](#advanced-configuration)
- [Directory Structure](#directory-structure)
- [Common Workflows](#common-workflows)

## Overview

This framework allows you to:
- Configure multi-step LLM pipelines with flexible input/output mappings
- Run experiments across datasets using various models
- Evaluate extraction performance against ground truth
- Reuse components across different experiments

## Getting Started

### Prerequisites

- Python 3.8+
- Access to LLM endpoints (configured in experiment configs)

### Quick Start

1. Copy an existing experiment as a template:
   ```bash
   cp -r src/medication-extraction/experiments/P/P_MIS_PSD my-new-experiment
   ```

2. Modify the configuration files as needed:
   ```bash
   cd my-new-experiment
   # Edit config_json.json
   ```

3. Run the experiment:
   ```bash
   python run.py
   ```

## Creating an Experiment

### Required Files

Each experiment needs:
- **Configuration file(s)** (`config_*.json`)
- **Prompt template(s)** (`prompt_*.txt`)
- **Model parameter file(s)** (`params.json`)
- **Run script** (`run.py`)
- Optional **utility functions** (`utils.py`)

### Configuration Structure

The `config_*.json` file defines your experiment:

```json
{
  "experiment_name": "My Extraction Experiment",
  "experiment_code": "my_experiment_code",
  "dataset": {
    "name": "Dataset Name",
    "code": "DS_CODE",
    "dir": "path/to/dataset/directory"
  },
  "model": {
    "name": "model_name",
    "code": "MODEL_CODE",
    "url": "api.endpoint.url"
  },
  "steps": [
    {
      "id": 0,
      "stepClass": "InputStep",
      "args": {
        "name": "input"
      }
    },
    {
      "id": 1,
      "stepClass": "Step",
      "args": {
        "name": "extraction_step",
        "prompt.txt": "prompt_1.txt",
        "params.json": "params.json",
        "model": "MODEL_CODE",
        "utils.py": [
          {
            "function_name": "map_input_function",
            "arg_name": "map_input"
          },
          {
            "function_name": "map_output_function",
            "arg_name": "map_output"
          }
        ],
        "inputs": [0]
      }
    }
  ],
  "outputFileName": "result_my_experiment.json"
}
```

### Available Step Classes

| Step Class | Purpose | Required Args |
|------------|---------|---------------|
| `InputStep` | Starting point for input | `name` |
| `Step` | LLM-based operation | `model`, `prompt`, `params`, `map_input`, `map_output`, `inputs` |
| `ParseJSONStep` | Parse LLM output as JSON | `inputs` |
| `ParseCSVStep` | Parse LLM output as CSV | `separator`, `inputs` |
| `MapStep` | Apply transformation without LLM | `map_input`, `inputs` |

## Running Experiments

Create a `run.py` file in your experiment directory:

```python
from step.exec import *

run('config_json.json', True)  # Second parameter enables debug output
```

Execute it:

```bash
python run.py
```

The framework will:
1. Load your configuration
2. Build the step pipeline
3. Process each dataset sample
4. Save results to the specified output file

## Evaluating Results

### Evaluation Configuration

Create an `eval.json` configuration:

```json
{
  "experiments_dir": "path/to/experiment/results",
  "experiments_file_pattern": "result_.*\\.json",
  "evaluations": [
    {
      "className": "FullRowExactMatch",
      "args": {
        "name": "Exact Match Evaluation"
      }
    },
    {
      "className": "PartialMatch",
      "args": {
        "name": "Partial Match Evaluation",
        "join_ann": {
          "type": "function",
          "module": "utils",
          "function_name": "join_function"
        }
      }
    }
  ]
}
```

### Running Evaluation

Execute:

```bash
python eval/run_eval.py
```

The framework computes precision, recall, and F1 scores for each evaluation method specified in your configuration.

## Advanced Configuration

### Custom Mapping Functions

Create a `utils.py` file with functions to map inputs/outputs between steps:

```python
def map_input_function(inputs):
    # Transform inputs before passing to the LLM
    return {"context": inputs[0]["text"]}

def map_output_function(output, inputs):
    # Process LLM output
    return {"extracted_data": output, "original": inputs[0]}
```

Reference these functions in your configuration:

```json
"utils.py": [
  {
    "function_name": "map_input_function",
    "arg_name": "map_input"
  }
]
```

### Dataset Format

Each dataset file should be a JSON object containing:
- `text`: The input document
- `annotations`: Ground truth data for evaluation

## Directory Structure

```
experiment_dir/
├── config_*.json        # Configuration files
├── prompt_*.txt         # Prompt templates
├── params.json          # LLM parameters
├── utils.py             # Custom functions
├── run.py               # Run script
└── result_*.json        # Experiment results
```

## Common Workflows

### 1. Adapting Existing Experiments

1. Copy a similar experiment directory
2. Modify prompts and configuration
3. Run and evaluate

### 2. Comparing Models

1. Create multiple configurations with different models
2. Run each configuration
3. Evaluate all results for comparison

### 3. Optimizing Prompts

1. Create variations of prompt files
2. Run experiments with each variant
3. Compare evaluation metrics

### 4. Multi-Step Reasoning

Configure a pipeline with intermediate steps:
1. Initial extraction
2. Refinement/filtering
3. Output formatting

Each step can use different prompts and mapping functions to progressively transform the data.

---

For examples, see the experiment directories under `src/medication-extraction/experiments/`.
