### Steps for running ReCIPE

##### Install ReCIPE

`pip install recipe-cluster`

##### Download Gene Ontology Data Base

[Download gene ontology](https://geneontology.org/docs/download-ontology/)

#### Generate DSD file

[fastDSD](https://github.com/samsledje/fastDSD) is recommended. It can be used simply by running command:

`fastDSD -c --converge -t 0.5 --outfile dscript_distances network-filepath.csv`

#### Generate Cluster File (if necessary)

ReCIPE accepts both CSV and JSON formats for cluster files.

- **CSV format**: Each line in the CSV represents a cluster of proteins, with each cluster containing a comma-separated list of protein identifiers.
  
- **JSON format**: Each key represents a unique cluster ID. The value associated with each key is an object containing a `members` array, which lists the protein identifiers for that cluster.
  

#### Run ReCIPE

##### Reconnect Clusters

This method analyses cluster, network and DSD files to determine the which proteins qualify to be introduced to clusters in order to create overlapping clusters.

```
usage: recipe-cluster cook [-h] -cfp CLUSTER_FILEPATH [-cfl CLUSTERS_LABELED] -nfp NETWORK_FILEPATH --outfile OUTFILE [--lb LB] [--ub UB] [--lr LR]
                           [--connectivity-threshold CONNECTIVITY_THRESHOLD] [--metric {degree,components_connected,score}] [--max_proteins MAX_PROTEINS] [--protein_cap PROTEIN_CAP]

options:
  -h, --help            show this help message and exit
  -cfp, --cluster-filepath CLUSTER_FILEPATH
                        Cluster filepath
  -cfl, --clusters-labeled CLUSTERS_LABELED
                        If a CSV file of clusters is passed, clusters have labels. Default: False
  -nfp, --network-filepath NETWORK_FILEPATH
                        Network filepath
  --outfile OUTFILE     Output file to save results
  --lb LB               Lower bound (inclusive) for cluster size. Default: 3
  --ub UB               Upper bound (exclusive) for cluster size. Default: 100
  --lr LR               Linear ratio (if not using sqrt). Default = None
  --connectivity-threshold, -cthresh CONNECTIVITY_THRESHOLD
                        Connectivity threshold to add proteins until. Default = -1.0 (yields connectivity thresholds [0.1, 0.25, 0.5, 0.75, 1.0]) (if only a single option is desired, 0.75
                        is recommended)
  --metric, -wm {degree,components_connected,score}
                        Which metric to use to rank proteins to be added back. Default: degree. Options: degree, components_connected, score
  --max_proteins MAX_PROTEINS
                        Maximises number of proteins to added to a cluster. Default = None
  --protein_cap PROTEIN_CAP
                        Adds at most the number of proteins defined by parameter. Default = 20
```

In addition to command line access, the `cook` method can be accessed programmatically with the same arguments as follows:
```
import recipe-cluster as recipe

recipe.cook(...)
```