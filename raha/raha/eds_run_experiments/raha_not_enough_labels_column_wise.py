import copy
import logging
import os
import pickle
from pathlib import Path
from random import shuffle
import random

import hydra
import pandas as pd
from raha.detection import main


def run_raha(dataset_path, results_path, labeling_budget, exec_number, column_wise_evaluation, column_idx):
    main(results_path, dataset_path, os.path.basename(dataset_path),
         labeling_budget, exec_number, column_wise_evaluation, column_idx)


def distribute_labels(labeling_budget_cells, label_per_col, sandbox_path):
    datasets_cols = []
    for dataset in os.listdir(sandbox_path):
        if os.path.exists(os.path.join(sandbox_path, dataset, "dirty.csv")):
            df = pd.read_csv(os.path.join(sandbox_path, dataset, "dirty.csv"), sep=",", header="infer",
                             encoding="utf-8", dtype=str,
                             low_memory=False)
            for col_idx, col in enumerate(list(df.columns)):
                datasets_cols.append((dataset, col_idx, col, len(df[col])))
    datasets_budget = dict()
    assigned_labels = 0
    datasets_cols_duplicate = copy.deepcopy(datasets_cols)
    while assigned_labels + label_per_col < labeling_budget_cells:
        if len(datasets_cols) == 0:
            for col in datasets_cols_duplicate:
                datasets_cols.append(col)
        while True:
            selected_col = random.choice(datasets_cols)
            if selected_col[3] > label_per_col:
                break
        if selected_col in datasets_budget:
            datasets_budget[selected_col] += label_per_col
        else:
            datasets_budget[selected_col] = label_per_col
        datasets_cols.remove(selected_col)
        assigned_labels += label_per_col
    return datasets_budget


def run_experiments(sandbox_path, results_path, labeling_budget_cells, exec_number, labels_per_col):
    for label_budget in labeling_budget_cells:
        logging.info(f"label_budget: {label_budget}")
        datasets_budget = distribute_labels(label_budget, labels_per_col, sandbox_path)
        for dataset in datasets_budget:
            logging.info(f"dataset - col: {dataset}")
            try:
                if datasets_budget[dataset] > 0:
                    results_path_raha = os.path.join(results_path,
                                                     "results_" + str(label_budget) + "_" + str(exec_number))
                    if not os.path.exists(results_path_raha):
                        os.makedirs(results_path_raha)
                    dataset_path = os.path.join(sandbox_path, dataset[0])
                    run_raha(dataset_path, results_path_raha, datasets_budget[dataset], exec_number,
                             column_wise_evaluation=True, column_idx=dataset[1])
                else:
                    logging.info(f"dataset {dataset} has no labeling budget")
            except Exception as e:
                print(dataset, e)


@hydra.main(version_base=None, config_path="hydra_configs", config_name="column_wise")
def start(cfg):
    logging.basicConfig(filename=str(Path(cfg["logs"]["path_to_log_file"]).resolve()),
                        level=logging.DEBUG)

    repetitions = range(1, cfg["shared"]["repetitions"] + 1)
    labeling_budget = cfg["experiment"]["labeling_budgets"]
    n_cols = cfg["experiment"]["n_columns"]
    labeling_budget_cells = [round(n_cols * x) for x in labeling_budget]
    labels_per_col_list = cfg["experiment"]["labels_per_column"]

    sandbox_path = Path(cfg["shared"]["sandbox_path"]).resolve()
    dataset_name = sandbox_path.stem
    sandbox_path = str(sandbox_path)

    results_folder = str(Path(cfg["shared"]["results_path"]).resolve().joinpath(dataset_name).resolve())

    for exec_number in repetitions:
        for labels_per_col in labels_per_col_list:
            exp_name = f"raha-non-enough-labels-{labels_per_col}-per-col"
            results_path = os.path.join(results_folder, f"exp_{exp_name}")
            if not os.path.exists(results_path):
                os.makedirs(results_path)
            logging.info(f"exec_number: {exec_number}")
            run_experiments(sandbox_path, results_path, labeling_budget_cells, exec_number, labels_per_col)


if __name__ == "__main__":
    start()
