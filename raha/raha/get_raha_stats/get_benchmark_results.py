import html
import pickle
from pathlib import Path
import re

import hydra
import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import numpy as np

def value_normalizer(value):
    """
    This method takes a value and minimally normalizes it.
    """
    if isinstance(value, str):
        value = html.unescape(value)
        value = re.sub("[\t\n ]+", " ", value, re.UNICODE)
        value = value.strip("\t\n ")
    return value

def get_eds_n_errors(base_path, dirty_file_name, clean_file_name):
    total_n_errors = 0
    tables = os.listdir(base_path)
    for table in tables:
        dirty_df = pd.read_csv(os.path.join(base_path, table, dirty_file_name), keep_default_na=False, dtype=str).applymap(value_normalizer)
        clean_df = pd.read_csv(os.path.join(base_path, table, clean_file_name), keep_default_na=False, dtype=str).applymap(value_normalizer)
        if dirty_df.shape != clean_df.shape:
            print("Shape mismatch")
        dirty_df.columns = clean_df.columns
        diff = dirty_df.compare(clean_df, keep_shape=True)
        self_diff = diff.xs('self', axis=1, level=1)
        other_diff = diff.xs('other', axis=1, level=1)
        # Custom comparison. True (or 1) only when values are different and not both NaN.
        label_df = ((self_diff != other_diff) & ~(self_diff.isna() & other_diff.isna())).astype(int)
        total_n_errors += label_df.sum().sum()
    return total_n_errors

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
    total_results = {"labeling_budget": [], "precision": [], "recall": [], "f_score": [],  "f_score_std": [], "ed_tpfp": [], "ed_tpfn": [],
                     "tp": []}
    for label_budget in labeling_budgets:
        avg_precision = 0
        avg_recall = 0
        avg_f_score = 0
        tp = 0
        ed_tpfp = 0
        ed_tpfn = 0
        f_scores = []
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
            f_scores.append(f_score)

        precision = avg_precision / len(repition)
        recall = avg_recall / len(repition)
        f_score = avg_f_score / len(repition)
        total_results['labeling_budget'].append(label_budget * n_cols)
        total_results['precision'].append(precision)
        total_results['recall'].append(recall)
        total_results['f_score'].append(f_score)
        total_results['f_score_std'].append(np.std(f_scores)) 
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

def get_raha_res_not_standard(labeling_budget, executions, res_path, tp_fn, n_cols, df_path):
    results = {"labeling_budget": [], "precision": [], "recall": [], "f_score": [], "f_score_std": []}
    labeling_budget_cells = [round(n_cols*x) for x in labeling_budget]
    for l in labeling_budget_cells:
        total_precision = 0
        total_recall = 0
        total_f_score = 0
        f_scores = []
        for exec in executions:
            tp = 0
            tp_fp = 0
            results_path_raha = os.path.join(res_path, "results_" + str(l) + "_"  + str(exec))
            for file in os.listdir(results_path_raha):
                if file.endswith(".json"):
                    with open(os.path.join(results_path_raha, file)) as f:
                        json_content = json.load(f)
                        tp += json_content['tp']
                        tp_fp += json_content['ed_tpfp']
            precision = tp / tp_fp if tp_fp > 0 else 0
            recall = tp / tp_fn if tp_fn > 0 else 0
            f_score = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
            f_scores.append(f_score)
            total_precision += precision
            total_recall += recall
            total_f_score += f_score
        avg_precision = total_precision / len(executions)
        avg_recall = total_recall / len(executions)
        avg_f_score = total_f_score / len(executions)
        results["labeling_budget"].append(l)
        results["precision"].append(avg_precision)
        results["recall"].append(avg_recall)
        results["f_score"].append(avg_f_score)
        results["f_score_std"].append(pd.Series(f_scores).std())
        results_df = pd.DataFrame.from_dict(results)
        results_df.to_csv(df_path, index=False)
    return results_df

@hydra.main(version_base=None, config_path="../eds_run_experiments/hydra_configs", config_name="results")
def main(cfg):
    repition = range(1, cfg["shared"]["repetitions"] + 1)
    n_cols = cfg["results"]["n_columns"]
    variant = cfg["results"]["variant"]
    labeling_budgets = cfg["results"]["labeling_budget"]
    sandbox_path = str(Path(cfg["shared"]["sandbox_path"]).resolve())
    dirty_file_name = cfg["shared"]["dirty_file_name"]
    clean_file_name = cfg["shared"]["clean_file_name"]
    results_path = str(Path(cfg["results"]["path_to_experiment_results_folder"]).resolve()) # execution not experiment folder
    df_path = str(Path(cfg["results"]["path_to_benchmark_dataframe"]).resolve())
    if variant == "standard":
        total_results = get_raha_res(repition, labeling_budgets, sandbox_path, results_path, df_path, n_cols)
    else:
        print("variant is not standard")
        tp_fn = get_eds_n_errors(sandbox_path, dirty_file_name, clean_file_name)
        total_results = get_raha_res_not_standard(labeling_budgets, repition, results_path, tp_fn, n_cols, df_path)

if __name__ == '__main__':
    main()
