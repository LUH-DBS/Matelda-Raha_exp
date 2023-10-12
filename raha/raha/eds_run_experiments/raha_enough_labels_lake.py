import os
import logging
import time
from pathlib import Path

import hydra

from raha.detection import main


@hydra.main(version_base=None, config_path="hydra_configs", config_name="table_wise")
def start(cfg):
    exp_name = "raha-enough-labels"
    logging.basicConfig(filename=str(Path(cfg["logs"]["path_to_log_file"]).resolve()), level=logging.DEBUG)

    repetition = range(1, cfg["shared"]["repetitions"] + 1)
    labeling_budgets = cfg["experiment"]["labeling_budgets"]

    sandbox_path = Path(cfg["shared"]["sandbox_path"]).resolve()
    dataset_name = sandbox_path.stem
    sandbox_path = str(sandbox_path)
    results_folder = str(Path(cfg["shared"]["results_path"]).resolve().joinpath(dataset_name).resolve())

    results_path = os.path.join(results_folder, f"exp_{exp_name}")
    if not os.path.exists(results_path):
        os.makedirs(results_path)

    datasets = []

    for dir in os.listdir(sandbox_path):
        datasets.append(os.path.join(sandbox_path, dir))

    logging.info(f"datasets: {datasets}")

    s_time = time.time()
    for execution_number in repetition:
        for labeling_budget in labeling_budgets:
            for dataset_path in datasets:
                try:
                    dataset_name = os.path.basename(dataset_path)
                    main(results_path, dataset_path, dataset_name, labeling_budget, execution_number,
                         column_wise_evaluation=False, column_idx=0)
                except Exception as e:
                    logging.error(dataset_path, e)
    e_time = time.time()
    logging.info("Total Run Time:")
    logging.info(e_time - s_time)


if __name__ == '__main__':
    start()
