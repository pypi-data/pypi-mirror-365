from drex.utils.tool_functions import *

import time
import sys
import numpy

def algorithm3(number_of_nodes, reliability_of_nodes, bandwidths, reliability_threshold, file_size, real_records, node_sizes, predictor):
	"""
	Uses a pareto front to find best N with biggest K possible
	"""
	start = time.time()

	# 1. Get set of N, K and associated nodes that match the reliability and put them in a list, with fastest N when multiple set of nodes can satisfy the reliability
	min_K = 0
	set_of_nodes_chosen = []
	set_of_nodes = list(range(0, number_of_nodes))
	set_of_possible_solutions = []
	time_and_space_from_set_of_possible_solution = []

	for i in range(2, number_of_nodes + 1):
		for set_of_nodes_chosen in itertools.combinations(set_of_nodes, i):
			reliability_of_nodes_chosen = []
			bandwidth_of_nodes_chosen = []
			
			reliability_of_nodes_chosen = [reliability_of_nodes[node] for node in set_of_nodes_chosen]
			bandwidth_of_nodes_chosen = [bandwidths[node] for node in set_of_nodes_chosen]
			
			K = get_max_K_from_reliability_threshold_and_nodes_chosen(
			    i, reliability_threshold, reliability_of_nodes_chosen)
			if (K != -1 and nodes_can_fit_new_data(set_of_nodes_chosen, node_sizes, file_size/K)):
				#replication_and_write_time = replication_and_chuncking_time(i, K, file_size, bandwidth_of_nodes_chosen, real_records)
				replication_and_write_time = predictor.predict(
				    file_size, i, K, bandwidth_of_nodes_chosen)
				
				set_of_possible_solutions.append((i, K, set_of_nodes_chosen, replication_and_write_time, (file_size/K)*i))
				time_and_space_from_set_of_possible_solution.append([replication_and_write_time, (file_size/K)*i])

	if (len(time_and_space_from_set_of_possible_solution) == 0):
		# ~ print("Algorithm 3 could not find a solution that would not overflow the memory of the nodes")
		return - 1, -1, -1, node_sizes
	
	# 2. Take those that are on the pareto front
	costs = numpy.asarray(time_and_space_from_set_of_possible_solution)
	set_of_solution_on_pareto = is_pareto_efficient(costs, False)

	time_on_pareto = []
	for i in range (0, len(set_of_solution_on_pareto)):
		time_on_pareto.append(time_and_space_from_set_of_possible_solution[set_of_solution_on_pareto[i]][0])
	
	# 3. Finding the solution on the plateau
	# Get min and max
	# ~ time_on_pareto.sort() # Already sorted by time anyway as it's the first value
	size = len(time_on_pareto) - 1
	
	max_time = max(time_on_pareto)
	min_time = min(time_on_pareto)
	
	# Start from smallest time and stop when 10% degradation of time has been made and keep the index
	total_progress = max_time - min_time
	if (total_progress == 0): # Don't want to divide by 0 so we take the last result
		min_index = size
	else:
		min_index = -1
		min_progress = sys.maxsize
		for i in range (0, size+1):
			progress = 100 - ((time_on_pareto[i] - min_time)*100)/total_progress

			if progress < 90:
				break
			if progress < min_progress:
				min_progress = progress
				min_index = i
		if min_index == -1:
			min_index = 0
	
	min_N = set_of_possible_solutions[set_of_solution_on_pareto[min_index]][0]
	min_K = set_of_possible_solutions[set_of_solution_on_pareto[min_index]][1]
	min_set_of_nodes_chosen = set_of_possible_solutions[set_of_solution_on_pareto[min_index]][2]
	
	node_sizes = update_node_sizes(min_set_of_nodes_chosen, min_K, file_size, node_sizes)
	
	end = time.time()
	
	# ~ print("\nAlgorithm 3 chose N =", min_N, "and K =", min_K, "with the set of nodes:", min_set_of_nodes_chosen, "It took", end - start, "seconds.")
	
	return list(min_set_of_nodes_chosen), min_N, min_K, node_sizes

def algorithm3_look_at_reduced_set_of_possibilities(number_of_nodes, reliability_of_nodes, bandwidths, reliability_threshold, file_size, real_records, node_sizes, predictor):
	"""
	Uses a pareto front to find best N with biggest K possible
	Look at nodes by group of 10 and then one possibility from 10 to number_of_nodes in order to reduce the complexity
	"""
	start = time.time()

	# 1. Get set of N, K and associated nodes that match the reliability and put them in a list, with fastest N when multiple set of nodes can satisfy the reliability
	min_K = 0
	set_of_nodes_chosen = []
	set_of_nodes = list(range(0, number_of_nodes))
	set_of_possible_solutions = []
	time_and_space_from_set_of_possible_solution = []

	subset_size = 10
	subsets = create_subsets(set_of_nodes, subset_size)
	
	# Above 10 we do random values. 
	subsets_random_values = []
	for i in range (subset_size+1, number_of_nodes+1):
		for j in range (0, number_of_nodes+1 - i):
			subsets_random_values.append(create_subsets_with_random_values(0, number_of_nodes, i))

	for j in range (len(subsets)):
		for i in range(2, len(subsets[j]) + 1):
			for set_of_nodes_chosen in itertools.combinations(subsets[j], i):
				reliability_of_nodes_chosen = []
				bandwidth_of_nodes_chosen = []
				
				reliability_of_nodes_chosen = [reliability_of_nodes[node] for node in set_of_nodes_chosen]
				bandwidth_of_nodes_chosen = [bandwidths[node] for node in set_of_nodes_chosen]
				
				K = get_max_K_from_reliability_threshold_and_nodes_chosen(
					i, reliability_threshold, reliability_of_nodes_chosen)

				if (K != -1 and nodes_can_fit_new_data(set_of_nodes_chosen, node_sizes, file_size/K)):
					replication_and_write_time = predictor.predict(
						file_size, i, K, bandwidth_of_nodes_chosen)
					
					set_of_possible_solutions.append((i, K, set_of_nodes_chosen, replication_and_write_time, (file_size/K)*i))
					time_and_space_from_set_of_possible_solution.append([replication_and_write_time, (file_size/K)*i])
	
	# Now loop on the random subsets
	for set_of_nodes_chosen in subsets_random_values:
		reliability_of_nodes_chosen = []
		bandwidth_of_nodes_chosen = []
		N = len(set_of_nodes_chosen)
				
		reliability_of_nodes_chosen = [reliability_of_nodes[node] for node in set_of_nodes_chosen]
		bandwidth_of_nodes_chosen = [bandwidths[node] for node in set_of_nodes_chosen]
				
		K = get_max_K_from_reliability_threshold_and_nodes_chosen(
			N, reliability_threshold, reliability_of_nodes_chosen)

		if (K != -1 and nodes_can_fit_new_data(set_of_nodes_chosen, node_sizes, file_size/K)):
			replication_and_write_time = predictor.predict(
				file_size, N, K, bandwidth_of_nodes_chosen)
					
			set_of_possible_solutions.append((N, K, set_of_nodes_chosen, replication_and_write_time, (file_size/K)*N))
			time_and_space_from_set_of_possible_solution.append([replication_and_write_time, (file_size/K)*N])

	if (len(time_and_space_from_set_of_possible_solution) == 0):
		print("Algorithm 3 could not find a solution that would not overflow the memory of the nodes")
		return - 1, -1, -1, node_sizes
	
	# 2. Take those that are on the pareto front
	costs = numpy.asarray(time_and_space_from_set_of_possible_solution)
	set_of_solution_on_pareto = is_pareto_efficient(costs, False)

	time_on_pareto = []
	for i in range (0, len(set_of_solution_on_pareto)):
		time_on_pareto.append(time_and_space_from_set_of_possible_solution[set_of_solution_on_pareto[i]][0])
	
	# 3. Finding the solution on the plateau
	# Get min and max
	# ~ time_on_pareto.sort() # Already sorted by time anyway as it's the first value
	size = len(time_on_pareto) - 1
	
	max_time = max(time_on_pareto)
	min_time = min(time_on_pareto)
	
	# Start from smallest time and stop when 10% degradation of time has been made and keep the index
	total_progress = max_time - min_time
	if (total_progress == 0): # Don't want to divide by 0 so we take the last result
		min_index = size
	else:
		min_index = -1
		min_progress = sys.maxsize
		for i in range (0, size+1):
			progress = 100 - ((time_on_pareto[i] - min_time)*100)/total_progress

			if progress < 90:
				break
			if progress < min_progress:
				min_progress = progress
				min_index = i
		if min_index == -1:
			min_index = 0
	
	min_N = set_of_possible_solutions[set_of_solution_on_pareto[min_index]][0]
	min_K = set_of_possible_solutions[set_of_solution_on_pareto[min_index]][1]
	min_set_of_nodes_chosen = set_of_possible_solutions[set_of_solution_on_pareto[min_index]][2]
	
	node_sizes = update_node_sizes(min_set_of_nodes_chosen, min_K, file_size, node_sizes)
	
	end = time.time()
	
	print("\nalgorithm3_look_at_reduced_set_of_possibilities chose N =", min_N, "and K =", min_K, "with the set of nodes:", min_set_of_nodes_chosen, "It took", end - start, "seconds.")
	
	return list(min_set_of_nodes_chosen), min_N, min_K, node_sizes
