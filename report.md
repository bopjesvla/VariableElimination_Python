# Implementing a Performant Inference Algorithm

**Bob de Ruiter | s4344952 | 04-06-2017**

## Specification

I set out to implement a performant inference algorithm for Bayesian networks.

## Design

The variable elimination algorithm, designed by Rina Derchter, takes a Bayesian network, a query variable which is to be inferred, any number of observed variables with corresponding value assignments, and an elimination ordering. With these variables in hand, the high-level algorithm is quite simple:

- Identify factors and reduce observed variables
- For every variable Z in the elimination ordering:
	- Multiply factors containing Z
	- Sum out Z to obtain new factor fZ
	- Remove the multiplied factors form the list and add fZ
- Normalize the result to make it a probability distribution
- Return this distribution

A large advantage of this method over Judea Pearl's object-oriented message passing algorithm is that it works on arbitrary Bayesian networks, not just trees.

## Implementation

My implementation of the variable elimination algorithm was based on the Python template provided by Joris van Vugt and used the pandas-based implementation of Bayesian networks by the same author.

The sections below explain the most important parts of the code. The remainder of the code directly maps to the algorithm described above. If anything is unclear, there are additional comments in the source code. Looking up the location of the log statements might also shed some light.

### Factors

The most interesting parts of the code are the operations on the factors: reduction, marginalization and multiplication. To implement the latter two, I made use of the SQL-like capabilities of pandas, and I will use SQL analogies to explain both. If you find yourself unfamiliar with both pandas and SQL, I suggest looking up the SQL equivalents, which, as the most-used data querying language, has far better documentation than pandas.

The reason for using these SQL-like capabilities is that they are not only more concise than their imperative counterparts, but they are also highly performant, making use of internal data structure in a way that outside operations cannot.

**Reduction**

```python
probs[name] = factor[factor[obs_node] == observed[obs_node]]
del probs[name][obs_node]
```

Reducing a variable in a factor is equivalent to taking all rows which have the observed value, which is done using array masking, and deleting the observed column.

**Multiplication**

```python
elim_factor = probs.pop(elim_node)

elim_factor.rename(columns={'prob': 'elim_prob'}, inplace=True)

print "Multiplying factors containing", elim_node

for name, factor in probs.viewitems():
		if elim_node in factor:
			print "Summing", elim_node, "out of", name
			print "Replacing", name, "with new factor"
			# factor product
			new_factor = pd.merge(factor, elim_factor, on=elim_node, sort=False)
			new_factor['prob'] *= new_factor.elim_prob
			del new_factor['elim_prob']

			# factor marginalization
			# ...
```

First we rename the probabilities of the factor corresponding to the eliminated variable, since joins in pandas do not have an equivalent to SQL's aliasing. Then, for every factor containing the eliminated variable, merge (which is equivalent to an inner join in SQL) it with the eliminated factor wherever the elimated variable is the same, multiply the probabilities, and delete the probabilities of the eliminated row.

Sorting, which can be quite expensive in large factor tables, is turned off since the order of the rows in a factor is not important.

**Marginalisation**

```python
del new_factor[elim_node]
combined_columns = list(new_factor)
combined_columns.remove('prob')
factors[name] = new_factor.groupby(combined_columns).sum().reset_index()
print "Replaced", name, "with new factor"
```

After performing factor multiplication, we can sum out the variable to be eliminated. When looking at a factor as a table, this can be described by deleting the eliminated variable's column, grouping together all rows that are equivalent except for their probability, and combining the almost-equivalent rows in each group by summing up their probabilities.

This is equivalent to performing a GROUP BY in SQL on all columns except for the probability, and summing over the probability. Unlike SQL servers, pandas automatically sums over the remaining column.

Another difference is that pandas' groups are hierarchical. Since we have no use for that, we flatten it by calling `reset_index`.

### Normalization

```python
query_dist = factors[query]
print "Normalizing"
query_dist['prob'] /= query_dist['prob'].sum()
```

The probabilities are normalized by dividing all probabilities by the sum of all probabilities.

### Logging

Logging is done directly to stdout. To save the log to a file, run `python2 run.py > log.txt`.

## Testing

An example output, verified on aispace.org:

```
The query variable: Alarm
The observed variables: {'JohnCalls': True}
Reducing observed variables...
Elimination ordering:  ['Burglary', 'MaryCalls', 'Alarm', 'JohnCalls', 'Earthquake']
Multiplying factors containing Burglary
Summing Burglary out of Alarm
Replacing Alarm with new factor
Multiplying factors containing MaryCalls
Multiplying factors containing Earthquake
Summing Earthquake out of Alarm
Replacing Alarm with new factor
Normalizing
RESULT
   Alarm      prob
0  False  0.983886
1   True  0.016114
```

## Conclusion

The product meets all requirements of the specification. All is well.

## Appendix

The source code should be included with this report, but can also be found at https://github.com/bopjesvla/VariableElimination_Python
