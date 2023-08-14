import os
import logging
import time
from raha.detection import main

exp_name = "raha-enough-labels_1_25"
logging.basicConfig(filename=f'/home/fatemeh/results-aug/raha-enough-labels/1_25/logs/{exp_name}.log', level=logging.DEBUG)

repetition = range(1, 6)
labeling_budgets = [1, 5, 10, 15, 20]
sandbox_path = "/home/fatemeh/EDS-Raha_exp/Raha/raha/datasets/output_lake_1_25_processed"
results_path = os.path.join("/home/fatemeh/results-aug/raha-enough-labels/1_25", f"exp_{exp_name}")
if not os.path.exists(results_path):
    os.makedirs(results_path)

datasets = []

for dir in os.listdir(sandbox_path):
    datasets.append(os.path.join(sandbox_path , dir))

logging.info(f"datasets: {datasets}")

s_time = time.time()
for execution_number in repetition:
    for labeling_budget in labeling_budgets:
        for dataset_path in datasets:
            try:
                dataset_name = os.path.basename(dataset_path)
                main(results_path, dataset_path, dataset_name, labeling_budget, execution_number)
            except Exception as e:
                logging.error(dataset_path, e)
e_time = time.time()
logging.info("Total Run Time:")
logging.info(e_time - s_time)