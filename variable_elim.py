"""
@Author: Joris van Vugt, adapted by Moira Berens

Implementation of the variable elimination algorithm for AISPAML assignment 3

"""

import pandas as pd

class VariableElimination():

    def __init__(self, network):
	self.network = network
	self.addition_steps =  0
	self.multiplication_steps = 0

    def run(self, query, observed, elim_order):
	"""
	Use the variable elimination algorithm to find out the probability
	distribution of the query variable given the observed variables

	Input:
	    query:      The query variable
	    observed:   A dictionary of the observed variables {variable: value}
	    elim_order: Either a list specifying the elimination ordering
			or a function that will determine an elimination ordering
			given the network during the run

	Output: A variable holding the probability distribution
		for the query variable

	"""
	print "The query variable:", query
	print "The observed variables:", observed

	factors = self.network.probabilities.copy()

	print "Reducing observed variables..."

	for obs_node in observed:
	    # don't care about the probability distributions of observed variables
	    if obs_node in factors:
		factors.pop(obs_node)

	    # reduce observed variable in factor
	    for name, factor in factors.viewitems():
		if obs_node in factor:
		    print "Reducing", obs_node, "in", name
		    factors[name] = factor[factor[obs_node] == observed[obs_node]]
		    del factors[name][obs_node]
	
	print "Elimination ordering: ", elim_order

	for elim_node in elim_order:
	    # don't eliminate query variables/observed variables
	    if elim_node == query or not elim_node in factors:
		continue

	    # eliminate
	    elim_factor = factors.pop(elim_node)

	    elim_factor.rename(columns={'prob': 'elim_prob'}, inplace=True)

            print "Multiplying factors containing", elim_node
	    for name, factor in factors.viewitems():
		if elim_node in factor:
		    print "Summing", elim_node, "out of", name
		    # factor product
		    new_factor = pd.merge(factor, elim_factor, on=elim_node, sort=False)
		    new_factor['prob'] *= new_factor.elim_prob
		    del new_factor['elim_prob']
		    del new_factor[elim_node]

		    # factor marginalization
		    combined_columns = list(new_factor)
		    combined_columns.remove('prob')
		    print "Replacing", name, "with new factor"
		    factors[name] = new_factor.groupby(combined_columns).sum().reset_index()

	query_dist = factors[query]
	print "Normalizing"
	query_dist['prob'] /= query_dist['prob'].sum()

	return factors[query]
