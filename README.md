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
1. Create a fresh python environment
2. ```shell
   cd raha 
   pip install -e .
   ```
## Usage
#### Raha - 2LPC and 20LPC
Both Raha versions will be executed by running:

``python Raha/raha/eds_run_experiments/raha_not_enough_labels_column_wise.py``

#### Raha - RT
This version can be executed by running:

``python Raha/raha/eds_run_experiments/raha_not_enough_labels_lake.py``

#### Raha - Standard
The standard Raha version can be executed by running:

``python Raha/raha/eds_run_experiments/raha_enough_labels_lake.py``