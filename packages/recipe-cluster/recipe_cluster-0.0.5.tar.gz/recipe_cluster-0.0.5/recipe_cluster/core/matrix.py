"""
Author: Charlotte Versavel
Date:   June 2022
Last Edited: Oct 2022

                             matrix_class.py

Purpose: a class to represent a matrix of protein interactions
TODO: figure out how to use (oct 2022)

"""

import time

import pandas as pd 
import numpy as np

from scipy.sparse import csr_matrix # used in submatrix class
from scipy.sparse.csgraph import connected_components # used in submatrix class

class ProteinMatrix:
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    * * * * * * * * * * * * * * INITIALIZERS * * * * * * * * * * * * * * *  
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    def __init__(self, csv_filename: str, **kwargs):
        """             
        Purpose:    to populate a matrix with data from a CSV file
        Returns:    n/a
        """

        """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        * * * * * * * * * * * * * MEMBER VARIABLES * * * * * * * * * * * * * *  
        """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

        protein_data_df = pd.DataFrame
        list_of_all_proteins_in_matrix = np.array
        protein_matrix = pd.DataFrame(dtype=float)

        """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    
        try:
            # read csv file into a dataframe
            self.protein_data_df = pd.read_csv(csv_filename, delimiter = r'\s+', 
                names = ["gene_1", "gene_2", "edge_weight"]) 

            # store names of all proteins
            self.list_of_all_proteins_in_matrix = np.unique(np.append(self.protein_data_df["gene_1"], self.protein_data_df["gene_2"]))

            # Initialize the interaction matrix
            self._init_matrix()
        
        except FileNotFoundError:
            print(f"ERROR! file: {csv_filename} not found. ProteinMatrix could not be initialized")


    def __repr__(self): 
        """             
        Purpose:    to override the print function for this class so only a 
                    portion of the matrix is shown
        Returns:    a portion of the matrix to be printed
        """
        return self.protein_matrix.to_string(max_cols=20, max_rows=20)


    def _init_matrix(self):
        """             
        Purpose:    a helper function to populate the matrix with interactions
                    from a csv file
        Returns:    n/a
        """

        self.protein_matrix = pd.DataFrame(0.0, 
                                           index=self.list_of_all_proteins_in_matrix, 
                                           columns=self.list_of_all_proteins_in_matrix)
        protein_pairs = self.protein_data_df[['gene_1', 'gene_2']].values
        interactions = self.protein_data_df['edge_weight'].values

        # gen row/colum indexing
        row_idx = np.array([self.protein_matrix.index.get_loc(protein1) for protein1 in protein_pairs[:, 0]])
        col_idx = np.array([self.protein_matrix.columns.get_loc(protein2) for protein2 in protein_pairs[:, 1]])

        # create symmetric matrix
        self.protein_matrix.values[row_idx, col_idx] = interactions
        self.protein_matrix.values[col_idx, row_idx] = interactions


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    * * * * * * * * * * * * * * * GETTERS * * * * * * * * * * * * * * * * *  
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def get_matrix(self) -> pd.DataFrame:
        """             
        Purpose:    allows for access to a 2D matrix of protein interactions
        Returns:    a dataframe of protein interactions
        """
        return self.protein_matrix
    
    def get_list_of_proteins(self) -> list:
        """             
        Purpose:    to access the list of all proteins in the matrix
        Returns:    an array of all proteins in the matrix
        """
        
        return self.list_of_all_proteins_in_matrix
    

    def get_list_of_proteins_connected_to_protein(self, protein1: str) -> list:
        """
        Parameters: protein1 is a protein of interest
        Purpose:    to create a list of proteins connected to the given protein
        """
        connections = list()
        for protein2 in self.get_list_of_proteins():

            if self.protein_matrix[protein1][protein2]:
                connections.append(protein2)
        return connections


    def get_interaction(self, protein1: str, protein2: str):
        """             
        Purpose:    to access the interaction values stored in the matrix
        Returns:    the value at the specified proteins
        """
        return self.protein_matrix.loc[protein1, protein2]

    def has_edge(self, protein1: str, protein2: str) -> bool:
        """       
        Parameters: protein1, protein2 are the names of the proteins 
        Purpose:    to determine if there is an edge between two proteins
        Returns:    true if there is an edge, false if there is not
        """
        try:
            if (self.protein_matrix.loc[protein1, protein2] != 0):
            # if (self.protein_matrix.loc[protein1, protein2] == 0):
                return True
        except KeyError:
            return False
        return False

    def find_degree(self, protein: str) -> int:
        """             
        Parameters: protein the name of a protein
        Purpose:    to find the degree of a protein
        Returns:    the degree of the protein
        """
        count = 0
        try:
            for elem in self.protein_matrix.loc[protein]:
                if elem != 0:
                    count += 1
            
            return count
            
        except KeyError:
            return 0
        




# TODO: descriptions of the two classes and their functions
# TODO: test the getters for submatrix
class SubMatrix:

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    * * * * * * * * * * * * * MEMBER VARIABLES * * * * * * * * * * * * * *  
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    list_of_all_proteins_in_matrix = np.array
    protein_matrix = pd.DataFrame
    csr_matrix : csr_matrix


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    * * * * * * * * * * * * * * INITIALIZERS * * * * * * * * * * * * * * *  
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def __init__(self, proteins_to_map : list, original_matrix : ProteinMatrix):
        """            
        Parameters: 
            -   proteins_to_map: a subset of proteins in the original matrix 
            -   original matrix: large matrix contaniing the interactions for 
                all proteins
        Purpose:    to populate the submatrix with data from the original 
                    matrix. 
        Returns:    n/a
        """
        # print(f"initializing submatrix from {proteins_to_map}. the unique proteins are: {list(set(proteins_to_map))}")
        # initialize list of proteins:
        self.list_of_all_proteins_in_matrix = list(set(proteins_to_map))
        
        # inititalize matrix:
        self._init_matrix(original_matrix)
        self._init_csr_matrix_()
    

    def _init_matrix(self, original_matrix: ProteinMatrix):
        """             
        Purpose: Populate a new matrix with interactions from the original matrix in a vectorized manner.
        Returns: n/a
        """
        proteins = self.list_of_all_proteins_in_matrix

        # Initialize an empty matrix with zeros
        self.protein_matrix = pd.DataFrame(0.0, index=proteins, columns=proteins)

        # Extract relevant interaction data from the original matrix
        protein_data = original_matrix.protein_data_df  # DataFrame with ['gene_1', 'gene_2', 'edge_weight']

        # Use get_indexer for fast lookup of indices
        row_idx = self.protein_matrix.index.get_indexer(protein_data["gene_1"])
        col_idx = self.protein_matrix.columns.get_indexer(protein_data["gene_2"])

        # Mask to filter valid indices (proteins that exist in our submatrix)
        valid_mask = (row_idx != -1) & (col_idx != -1)

        row_idx, col_idx, interactions = (
            row_idx[valid_mask], 
            col_idx[valid_mask], 
            protein_data["edge_weight"].values[valid_mask]
        )

        # Convert DataFrame to NumPy array for fast assignment
        matrix_values = self.protein_matrix.values

        # Assign interactions to matrix (vectorized)
        matrix_values[row_idx, col_idx] = interactions
        matrix_values[col_idx, row_idx] = interactions  # Symmetric assignment
        
        
    def _init_csr_matrix_(self):
        """             
        Purpose:    initializes a csr matrix to use for determining 
                    connectedness within a cluster
        Returns:    n/a
        """
        self.csr_matrix = csr_matrix(self.protein_matrix.astype(pd.SparseDtype(dtype=float, fill_value=0)))
        # print(self.csr_matrix)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    * * * * * * * * * * * * * * * GETTERS * * * * * * * * * * * * * * * * *  
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def get_matrix(self) -> pd.DataFrame:
        """             
        Purpose:    allows for access to a 2D matrix of protein interactions
        Returns:    a dataframe of protein interactions
        """
        return self.protein_matrix
    
    def get_list_of_proteins(self) -> list:
        """             
        Purpose:    allows for access to the list of proteins in the matrix
        Returns:    a list of proteins
        """
        return self.list_of_all_proteins_in_matrix
    

    def get_list_of_proteins_connected_to_protein(self, protein1: str) -> list:
        """
        Parameters: protein1 is a protein of interest
        Purpose:    to create a list of proteins connected to the given protein
        """
        connections = list()
        for protein2 in self.get_list_of_proteins():

            if self.protein_matrix[protein1][protein2]:
                connections.append(protein2)
        
        return connections



    def get_interaction(self, protein1: str, protein2: str):
        """             
        Purpose:    to access the interaction values stored in the matrix
        Returns:    the value at the specified indexes
        """
        return self.protein_matrix.loc[protein1, protein2]


    def get_num_components_and_labels(self):
        """
        TODO
        """
        n_components, labels = connected_components(self.csr_matrix, directed=False, return_labels=True)

        # n_components = connected_components(self.csr_matrix, directed=False, return_labels=False)

        return n_components, labels
    # def find_degree(self, protein: str) -> int:
    #     """             
    #     Parameters: protein the name of a protein
    #     Purpose:    to find the degree of a protein
    #     Returns:    the degree of the protein
    #     """
    #     count = 0
    #     for elem in self.protein_matrix.loc[protein]:
    #         if elem != 0:
    #             count += 1
        
    #     return count

    







# a : int | str = "hello"

# class Foo:
#     def __init__(self, a : int | None = None, b : str | None = None, c : list[str] | None = None) -> None:
#         pass

# f = Foo(b="hello")

# def bar(b, *args, a=3, **kwargs):
#     kwargs["whatever"]
#     ...

# bar(1, 2,3,4, a=18, whatever=3)


