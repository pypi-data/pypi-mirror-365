"""
Author: Charlotte Versavel
Date:   June 2022
Last Edit: Nov 2022

                             cluster_class.py

Purpose: a class to store the protein clusters and allow for access of a 
         specific cluster. 
         Also, allows 

"""
import json
import hashlib
import pandas as pd 
import numpy as np
from collections import defaultdict
import networkx as nx

from sklearn import cluster
from pyvis.network import Network as PyvizNetwork

class AllClusters:

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    * * * * * * * * * * * * * MEMBER VARIABLES * * * * * * * * * * * * * *  
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    # clusters = defaultdict(lambda: []) # a dict of relation {cluster_num : list_of_proteins_in_cluster}
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    * * * * * * * * * * * * * * INITIALIZERS * * * * * * * * * * * * * * *  
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    def __init__(self, csv_filename: str = "", csv_clusters_have_labels: bool = False, cluster_to_protein_dict: dict = {}) -> None:
        """  
        Parameters: csv_filename is the name of a csv file containing several 
                    clusters of proteins 
                        in the form [cluster_identifier]  Protein1    Protein2 ... (note that cluster_identifiers may not be present, and if not, they will be assigned in order of appearance)
                    protein_to_cluster_dict is a dictionary with the form { protein : cluster_identifier }
                    cluster_to_protein_dict is a dictionary with the form { cluster_identifier : [ protein_members, ... ] }
        Purpose:    to populate several single clusters with data from a CSV 
                    file, or from a dictionary
        Returns:    n/a
        """

        self.clusters = defaultdict(lambda: [])

        if csv_filename != "":
            try:
                with open(csv_filename, "r") as data:
                    
                    for i, line in enumerate(data):
                        list_of_proteins = line.strip().split(",")
                        cluster_id = None
                        if csv_clusters_have_labels:
                            cluster_id = list_of_proteins.pop(0)
                        else:
                            cluster_id = i
                       
                        self.clusters[cluster_id] = list_of_proteins

            except FileNotFoundError:
                print(f"ERROR! file: {csv_filename} not found.")
        
        elif cluster_to_protein_dict: # dictionary not empty
            for cluster in cluster_to_protein_dict.keys():
                for protein in cluster_to_protein_dict[cluster]:
                    self.add_protein_to_cluster(protein, int(cluster))
        
        else: # no filename or dictionary passed in
            print(f"ERROR! please specify a [csv_filename] or a [cluster_to_protein_dict] to initialize the clusters.")
            



    def __repr__(self): 
        """             
        Purpose:    Overloaded Print function - Prints a message indicating how to print clusters
        Returns:    a new message to print
        """
        return f"AllClusters has {len(self.clusters)} clusters (use the print_all method to see them)"

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    * * * * * * * * * * * * * * * SETTERS * * * * * * * * * * * * * * * * *  
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    def add_protein_to_cluster(self, protein:str, cluster_num) -> None:
        """             
        Parameters: 
            -   protein is the protein to add to a specified cluster
            -   cluster_num is the num of the cluster to add a protein to
        Purpose:    to add a protein to a cluster
        Returns:    n/a
        """
        self.clusters[cluster_num].append(protein)
        # print(f"appended cluster {cluster_num}: {self.clusters[cluster_num]}")

    def sort_dictionary(self) -> None:
        """             
        Purpose:    to sort the dictionary by number of proteins in each cluster
        Returns:    n/a
        """
        sorted_clusters = dict(sorted(self.clusters.items(), key=lambda x: len(x[1])))
        self.clusters = sorted_clusters
        # print(f"appended cluster {cluster_num}: {self.clusters[cluster_num]}")


    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    * * * * * * * * * * * * * * * GETTERS * * * * * * * * * * * * * * * * *  
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    def get_cluster_proteins(self, cluster_number) -> list:
        """             
        Parameters: cluster_number is the number of the cluster to get
        Purpose:    to get the list of proteins from a cluster
        Returns:    the list of proteins in the cluster
        """

        return self.clusters[cluster_number]

    def get_num_clusters(self) -> int:
        """
        Purpose:    to access the number of clusters
        Returns:    the number of clusters
        """
        return len(self.clusters)

    def get_all_cluster_labels(self) -> list():
        """
        Purpose:    to access all labels (cluster nums)
        Returns:    the labels of the clusters
        """
        return self.clusters.keys()

    def get_all_clusters(self) -> dict():
        """
        Purpose:    to access all of the clusters
        Returns:    all clusters in format {cluster_num: [list_of_proteins]}
        """
        return dict(self.clusters)


    def print_all(self) -> None:
        """             
        Purpose:    to print all the clusters in the dictionary
        Returns:    n/a
        """
        print(self.clusters.keys())
        
        for cluster_num in self.clusters.keys():
            print(f"Cluster {cluster_num}: {self.get_cluster_proteins(cluster_num)}")
    
    
    def filter_clusters_by_size(self, min_size, max_size):
        """             
        Purpose:    to retrieve a dictionary that only contains clusters within a certain size range
        Returns:    dictionary
        """
        filtered_dict = {key: value for key, value in self.clusters.items() if min_size <= len(value) <= max_size}
        return filtered_dict

class Cluster:
    def __init__(self,proteins):
        self.proteins = proteins

    def __len__(self):
        return len(self.proteins)

    def __repr__(self): # NOTE: 
        reprStr = "Cluster of {} [{},{},...] (hash {})".format(len(self), self.proteins[0], self.proteins[1], hash(self))
        if hasattr(self, 'G'):
            reprStr += "\nTriangles: {}\nMax Degree: {}".format(self.triangles(), max(self.G.degree(), key=lambda x: x[1])[1])
        if hasattr(self, 'GO_terms'):
            reprStr += "\nTop Terms:\n\t{}".format('\n\t'.join(
                    ['{} ({})'.format(i[0], i[1]) for i in self.get_top_terms(5)]
            ))
        return reprStr

    def __hash__(self):
        return int(hashlib.md5(''.join(self.proteins).encode()).hexdigest(), 16)
    
    def __iter_(self):
        return iter(self.proteins)

    def to_dict(self): # NOTE: 
        D = {}
        D['id'] = hash(self)
        D['proteins'] = []
        for p in self.proteins:
            pD = {}
            pD['name'] = p
            if hasattr(self, 'GO_DB'):
                pD['go'] = self.GO_DB[self.GO_DB['seq'] == p]['GO_ids'].values[0]
            D['proteins'].append(pD)
        if hasattr(self, 'GO_DB'):
            D['go'] = sorted([{"id": i.ID, "desc": i.name, "freq": self.GO_terms[i]} for i in self.GO_terms], key = lambda x: x['freq'], reverse=True)
        if hasattr(self,'G'):
            D['graph'] = list(self.G.edges())
        return D

    def to_json(self): # NOTE:
        return json.dumps(self.to_dict())

    def add_GO_terms(self, go_db, GO_OBJECTS):
        self.GO_terms = {}
        self.GO_DB = go_db
        for prot in self.proteins:
            goIds = go_db[go_db['seq'] == prot]['GO_ids'].values[0]
            if goIds is None or len(goIds) == 0:
                continue
            for gid in goIds:
                try:
                    goObj = GO_OBJECTS[gid]
                except KeyError:
                    GO_OBJECTS[gid] = GO(gid,{'id':gid,'name':gid})
                    goObj = GO_OBJECTS[gid]
                goCount = self.GO_terms.setdefault(gid,0)
                self.GO_terms[gid] = goCount + 1

    def get_proteins_by_GO(self, GO_id):
        return [p for p in self.proteins if GO_id in prot_go_db.loc[p,'GO_ids']]

    def get_GO_by_protein(self, protein):
        assert protein in self.proteins, "{} not in cluster".format(protein)
        return [gt for gt in coi.GO_terms if gt.ID in prot_go_db.loc[protein,'GO_ids']]

    def get_top_terms(self,N):
        if not hasattr(self, 'GO_terms'):
            raise NotImplementedError("GO Terms have not been added yet.")
        GOlist = list(self.GO_terms.keys())
        if N == -1:
            N = len(GOlist)
        sortedList = sorted(GOlist,key=lambda x: self.GO_terms[x],reverse=True)[:N]
        return list(zip(sortedList, [self.GO_terms[i] for i in sortedList]))

    def set_graph(self,G):
        self.G = G.subgraph(self.proteins)

    def triangles(self):
        return sum([i for i in nx.triangles(self.G).values()]) / 3

    def draw_degree_histogram(self,draw_graph=True):
        if not hasattr(self,'G'):
            raise ValueError('Run .set_graph() method on this cluster first')
        G = self.G
        degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
        degreeCount = collections.Counter(degree_sequence)
        deg, cnt = zip(*degreeCount.items())

        fig, ax = plt.subplots()
        plt.bar(deg, cnt, width=0.80, color='b')

        plt.title("Degree Histogram")
        plt.ylabel("Count")
        plt.xlabel("Degree")
        ax.set_xticks([d + 0.4 for d in deg])
        ax.set_xticklabels(deg)

        # draw graph in inset
        if draw_graph:
            plt.axes([0.4, 0.4, 0.5, 0.5])
            pos = nx.spring_layout(G, k=0.15,iterations=10)
            plt.axis('off')
            nx.draw_networkx_nodes(G, pos, node_size=20)
            nx.draw_networkx_edges(G, pos, alpha=0.4)
        plt.show()

    def draw_graph(self, buttons=False):
        if not hasattr(self,'G'):
            raise ValueError('Run .set_graph() method on this cluster first')
        net = NetworkViz(width="500px", height="500px", notebook=True)
        net.from_nx(self.G)
        if buttons: net.show_buttons()
        return net.show(f"{hash(self)}_graph.html")
        #nx.draw_kamada_kawai(G, with_labels=True,node_size=600, font_size=8)


    @staticmethod
    def readClusterObjects(infile,sep=','):
        if infile.endswith(".csv"):
            clusts = []
            with open(infile,'r') as f:
                for line in f:
                    clusts.append(Cluster(line.strip().split(sep)))
            return clusts
        else:
            with open(infile, 'r') as f:
                cluster_json = json.load(f)
            clusts = []
            for cluster_id in cluster_json.keys():
                proteins = cluster_json[cluster_id]['members']
                clusts.append(Cluster(proteins))
            return clusts

    @staticmethod
    def cluster_from_json(jsonString, GO_OBJECTS):
            clust = Cluster([])
            D = json.loads(jsonString)
            clust.proteins = [i['name'] for i in D['proteins']]
            clust.GO_terms = {}
            for goDict in D['go']:
                gid = goDict['id']
                gdesc = goDict['desc']
                try:
                    goObj = GO_OBJECTS[gid]
                except KeyError:
                    GO_OBJECTS[gid] = GO(gid,{'id':gid,'name':gdesc})
                    goObj = GO_OBJECTS[gid]
                clust.GO_terms[goObj] = goDict['freq']
            try:
                edgeList = D['graph']
                G = nx.Graph()
                for e in edgeList:
                    G.add_edge(*e)
                clust.G = G
            except KeyError:
                pass
            return clust

    @staticmethod
    def triangle_search(clusters, min_triangles=0, max_triangles=np.inf):
        return [c for c in clusters if c.triangles() >= min_triangles and c.triangles() <= max_triangles]

    @staticmethod
    def node_search(clusters, min_nodes=0, max_nodes=np.inf):
        return [c for c in clusters if len(c) >= min_nodes and len(c) <= max_nodes]


class NetworkViz(PyvizNetwork):
    """Extend PyVis class so that we can use a modified template that works in Colab. 
    """
 
    def __init__(self,
                 height="500px",
                 width="500px",
                 directed=False,
                 notebook=False,
                 bgcolor="#ffffff",
                 font_color=False,
                 layout=None,
                 heading=""):
        # call super class init
        PyvizNetwork.__init__(self, 
                              height, 
                              width,
                              directed,
                              notebook,
                              bgcolor,
                              font_color,
                              layout,
                              heading=heading)
        # override template location - update as per installation
        #self.path =  os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'templates/pyvis_inline.html'))


    # fun copied from pyvis to skip imports
    def check_html(self, name):
        """
        Given a name of graph to save or write, check if it is of valid syntax
        :param: name: the name to check
        :type name: str
        """
        assert len(name.split(".")) >= 2, "invalid file type for %s" % name
        assert name.split(
            ".")[-1] == "html", "%s is not a valid html file" % name

    # fun extended for colab
    def show(self, name):
        """
        Writes a static HTML file and saves it locally before opening.
        :param: name: the name of the html file to save as
        :type name: str
        """
        self.check_html(name)
        if self.template is not None:
            if not COLAB_ENV: 
                # write file and return IFrame
                return self.write_html(name, notebook=True)
            else:
                # write file and return HTML
                self.write_html(name, notebook=True)
                return IPython.display.HTML(data=name)
        else:
            self.write_html(name)
            webbrowser.open(name)

    

