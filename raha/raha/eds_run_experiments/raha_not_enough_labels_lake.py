import logging
import os
import pickle
from pathlib import Path
from random import shuffle

import hydra
import pandas as pd
from raha.detection import main


def run_raha(dataset_path, results_path, labeling_budget, exec_number):
    main(results_path, dataset_path, os.path.basename(dataset_path),
         labeling_budget, exec_number, column_wise_evaluation=False, column_idx=0)


def distribute_labels(labeling_budget_cells, sandbox_path, results_path):
    datasets_shape = dict()
    datasets_budget = dict()
    datasets_num_cells = dict()

    num_cols = 0
    num_rows = 0
    num_cells = 0

    for dir in os.listdir(sandbox_path):
        try:
            dataset_path = os.path.join(sandbox_path, dir)
            df = pd.read_csv(os.path.join(dataset_path, "dirty.csv"), sep=",", header="infer", encoding="utf-8",
                             dtype=str,
                             low_memory=False)
            datasets_shape[dataset_path] = df.shape
            num_cells_dataset = df.size
            datasets_num_cells[dataset_path] = num_cells_dataset
            datasets_budget[dataset_path] = 0
            num_cols += df.shape[1]
            num_rows += df.shape[0]
            num_cells += num_cells_dataset
        except Exception as e:
            print(dir, e)

    if labeling_budget_cells % num_cols == 0:
        labeling_budget_tuples_per_table = labeling_budget_cells / num_cols
        for dataset in datasets_shape:
            datasets_budget[dataset] = round(labeling_budget_tuples_per_table)
    else:
        asssigned_labels = 0
        non_eligable_datasets = 0
        while labeling_budget_cells > asssigned_labels and non_eligable_datasets < len(datasets_shape):
            dataset_names = list(datasets_num_cells.keys())
            shuffle(dataset_names)
            for dataset in dataset_names:
                dataset_num_cols = datasets_shape[dataset][1]
                remained_labels = labeling_budget_cells - asssigned_labels
                if remained_labels >= dataset_num_cols:
                    datasets_budget[dataset] += 1
                    asssigned_labels += dataset_num_cols
                    non_eligable_datasets = 0
                else:
                    non_eligable_datasets += 1

    with open(os.path.join(results_path, f"labeling_budget_{labeling_budget_cells}.pickle"), "wb") as f:
        pickle.dump(datasets_budget, f)
    return datasets_budget


def run_experiments(sandbox_path, results_path, labeling_budget_cells, exec_number):
    for label_budget in labeling_budget_cells:
        logging.info(f"label_budget: {label_budget}")
        datasets_budget = distribute_labels(label_budget, sandbox_path, results_path)
        for dataset in datasets_budget:
            logging.info(f"dataset: {dataset}")
            try:
                if datasets_budget[dataset] > 0:

                    results_path_raha = os.path.join(results_path,
                                                     "results_" + str(label_budget) + "_" + str(exec_number))
                    if not os.path.exists(results_path_raha):
                        os.makedirs(results_path_raha)
                    run_raha(dataset, results_path_raha, datasets_budget[dataset], exec_number)
                else:
                    logging.info(f"dataset {dataset} has no labeling budget")
            except Exception as e:
                print(dataset, e)


@hydra.main(version_base=None, config_path="hydra_configs", config_name="table_wise")
def start(cfg):
    logging.basicConfig(filename=str(Path(cfg["logs"]["path_to_log_file"]).resolve()),
                        level=logging.DEBUG)

    repetition = range(1, cfg["shared"]["repetitions"] + 1)
    labeling_budget = cfg["experiment"]["labeling_budgets"]
    n_cols = cfg["experiment"]["n_columns"]
    labeling_budget_cells = [round(n_cols * x) for x in labeling_budget]  # [158, 336, 672, 1008]

    sandbox_path = Path(cfg["shared"]["sandbox_path"]).resolve()
    dataset_name = sandbox_path.stem
    sandbox_path = str(sandbox_path)
    results_folder = str(Path(cfg["shared"]["results_path"]).resolve().joinpath(dataset_name).resolve())
    results_path = os.path.join(results_folder, f"exp_raha-non-enough-labels-RT")

    if not os.path.exists(results_path):
        os.makedirs(results_path)

    for exec_number in repetition:
        logging.info(f"exec_number: {exec_number}")
        run_experiments(sandbox_path, results_path, labeling_budget_cells, exec_number)


if __name__ == "__main__":
    start()
