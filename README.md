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
