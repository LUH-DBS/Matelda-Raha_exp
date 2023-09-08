import pickle
import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import numpy as np

def get_results_df(sandbox_path, results_path, algorithm, repition, labeling_budgets):
    datasets = []
    for dir in os.listdir(sandbox_path):
        datasets.append(dir)

        results_dict = {"algorithm":[], "dataset":[], "execution_number":[], 
                    "precision": [], "recall": [], "f_score": [],
                        "tp": [], "ed_tpfp": [], "ed_tpfn": [], "execution_time": [],
                        "number_of_labeled_tuples": [], "number_of_labeled_cells": [], "detected_errors_keys":[]}
        count = 0 
        d = []
        for i in repition:
            for dataset in datasets:
                for label_budget in labeling_budgets:
                    file_path = results_path + '/{}_{}_number#{}_${}$labels.json'\
                                .format(algorithm, dataset, str(i), str(label_budget))
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
    total_results = {"labeling_budget":[], "precision": [], "recall": [], "f_score": [], "ed_tpfp": [], "ed_tpfn": [], "tp": []}
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
            tp = res_rep_lab['tp'].sum()
            ed_tpfp = res_rep_lab['ed_tpfp'].sum()
            ed_tpfn = res_rep_lab['ed_tpfn'].sum()
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
        total_results['tp'].append(tp)
        total_results['ed_tpfp'].append(ed_tpfp)
        total_results['ed_tpfn'].append(ed_tpfn)
    total_results_df = pd.DataFrame.from_dict(total_results)
    return total_results_df

def get_eds_res(path, exp_name, labeling_budgets):
    
    res_dict = {"labeling_budget": [], "precision": [], "recall": [], "fscore": []}
    for label_budget in labeling_budgets:
        path_ = os.path.join(path, "{}_{}_labels/results".format(exp_name, label_budget))
        with open(os.path.join(path_, "scores_all.pickle"), "rb") as f:
            scores_all = pickle.load(f)
            res_dict["labeling_budget"].append(label_budget)
            res_dict["precision"].append(scores_all["total_precision"])
            res_dict["recall"].append(scores_all["total_recall"])
            res_dict["fscore"].append(scores_all["total_fscore"])
    res_df_eds = pd.DataFrame(res_dict)
    return res_df_eds

def get_raha_res(repitions, labeling_budgets, sandbox_path, results_path, df_path, n_cols):
    algorithm = 'raha'
    result_df = get_results_df(sandbox_path, results_path, algorithm, repitions, labeling_budgets)
    total_results = get_total_results(labeling_budgets, repitions, result_df, n_cols)
    total_results.to_csv(df_path, index=False)
    return total_results

def plot(total_results, res_df_eds, plot_path, dataset_name):

    # Extracting the required columns from the first DataFrame
    labeling_budget1 = total_results['labeling_budget']
    f_score1 = total_results['f_score']

    # Extracting the required columns from the second DataFrame
    labeling_budget2 = res_df_eds['labeling_budget']
    f_score2 = res_df_eds['fscore']

    # Creating the line plot
    plt.figure(figsize=(20, 5))  # Adjust the width and height as desired

    # Plotting the first method's data
    plt.plot(labeling_budget1, f_score1, marker='o', color='blue', label='Raha')

    # Plotting the second method's data
    plt.plot(labeling_budget2, f_score2, marker='o', color='green', label='EDS')

    # Setting the axis labels and title
    plt.xlabel('Labeling Budget')
    plt.ylabel('F-Score')
    plt.title('F-Score based on Labeling Budget on {}'.format(dataset_name))

    # Setting the X-axis tick locations and labels
    # x_ticks = np.arange(66, 1387, 66) # Assuming labeling_budget range is 1 to 20
    # plt.xticks(x_ticks)

    x_ticks = np.concatenate([labeling_budget1, labeling_budget2])
    x_labels = [str(lb) for lb in x_ticks]
    plt.xticks(x_ticks, x_labels)

    plt.ylim(0, 1)

    # Displaying the legend
    plt.legend()

    plt.tight_layout()

    plt.savefig(os.path.join(plot_path, "{}.png".format(dataset_name)), bbox_inches='tight')
    return 

repition = range(1, 6)
n_cols = 768
labeling_budgets = [1, 2, 3, 5, 10, 15, 20]
sandbox_path = "/home/fatemeh/VLDB-Aug/EDS-Raha_exp/Raha/raha/datasets/data-dgov/output_lake_high_percent_processed"
results_path = "/home/fatemeh/VLDB-Aug/results/raha-dgov/exp_raha-enough-labels_dgov"
df_path = "/home/fatemeh/VLDB-Aug/EDS-Raha_exp/Raha/benchmark-results/raha-dgov-e.csv"

total_results = get_raha_res(repition, labeling_budgets, sandbox_path, results_path, df_path, n_cols)

# labeling_budgets = [500, 1000, 2015, 4030, 6045, 8060, 10075, 12090, 14105, 16120]
# exp_name = "_dgov-old"
# path = "/home/fatemeh/ED-Scale/marshmallow_pipeline/output/kaggle-dataset/dgov-old-min-2/"
# res_df_eds = get_eds_res(path, exp_name, labeling_budgets)

# plot_path = "/home/fatemeh/EDS-BaseLines/Raha/pictures/KMeans"
# dataset_name = "dgov-old"
# plot(total_results, res_df_eds, plot_path, dataset_name)