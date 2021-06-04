import sys
import ray
import random
import psutil
import numpy as np
from scipy.stats import friedmanchisquare, wilcoxon, rankdata
from datetime import datetime

@ray.remote
class RunSingleConfiguration(object):

    def __init__(self, configuration, instance, parameters_ranges, sample_size_per_run,
                 algorithm_class, iterations_per_algorithm_exec):
        self.configuration = configuration
        self.instance = instance
        self.parameters_ranges = parameters_ranges
        self.sample_size_per_run = sample_size_per_run
        self.algorithm_class = algorithm_class
        self.iterations_per_algorithm_exec = iterations_per_algorithm_exec

    @ray.method(num_return_vals=1)
    def run(self):
        performance = []
        params_dict = {}
        for i, key in enumerate(self.parameters_ranges.keys()):
            params_dict[key] = self.configuration[i] * (self.parameters_ranges[key][1] - \
                                                   self.parameters_ranges[key][0]) + \
                                                   self.parameters_ranges[key][0]
        for i in range(self.sample_size_per_run):
            algorithm = self.algorithm_class(params_dict, self.instance)
            for i in range(self.iterations_per_algorithm_exec):
                algorithm.run(self.iterations_per_algorithm_exec - i)
            performance.append(algorithm.best_fitness_ever)
        return np.mean(performance)

class IFRace:
    def __init__(self, parameters_ranges, algorithm_class, instances, number_of_configurations,
                 min_frace_iterations, maximum_generator_stdev, budget,
                 number_configurations_threshold, maximum_frace_iterations, sample_size_per_run,
                 iterations_per_algorithm_exec, test_results_file_path):
        self.parameters_ranges = parameters_ranges
        self.number_of_configurations = number_of_configurations
        self.min_frace_iterations = min_frace_iterations
        self.maximum_generator_stdev = maximum_generator_stdev
        self.number_configurations_threshold = number_configurations_threshold
        self.maximum_frace_iterations = maximum_frace_iterations
        self.iterations_per_algorithm_exec = iterations_per_algorithm_exec
        self.sample_size_per_run = sample_size_per_run
        self.instances = instances
        self.algorithm_class = algorithm_class
        self.test_results_file_path = test_results_file_path
        with open(self.test_results_file_path, 'w') as f:
            pass
        self.current_instance = random.sample(self.instances, 1)[0]
        self.budget = budget
        self.init_time = datetime.now()
    
    def generate_configurations(self, current_configurations=None, performances=None):
        if current_configurations is None:
            current_configurations = np.random.random((self.number_of_configurations,
                                                       len(self.parameters_ranges)))
        else:
            transposed_performances = np.transpose(performances)
            rankings = [rankdata(a) for a in transposed_performances]
            rankings = np.mean(np.transpose(rankings), axis=1)
            total_configurations = len(current_configurations)
            weights = [(total_configurations - r + 1) / (total_configurations * \
                                                        (total_configurations + 1) / 2) \
                       for r in rankings]
            chosen_indexes = np.random.choice(list(range(len(current_configurations))),
                                             self.number_of_configurations - len(current_configurations),
                                             p=weights, replace=True)
            chosen_config = current_configurations[chosen_indexes]
            new_config = np.random.normal(chosen_config,
                                          self.maximum_generator_stdev * \
                                          (1 - (datetime.now() - self.init_time) / self.budget))
            new_config = np.minimum(np.maximum(new_config, np.zeros_like(new_config)),
                                    np.ones_like(new_config))
            current_configurations = np.concatenate([current_configurations, new_config])
        return current_configurations
    
    def run_configurations(self, current_configurations, previous_performances=None):
        if previous_performances is None:
            previous_performances = []
            for i in range(len(current_configurations)):
                previous_performances.append([])
        remote_call_references = []
        for i, configuration in enumerate(current_configurations):
            wrapper = RunSingleConfiguration.remote(configuration,
                                             self.current_instance,
                                             self.parameters_ranges,
                                             self.sample_size_per_run,
                                             self.algorithm_class,
                                             self.iterations_per_algorithm_exec)
            remote_call_references.append(wrapper.run.remote())
        for i in range(len(remote_call_references)):
            previous_performances[i].append(ray.get(remote_call_references[i]))
        return previous_performances
    
    def get_surviving_configurations(self, current_configurations, performances):
        if len(performances) == 1:
            return current_configurations, performances
        elif len(performances) > 2:
            stat_result = friedmanchisquare(*performances)[1]
            if stat_result <= 0.05:
                best_performance = performances[0]
                best_index = 0
                for i in range(1, len(performances)):
                    if (np.array(best_performance) == np.array(performances[i])).all():
                        stat_result = 1
                    else:
                        stat_result = wilcoxon(best_performance, performances[i])[1]
                    if stat_result <= 0.05:
                        if np.mean(best_performance) < np.mean(performances[i]):
                            best_performance = performances[i]
                            best_index = i
                surviving_configurations = [current_configurations[best_index]]
                surviving_performances = [performances[best_index]]
                for i in range(len(performances)):
                    if i != best_index:
                        if (np.array(best_performance) == np.array(performances[i])).all():
                            stat_result = 1
                        else:
                            stat_result = wilcoxon(best_performance, performances[i])[1]
                        if stat_result > 0.05:
                            surviving_configurations.append(current_configurations[i])
                            surviving_performances.append(performances[i])
                return np.array(surviving_configurations), surviving_performances
            else:
                return np.array(current_configurations), performances
        else:
            if (np.array(performances[0]) == np.array(performances[1])).all():
                stat_result = 1
            else:           
                stat_result = wilcoxon(performances[0], performances[1])[1]
            if stat_result <= 0.05:
                if np.mean(performances[0]) > np.mean(performances[1]):
                    return np.array([current_configurations[0]]), [performances[0]]
                else:
                    return np.array([current_configurations[1]]), [performances[1]]
            else:
                return current_configurations, performances
            
    def test_best_configuration(self, configurations, instance):
        configuration_index = random.sample(range(len(configurations)), 1)[0]
        configuration = configurations[configuration_index]
        param_dict = {}
        for i, key in enumerate(self.parameters_ranges.keys()):
            param_dict[key] = configuration[i] * (self.parameters_ranges[key][1] - \
                                                   self.parameters_ranges[key][0]) + \
                                                   self.parameters_ranges[key][0]
        testing_instances = instance.test_instances
        with open(self.test_results_file_path, 'a') as f:
            f.write(str(datetime.now()) + '\n')
            f.write(str(param_dict) + '\n')
        for test_instance in testing_instances:
            with open(self.test_results_file_path, 'a') as f:
                f.write(str(test_instance) + ': ')
            instance.running_instances = [test_instance]
            instance.indexes = []
            instance.next_instance()
            performance = []
            for i in range(self.sample_size_per_run):
                algorithm = self.algorithm_class(param_dict, instance)
                for i in range(self.iterations_per_algorithm_exec):
                    algorithm.run(self.iterations_per_algorithm_exec - i)
                performance.append(str(algorithm.best_fitness_ever))
            with open(self.test_results_file_path, 'a') as f:
                f.write(','.join(performance) + '\n')
        instance.running_instances = instance.training_instances
        instance.indexes = []
        instance.next_instance()
            
    def run(self):
        init_time = datetime.now()
        configs = None
        performances = None
        while datetime.now() - init_time < self.budget:
            configs = self.generate_configurations(configs, performances)
            performances = None
            frace_iteration_counter = 0
            while len(configs) > self.number_configurations_threshold and \
                  frace_iteration_counter < self.maximum_frace_iterations:
                performances = self.run_configurations(configs, performances)
                print('ANTES:', len(configs), len(performances))
                while len(performances[0]) < self.min_frace_iterations:
                    print(psutil.virtual_memory())
                    performances = self.run_configurations(configs, performances)
                configs, performances = self.get_surviving_configurations(configs, performances)
                print('DEPOIS:', len(configs), len(performances))
                self.current_instance = random.sample(self.instances, 1)[0]
                self.test_best_configuration(configs, self.current_instance)
                frace_iteration_counter += 1
                print(frace_iteration_counter)
