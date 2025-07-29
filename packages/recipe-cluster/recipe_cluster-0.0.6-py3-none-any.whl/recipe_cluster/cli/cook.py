#!/usr/bin/env python3

# This script is used to add proteins to clusters to reconnect the clusters, based on the structure of the network.
# run with python recipe.py --network ../to-run-recipe-on/20240202_apall_hits_v_all_dscript_out.positive.tsv --cluster-filepath ../to-run-recipe-on/protein_to_cluster.json --lr .1 --max 100 -cthresh 0.75
# the result is a .json file with the added proteins for each cluster, for each metric and connectivity threshold
# the results are structured in a dict with the metric as the key, and within the metric, keys for each connectivity threshold, and within each connectivity threshold, keys for each cluster name. The corresponding values are the added proteins for each cluster.

import time
import json
import sys
import os
sys.path.append(os.getcwd())
import argparse
import logging

from math import sqrt
from math import floor
from math import ceil
from collections import defaultdict
from tqdm import tqdm

import numpy as np
import pandas as pd

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)


# importing the classes recipe uses
from ..core.matrix import ProteinMatrix # ppi matrix
from ..core.cluster import AllClusters # dictionary to hold all clusters (in form number of cluster : list of proteins in that cluster)
from ..core.degree import DegreeList # creates a list of all proteins in order of their degree
from ..core.matrix import SubMatrix

# helper functions for setting up program
from ..core.utils import initialize_matrix_clusters_degreelist

logging.basicConfig(
    level=logging.DEBUG,  # Set the minimum level of messages to capture
    format='%(asctime)s - %(levelname)s - %(message)s',  # Specify the format of the log messages
    handlers=[
        logging.StreamHandler()  # Log messages will be output to the console
    ]
)

def compute_qualifying_proteins(
    matrix,
    degreelist,
    clusters,
    metric = 'degree',
    sort_ascending = False,
    connectivity_threshold = 1,
    degree_cutoff = 5000,
    linear_ratio = None,
    max_added_proteins = None,
    addition_cap = None,
    lower_bound = 3,
    upper_bound = 8
):
    proteins = matrix.get_list_of_proteins()
    degree_dict = dict(degreelist.sorted_protein_degree_dict)
    matrix_df = matrix.get_matrix()
    all_proteins_to_add = {}

    filtered_clusters = clusters.filter_clusters_by_size(lower_bound, upper_bound)
    for cluster_num in tqdm(filtered_clusters.keys(),total=len(filtered_clusters)):
        # initialise list of proteins to add
        added_proteins = []
        protein_to_add = "initialise"
        # get all the proteins associated to a cluster
        cluster_proteins = clusters.get_cluster_proteins(cluster_num)
        # get the list of potential proteins to add to cluster
        potential_proteins = list(filter(lambda prot: prot not in cluster_proteins and degree_dict[prot] < degree_cutoff, proteins))
        # TODO: is there a better way of doing this??
        submatrix = SubMatrix(cluster_proteins, matrix)
        components_and_labels = submatrix.get_num_components_and_labels()
        num_components = components_and_labels[0]
        # current ratio of clusters to proteins
        num_proteins = len(cluster_proteins)
        percent_connectivity = 1 - (num_components - 1) / (num_proteins - 1)
        # loop through all the proteins and add proteins based on score
        while protein_to_add and percent_connectivity < connectivity_threshold:
            if addition_cap:
                if len(added_proteins) > addition_cap:
                    break
            qualifying_proteins = {}
            connection_sitch = None
            # get sqrt of number of components in the subgraph
            if linear_ratio:
                connection_sitch = floor(linear_ratio * len(np.unique(components_and_labels[1])))
            else:
                connection_sitch = floor(sqrt(len(np.unique(components_and_labels[1]))))
            min_connection = connection_sitch if connection_sitch > 1 else 2

            for protein in tqdm(potential_proteins,leave=False):
                a = protein not in matrix_df
                if a:
                    with open("mismatched_proteins.txt", 'a+') as f:
                        f.write(f"{protein}\n")
                else:
                    protein_degree = degree_dict[protein]
                    if protein_degree >= min_connection:
                        # create component dictionary
                        protein_component_dictionary = dict(zip(submatrix.get_matrix().index, components_and_labels[1]))
                        # swap the values so the component number is the key
                        component_dictionary = defaultdict(list)
                        for key, val in protein_component_dictionary.items():
                            component_dictionary[val].append(key)
                        # get number of connected components
                        num_components_protein_connects = 0
                        for component_number in range(num_components):
                            if next((prot for prot in component_dictionary[component_number] if prot in matrix_df and matrix_df[prot][protein]), None):
                                num_components_protein_connects = num_components_protein_connects + 1
                        # if connection, greater than cutoff, consider for re-addition
                        if num_components_protein_connects >= min_connection:
                            qualifying_proteins[protein] = {
                                'components_connected': num_components_protein_connects,
                                'degree': protein_degree,
                                'score': num_components_protein_connects * (1 / protein_degree)
                            }
            if max_added_proteins:
                sorted_qualifying_proteins = sorted(qualifying_proteins.items(), key = lambda x: x[1][metric], reverse=not sort_ascending)
                for _ in range(max_added_proteins):
                    if len(sorted_qualifying_proteins):
                        added_proteins.append(sorted_qualifying_proteins.pop()[0])
                    else:
                        break
                protein_to_add = None
                percent_connectivity = 1
            else:
                protein_to_add = sorted(qualifying_proteins.items(), key = lambda x: x[1][metric], reverse=sort_ascending)[0][0] if qualifying_proteins else None
                if protein_to_add:
                    potential_proteins.remove(protein_to_add)
                    added_proteins.append(protein_to_add)
                    # get number of components in original cluster
                    submatrix = SubMatrix(cluster_proteins + added_proteins, matrix)
                    components_and_labels = submatrix.get_num_components_and_labels()
                    num_components = components_and_labels[0]
                    percent_connectivity = 1 - (num_components - 1) / (num_proteins - 1)

        if len(added_proteins):
            all_proteins_to_add[cluster_num] = added_proteins
    return all_proteins_to_add

def cook(cluster_filepath,
              network_filepath,
              lb = 3,
              ub = 100,
              lr = None,
              cthresh = -1,
              metric = ["degree", "components_connected", "score"],
              max_proteins = None,
              addition_cap = 20,
              clusters_labeled = False):
    max_added_proteins = max_proteins # 3
    size = f"{lb}-{ub}"
    lr = lr

    print("initializing cluster matrix")
    matrix, clusters, degreelist = initialize_matrix_clusters_degreelist(network_filepath, cluster_filepath, csv_clusters_have_labels=clusters_labeled)
    qualifying_proteins_by_metric = {} # Dict of structure: {metric: {connectivity_threshold: {cluster_id: [qualifying_proteins]}}}

    connectivity_thresholds = []
    if cthresh == -1.0:
        connectivity_thresholds = [0.1, 0.25, 0.5, 0.75, 1.0]
    else:
        connectivity_thresholds = [cthresh]
    print("connectivity_thresholds", connectivity_thresholds, time.ctime())

    metrics_base = {'degree': False, 'components_connected': True, 'score': True}
    metrics = {k: metrics_base[k] for k in metric}
    for metric in metrics.items():
        # skip all metrics not specified

        print("starting metric:", metric[0])
        qualifying_proteins_at_threshold = {}

        for connectivity_threshold in connectivity_thresholds:
            print("   -starting threshold", connectivity_threshold, time.ctime())
            adjusted_lb = lb if lb == 3 else lb + 1
            qualifying_proteins = compute_qualifying_proteins(
                matrix,
                degreelist,
                clusters,
                metric = metric[0],
                sort_ascending = metric[1],
                connectivity_threshold = connectivity_threshold,
                degree_cutoff = 5000,
                linear_ratio = lr,
                max_added_proteins = max_added_proteins,
                addition_cap = addition_cap,
                lower_bound=adjusted_lb,
                upper_bound=ub
            )

            if qualifying_proteins:
                qualifying_proteins_at_threshold[connectivity_threshold] = qualifying_proteins
                avg_proteins_added = sum([len(proteins) for proteins in qualifying_proteins.values()]) / len(qualifying_proteins)

                # NOTMETRIC = f"lr: {lr}" if lr else "sqrt" # TODO figure out how to do LR and SQRT Qualifiers
                print(f"at threshold {connectivity_threshold}, and {metric}, {len(qualifying_proteins)} clusters have an average of {avg_proteins_added} proteins added")
        if qualifying_proteins_at_threshold:
            qualifying_proteins_by_metric[metric[0]] = qualifying_proteins_at_threshold

    return qualifying_proteins_by_metric

def main(args=None):
    if args is None:
        args = get_args().parse_args()

    with open(args.cluster_filepath, "r") as f:
        cluster_dict = json.load(f)
    for clkey in cluster_dict.keys():
        cluster_dict[clkey]["recipe"] = {}

    if not isinstance(args.metric, list):
        args.metric = [args.metric]

    recipe_results = cook(args.cluster_filepath, args.network_filepath, args.lb, args.ub, args.lr, args.connectivity_threshold, args.metric, args.max_proteins, args.protein_cap, args.clusters_labeled)

    for clkey in tqdm(cluster_dict.keys(),total=len(cluster_dict)):
        for m, metric_results in recipe_results.items():
            cluster_dict[clkey]["recipe"][m] = {}
            for ct, ct_results in metric_results.items():
                if int(clkey) in ct_results:
                    cluster_dict[clkey]["recipe"][m][ct] = ct_results[int(clkey)]
                else:
                    cluster_dict[clkey]["recipe"][m][ct] = {}

    with open(args.outfile, "w+") as f:
        json.dump(cluster_dict, f, indent=4)

def get_args(parser=None):
    """
    """
    if parser is None:
        parser = argparse.ArgumentParser()
    # TODO: Charlotte: add a default value for the network filepath
    # TODO: Charlotte: add an option for structure of the network filepath
    # TODO: Charlotte: add a default value for the cluster filepath
    # Location Arguments: (where data is, and where to save it)
    parser.add_argument(
        "-cfp", "--cluster-filepath",
        required=True,
        help = "Cluster filepath",
        type = str
    )
    parser.add_argument (
        "-cfl", "--clusters-labeled",
        required=False,
        help = "If a CSV file of clusters is passed, clusters have labels. Default: False",
        type = bool,
        default = False
    )
    parser.add_argument(
        "-nfp", "--network-filepath",
        help = "Network filepath",
        required=True,
        type = str
    )
    parser.add_argument("--outfile", help = "Output file to save results", type = str, required=True)

    # Arguments for output file options
    '''
    parser.add_argument (
        "--modify-clusters",
        help = "Format of the output file. default is false, meaning the dict (which maps added proteins to clusters, and retains all param options) is printed. if set to true, the modified clusters are printed. Default: False",
        type = bool,
        required = False,
        default = False
    )
    '''
    # parser.add_argument (
    #     "--new-clusters-outfile",
    #     required=False,
    #     help = "name for the output file of clusters with qualifying proteins added",
    #     type = str,
    #     default = "updated_clusters.csv"
    # )

    # Arguments for which clusters to run ReCIPE on
    # Based on number of proteins in cluster
    parser.add_argument(
        "--lb",
        required=False,
        help = "Lower bound (inclusive) for cluster size. Default: 3",
        type = int,
        default = 3,
    )
    parser.add_argument(
        "--ub",
        required=False,
        help = "Upper bound (exclusive) for cluster size. Default: 100",
        type = int,
        default=100,
    )
    # Arguments for ReCIPE
    parser.add_argument(
        "--lr",
        required=False,
        help = "Linear ratio (if not using sqrt). Default = None",
        type = float,
        default = None,

    )
    parser.add_argument(
            "--connectivity-threshold", "-cthresh",
        required=False,
        help = 'Connectivity threshold to add proteins until. Default = -1.0 (yields connectivity thresholds [0.1, 0.25, 0.5, 0.75, 1.0]) (if only a single option is desired, 0.75 is recommended)',
        default = -1.0,
        type=float
    )
    parser.add_argument(
        "--metric", "-wm",
        required=False,
        help = "Which metric to use to rank proteins to be added back. Default: degree. Options: degree, components_connected, score",
        type = str,
        choices=['degree', 'components_connected', 'score'],
        default = "degree"
    )

    parser.add_argument(
        "--max_proteins",
        required=False,
        help = "Maximises number of proteins to added to a cluster. Default = None",
        type=int,
        default = None
    )

    parser.add_argument(
        "--protein_cap",
        required=False,
        help = "Adds at most the number of proteins defined by parameter. Default = 20",
        type=int,
        default = 20
    )
    # parser.add_argument("--ic", help = "Spectral parameter", type = int)
    return parser

if __name__ == "__main__":
    parser = get_args()
    main(parser.parse_args())
