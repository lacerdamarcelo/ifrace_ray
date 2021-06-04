import numpy as np

def modify_population_size(population, fitnesses, fitness_call, delta_pop_size, v, search_space_bounds,
                           pop_matrices_data, pop_matrices_remove_add_column, pop_matrices_gen_copy):
    search_space_bounds_t = search_space_bounds.transpose()
    search_space_bounds_t_delta = search_space_bounds_t[1] - search_space_bounds_t[0]
    if delta_pop_size < 0:
        removed_individuals_counter = 0
        while removed_individuals_counter < abs(delta_pop_size):
            fitnesses_sum = np.sum(fitnesses)
            probabilities = [fitness / fitnesses_sum for fitness in fitnesses]
            chosen_index = np.random.choice(np.arange(0, len(fitnesses)),
                                            p=probabilities)
            for i in range(len(pop_matrices_data)):
                pop_matrices_data[i] = np.delete(pop_matrices_data[i], chosen_index, 0)
                if pop_matrices_remove_add_column[i]:
                    pop_matrices_data[i] = np.delete(pop_matrices_data[i], chosen_index, 1)
            population = np.delete(population, chosen_index, 0)
            fitnesses = np.delete(fitnesses, chosen_index, 0)
            removed_individuals_counter += 1
    elif delta_pop_size > 0:
        added_individuals_counter = 0
        modified_fitness = [1.0 / (fitness - 0.0001) for fitness in fitnesses]
        modified_fitness_sum = sum(modified_fitness)
        probabilities = [mod_fit / modified_fitness_sum for mod_fit in modified_fitness]
        previous_pop_size = len(population)
        new_individuals = []
        new_pop_row_data = []
        new_pop_column_data = []
        for i in range(len(pop_matrices_data)):
            new_pop_row_data.append([])
            if pop_matrices_remove_add_column[i]:
                new_pop_column_data.append([])
        while added_individuals_counter < delta_pop_size:
            chosen_index = np.random.choice(a=np.arange(0, previous_pop_size),
                                            p=probabilities)
            new_individual = np.copy(population[chosen_index])
            
            for i in range(len(pop_matrices_data)):
                if pop_matrices_gen_copy[i]:
                    if type(pop_matrices_data[i][chosen_index]) == np.ndarray:
                        new_pop_row_data[i].append(np.copy(pop_matrices_data[i][chosen_index]))
                    else:
                        new_pop_row_data[i].append(pop_matrices_data[i][chosen_index])
                else:
                    if type(pop_matrices_data[i][chosen_index]) == np.ndarray:
                        new_pop_row_data[i].append(np.zeros(pop_matrices_data[i][chosen_index].shape[0]))
                    else:
                        new_pop_row_data[i].append(0)
                if pop_matrices_remove_add_column[i]:
                    if pop_matrices_gen_copy[i]:                    
                        new_pop_column_data[i].append(np.concatenate([np.copy(pop_matrices_data[i][chosen_index]),
                                                                          np.zeros(delta_pop_size,)]))
                    else:
                        new_pop_column_data[i].append(np.zeros(pop_matrices_data[i][chosen_index].shape[0] + delta_pop_size))
            
            # ((search_space_bounds_t_delta / 4) - 1) is used because in the simulations I defiend the boundaries by
            # varying a variable 'i', given that search_space_bounds_t_delta = i * 2 - i * -2
            # This function was approximated by non-linear least squares method from the following set of data:
            # (dimensions, space_boundaries_length) -> max_v, where random_vector * (v=1) * max_v generates individuals within the boundaries of the
            # search space in 95% of the time.
            random_vector = np.random.randn(population.shape[1])
            new_individual += random_vector * v * (0.53559486 * np.power(1.00012346, 0.82182626 * population.shape[1]) * ((search_space_bounds_t_delta) - 1) - 2.28402209)
            new_indiv_lower_min = new_individual < search_space_bounds_t[0][0]
            new_indiv_greater_max = new_individual > search_space_bounds_t[1][0]
            new_individual[new_indiv_lower_min] = search_space_bounds_t[0][0]
            new_individual[new_indiv_greater_max] = search_space_bounds_t[1][0]
            new_individuals.append(new_individual)
            added_individuals_counter += 1
        new_individuals = np.array(new_individuals)
        new_fitnesses = np.array([fitness_call(individual) for individual in new_individuals])
        fitnesses = np.concatenate([fitnesses, new_fitnesses])
        population = np.concatenate([population, new_individuals])
        for i in range(len(pop_matrices_data)):
            pop_matrices_data[i] = np.concatenate([pop_matrices_data[i], np.array(new_pop_row_data[i])])
            if pop_matrices_remove_add_column[i]:
                pop_matrices_data[i] = np.concatenate([pop_matrices_data[i], np.array(new_pop_column_data[i]).transpose])
    return population, fitnesses, pop_matrices_data
