### Experiments List

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
