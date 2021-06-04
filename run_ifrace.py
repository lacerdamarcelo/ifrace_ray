import sys
import ray
import json
from ifrace import IFRace
from metaheuristics import HCLPSO, FSS, DE, BinGA, ACO_TSP
from knapsack import Knapsack
from tsp import TSP
from cec17 import CEC17
from datetime import datetime, timedelta

redis_address=sys.argv[1]
redis_password=sys.argv[2]
ray.init(address=redis_address, redis_port=6380, redis_password=redis_password)

alg_config_file_path = sys.argv[3]
with open(alg_config_file_path, 'r') as f:
	parameters_data = json.load(f)
parameters_ranges = parameters_data['parameters_ranges']
for parameter in parameters_data['constant_parameters']:
	parameters_ranges[parameter] = [parameters_data['constant_parameters'][parameter],
									parameters_data['constant_parameters'][parameter]]

algorithm_class = eval(sys.argv[4])

problem_class = eval(sys.argv[5])
instances_file_path = sys.argv[6]
with open(instances_file_path, 'r') as f:
	instances_files = [line.split('\n')[0] for line in f.readlines()]
instances = []
for instance_file in instances_files:
	instances.append(problem_class(instance_file))

number_of_configurations = int(sys.argv[7])
min_frace_iterations = int(sys.argv[8])
maximum_generator_stdev = float(sys.argv[9])
budget = timedelta(days=float((sys.argv[10])))
number_configurations_threshold = int(sys.argv[11])
maximum_frace_iterations = int(sys.argv[12])
sample_size_per_run = int(sys.argv[13])
iterations_per_algorithm_exec = int(sys.argv[14])
test_results_file_path = sys.argv[15]

ifrace = IFRace(parameters_ranges, algorithm_class, instances, number_of_configurations,
                 min_frace_iterations, maximum_generator_stdev, budget,
                 number_configurations_threshold, maximum_frace_iterations, sample_size_per_run,
                 iterations_per_algorithm_exec, test_results_file_path)
ifrace.run()
