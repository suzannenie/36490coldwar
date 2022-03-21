import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from heapq import nlargest

import graph as g


def get_num_nodes(G):
	return G.number_of_nodes()

def get_num_edges(G):
	return G.number_of_edges()

def get_degree_distribution(G):
	"""
	Parameters
	-----------------
	G : networkx graph

	Returns
	----------------
	degree_sequence : tuple
		tuple of form (degree, name), sorted in ascending order of degree.
		Name is included for investigating high outliers of the exponential
		distribution (Dulles, Wisner, etc.)
	"""
	degree_sequence = sorted(((d, n) for n, d in G.degree()))
	return degree_sequence

def get_centralities(G):
	"""
	Parameters
	-----------------
	G : networkx graph

	Returns
	----------------
	centralities : tuple
		tuple returning (degree_centrality, betweenness_centrality, eigenvector_centrality)
	"""

	### TO ACTUALLY INTERPRET THESE WE'LL NEED TO DO SOME RESEARCH:
	### https://www2.unb.ca/~ddu/6634/Lecture_notes/Lecture_4_centrality_measure.pdf

	deg = nx.degree_centrality(G)
	bet = nx.betweenness_centrality(G)
	eig = nx.eigenvector_centrality(G)
	return (deg, bet, eig)

def n_most_central(centrality_dict, n):
	"""
	Parameters
	-----------------
	centrality_dict : dict
		Any of the dictionaries output by get_centralities(G)
	n : int
		Number of items to return

	Returns
	----------------
	n_highest : tuple
		tuple returning (degree_centrality, betweenness_centrality, eigenvector_centrality)
	"""
	return nlargest(n, centrality_dict, key = centrality_dict.get)

def plot_degree_distribution(degree_sequence):
	bins = np.arange(0, 42, 4)
	data = [ d for d, n in degree_sequence ]
	plt.hist(data, bins=bins)
	plt.title('Degree Distribution')
	plt.xlabel('Degree of Node')
	plt.ylabel('Count')

	plt.show()

if __name__ == '__main__':
	G, figure = g.get_scraped_graph()

	print("Num nodes: ", get_num_nodes(G))
	print("Num edges: ", get_num_edges(G))

	degree_sequence = get_degree_distribution(G)
	plot_degree_distribution(degree_sequence)
	(deg, bet, eig) = get_centralities(G)

	print(n_most_central(deg, 10))
	print(n_most_central(bet, 10))
	print(n_most_central(eig, 10))
