"""
@Author: Joris van Vugt, adapted by Moira Berens

Implementation of the variable elimination algorithm for AISPAML assignment 3

"""

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
	probs = self.network.probabilities.copy()
	for elim_node in elim_order:
		dist = probs.pop(elim_node)
		for n in probs:
			if observed[node]:
				
			
		print "AAA", dist
		
