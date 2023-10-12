# EDS - Raha Variants
This repository contains several variants of Raha. Specifically, there are three different label distribution variations.

### Raha - 2LabelsPerCol (2LPC)
In this version, Raha randomly selects one column at a time and labels two cells from that column. 
This is repeated until the labeling budget is exhausted.

### Raha - 20LabelsPerCol (20LPC)
In this version, Raha randomly selects one column at a time and labels 20 cells from that column.
This is repeated until the labeling budget is exhausted.
### Raha - RandomTables (RT)
In this version, the datasets are shuffled and then assigned one label at a time until the labeling budget is exhausted.


## Installation
Create a fresh python environment
```shell
cd raha
conda env create -f benchmarks-env.yml
```
## Usage
#### Raha - 2LPC and 20LPC
Both Raha versions will be executed by running:

``python raha/raha/eds_run_experiments/raha_not_enough_labels_column_wise.py``

This version can be configured in ``raha/raha/eds_run_experiments/hydra_configs/column_wise.yaml`` and 
``raha/raha/eds_run_experiments/hydra_configs/shared.yaml``
#### Raha - RT
This version can be executed by running:

``python raha/raha/eds_run_experiments/raha_not_enough_labels_lake.py``

This version can be configured in ``raha/raha/eds_run_experiments/hydra_configs/table_wise.yaml`` and 
``raha/raha/eds_run_experiments/hydra_configs/shared.yaml``
#### Raha - Standard
The standard Raha version can be executed by running:

``python raha/raha/eds_run_experiments/raha_enough_labels_lake.py``

This version can be configured in ``raha/raha/eds_run_experiments/hydra_configs/shared.yaml`` and 
``raha/raha/eds_run_experiments/hydra_configs/shared.yaml``