import os
import logging
import time

exp_name = "git-2"
logging.basicConfig(filename=f'raha/logs/{exp_name}.log', level=logging.DEBUG)

repition = range(1, 2)
labeling_budgets = range(2, 3)
sandbox_path = "/home/fatemeh/ED-Scale-mp-dgov/ED-Scale/git-2-tables/tables"
results_path = os.path.join("/home/fatemeh/EDS-BaseLines/Raha/raha/res-git-250", f"exp_{exp_name}")
if not os.path.exists(results_path):
    os.makedirs(results_path)

datasets = []

for dir in os.listdir(sandbox_path):
    datasets.append(os.path.join(sandbox_path , dir))

logging.info(f"datasets: {datasets}")

def run_raha(dataset, results_path, labeling_budget, exec_number):
    python_script = f'''python raha/detection.py \
                             --results_path {results_path} --base_path {dataset} --dataset {os.path.basename(dataset)} --labeling_budget {labeling_budget} --execution_number {exec_number}'''
    logging.info("python_script: " + python_script)
    os.system(python_script)

s_time = time.time()
for exec_number in repition:
    for labeling_budget in labeling_budgets:
        for dataset in datasets:
            try:
                run_raha(dataset, results_path, labeling_budget, exec_number)
            except Exception as e:
                logging.error(dataset, e)
e_time = time.time()
print("Total Run Time:")
print(e_time - s_time)