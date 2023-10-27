import pickle
from pathlib import Path

import hydra
import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import numpy as np


def get_results_df(sandbox_path, results_path, algorithm, repition, labeling_budgets):
    datasets = []
    for dir in os.listdir(sandbox_path):
        datasets.append(dir)

    results_dict = {"algorithm": [], "dataset": [], "execution_number": [],
                        "precision": [], "recall": [], "f_score": [],
                        "tp": [], "ed_tpfp": [], "ed_tpfn": [], "execution_time": [],
                        "number_of_labeled_tuples": [], "number_of_labeled_cells": [], "detected_errors_keys": []}
    count = 0
    d = []

    result_files = [child for child in Path(results_path).resolve().iterdir()]

    for i in repition:
        for dataset in datasets:
            for label_budget in labeling_budgets:
                for child in result_files:
                    if algorithm in str(child) and dataset in str(child) and f"number#{i}_${label_budget}$labels" in str(child):
                        file_path = child
                    else:
                        continue
                    # file_path = results_path + '/{}_{}_number#{}_${}$labels.json' \
                        # .format(algorithm, dataset, str(i), str(label_budget))

                    file_path = str(Path(file_path).resolve())
                    if os.path.exists(file_path):
                        with open(file_path) as file:
                            json_content = json.load(file)
                            results_dict['algorithm'].append(algorithm)
                            results_dict['dataset'].append(dataset)
                            results_dict['execution_number'].append(i)
                            results_dict['precision'].append(json_content['precision'])
                            results_dict['recall'].append(json_content['recall'])
                            results_dict['f_score'].append(json_content['f_score'])
                            results_dict['tp'].append(json_content['tp'])
                            results_dict['ed_tpfp'].append(json_content['ed_tpfp'])
                            results_dict['ed_tpfn'].append(json_content['ed_tpfn'])
                            results_dict['execution_time'].append(json_content['execution-time'])
                            results_dict['number_of_labeled_tuples'].append(json_content['number_of_labeled_tuples'])
                            results_dict['number_of_labeled_cells'].append(json_content['number_of_labeled_cells'])
                            results_dict['detected_errors_keys'].append(json_content['detected_errors_keys'])
                    else:
                        print("The file does not exist: {}".format(file_path))

    result_df = pd.DataFrame.from_dict(results_dict)
    return result_df


def get_total_results(labeling_budgets, repition, result_df, n_cols):
    total_results = {"labeling_budget": [], "precision": [], "recall": [], "f_score": [], "ed_tpfp": [], "ed_tpfn": [],
                     "tp": []}
    for label_budget in labeling_budgets:
        avg_precision = 0
        avg_recall = 0
        avg_f_score = 0
        tp = 0
        ed_tpfp = 0
        ed_tpfn = 0

        for rep in repition:
            res_rep = result_df[result_df['execution_number'] == rep]
            res_rep_lab = res_rep[res_rep['number_of_labeled_tuples'] == label_budget]
            tp += res_rep_lab['tp'].sum()
            ed_tpfp += res_rep_lab['ed_tpfp'].sum()
            ed_tpfn += res_rep_lab['ed_tpfn'].sum()
            if res_rep_lab['ed_tpfp'].sum() == 0:
                precision = 0
                recall = 0
                f_score = 0
            else:
                precision = res_rep_lab['tp'].sum() / res_rep_lab['ed_tpfp'].sum()
                recall = res_rep_lab['tp'].sum() / res_rep_lab['ed_tpfn'].sum()
                f_score = 2 * precision * recall / (precision + recall)
            avg_precision += precision
            avg_recall += recall
            avg_f_score += f_score

        precision = avg_precision / len(repition)
        recall = avg_recall / len(repition)
        f_score = avg_f_score / len(repition)
        total_results['labeling_budget'].append(label_budget * n_cols)
        total_results['precision'].append(precision)
        total_results['recall'].append(recall)
        total_results['f_score'].append(f_score)
        total_results['tp'].append(tp / len(repition))
        total_results['ed_tpfp'].append(ed_tpfp / len(repition))
        total_results['ed_tpfn'].append(ed_tpfn / len(repition))
    total_results_df = pd.DataFrame.from_dict(total_results)
    return total_results_df


def get_raha_res(repitions, labeling_budgets, sandbox_path, results_path, df_path, n_cols):
    algorithm = 'raha'
    result_df = get_results_df(sandbox_path, results_path, algorithm, repitions, labeling_budgets)
    total_results = get_total_results(labeling_budgets, repitions, result_df, n_cols)
    total_results.to_csv(df_path, index=False)
    return total_results


@hydra.main(version_base=None, config_path="../eds_run_experiments/hydra_configs", config_name="results")
def main(cfg):
    repition = range(1, cfg["shared"]["repetitions"] + 1)
    n_cols = cfg["experiment"]["n_columns"]
    labeling_budgets = cfg["results"]["labeling_budget"]
    sandbox_path = str(Path(cfg["shared"]["sandbox_path"]).resolve())
    results_path = str(Path(cfg["results"]["path_to_experiment_results_folder"]).resolve()) # execution not experiment folder
    df_path = str(Path(cfg["results"]["path_to_benchmark_dataframe"]).resolve())

    total_results = get_raha_res(repition, labeling_budgets, sandbox_path, results_path, df_path, n_cols)


if __name__ == '__main__':
    main()
