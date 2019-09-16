from random import shuffle, choices, choice, sample
import math
import time


def __init_population(cities, num_individuals):
    cities_clone = cities.copy()

    population = []
    for i in range(num_individuals):
        shuffle(cities_clone)
        first_city = cities_clone[0]
        cities_path = cities_clone.copy()
        cities_path.append(first_city)

        individual = []
        for j in range(len(cities_path) - 1):
            orig_city, orig_lat, orig_long = int(cities_path[j][0]), float(cities_path[j][1]), float(cities_path[j][2])
            dest_city, dest_lat, dest_long = int(cities_path[j + 1][0]), float(cities_path[j + 1][1]), float(cities_path[j + 1][2])

            route_distance = __calculate_distance(orig_lat, dest_lat, orig_long, dest_long)
            individual.append((orig_city, dest_city, route_distance))

        population.append(individual)

    return population


def __calculate_cities_distance(city_1, city_2, cities):
    _, orig_lat, orig_long = cities[city_1 - 1]
    _, dest_lat, dest_long = cities[city_2 - 1]
    return __calculate_distance(float(orig_lat), float(dest_lat), float(orig_long), float(dest_long))


def execute(cities, num_individuals, mutation_ratio, selection_type):
    population = __init_population(cities, num_individuals)

    unimproved_iterations_limit = 25
    num_descendants = 3

    best_fitness = None
    best_fitness_history = []
    best_individual = None
    best_individual_history = []
    unimproved_iterations = 0
    num_iterations = 0
    opt_time = 0

    print('########## Optimization ##########\n')
    while unimproved_iterations < unimproved_iterations_limit:
        print('********** Iteration ' + str(num_iterations + 1) + ' **********')

        iter_start = time.time()
        num_iterations += 1

        population = __reproduction(population, num_individuals, num_descendants, mutation_ratio, cities)
        population = __selection(population, selection_type, num_individuals, num_descendants)
        best_individual_candidate = __get_best_individual(population)
        best_fitness_candidate = __get_fitness(best_individual_candidate)

        if best_fitness is None or best_fitness_candidate < best_fitness:
            best_fitness = best_fitness_candidate
            best_individual = best_individual_candidate
            best_individual_history.append(best_individual)
            unimproved_iterations = 0

            print('New best individual with fitness ' + str(best_fitness))
        else:
            unimproved_iterations += 1
            print('No improvement in this iteration. ' +
                  'Number of unimproved iterations: ' +
                  str(unimproved_iterations) + '/' + str(unimproved_iterations_limit)
                  )

        best_fitness_history.append(best_fitness)

        iter_time = time.time() - iter_start
        opt_time += iter_time
        print('Execution time: ' + str(opt_time) + ' s')
        print('*********************************\n')

    print('##################################')

    return best_individual, best_individual_history, best_fitness_history


def __reproduction(population, num_individuals, num_descendants, mutation_ratio, cities):
    new_population = []

    factor = sum([__get_fitness(i) for i in population])
    weights = [__get_fitness(i) / factor for i in population]

    while len(new_population) < num_individuals * num_descendants:
        parents = __choices_no_replacement(population, weights, 2)

        for i in range(num_descendants):
            new_population.append(__generate_descendant(parents, cities))

    __mutation(population, mutation_ratio, cities)
    new_population += population
    return new_population


def __generate_descendant(parents, cities):
    descendant = None

    num_routes = len(parents[0])
    parent_1_fitness = __get_fitness(parents[0])
    parent_2_fitness = __get_fitness(parents[1])

    if parent_1_fitness < parent_2_fitness:
        route_fragment_size = math.ceil((1 - (parent_1_fitness / parent_2_fitness)) * num_routes)

        if route_fragment_size == 0:
            route_fragment_size = math.ceil(num_routes / 2)

        route_fragment = __get_route_fragment(parents[0], route_fragment_size)
        descendant = __insert_route_fragment(parents[1], route_fragment, cities)
    else:
        route_fragment_size = math.ceil((1 - (parent_2_fitness / parent_1_fitness)) * num_routes)

        if route_fragment_size == 0:
            route_fragment_size = math.ceil(num_routes / 2)

        route_fragment = __get_route_fragment(parents[1], route_fragment_size)
        descendant = __insert_route_fragment(parents[0], route_fragment, cities)

    return descendant


def __get_route_fragment(individual, route_fragment_size):
    initial_index = choice(list(range(len(individual) - route_fragment_size)))
    return individual[initial_index:initial_index + route_fragment_size]


def __insert_route_fragment(individual, route_fragment, cities):
    descendant = individual.copy()

    for i in range(len(descendant)):
        route = descendant[i]

        if route[0] == route_fragment[0][0]:
            for j in range(len(route_fragment)):
                index = 0

                if i + j >= len(descendant):
                    index = i + j - len(descendant)
                else:
                    index = i + j

                if j > 0:
                    __shift_cities(descendant, descendant[index][0], route_fragment[j][0], cities)

                __shift_cities(descendant, descendant[index][1], route_fragment[j][1], cities)

            break

    return descendant


def __mutation(population, mutation_ratio, cities):
    if mutation_ratio > 0:
        num_cities = len(population[0])
        num_shifts = int(num_cities * mutation_ratio)
        cities_indices = list(range(1, num_cities + 1))

        for individual in population:
            if choice([True, False]):
                for i in range(num_shifts):
                    [city_1, city_2] = sample(cities_indices, 2)
                    __shift_cities(individual, city_1, city_2, cities)


def __shift_cities(individual, city_1, city_2, cities):
    city_1_routes = 0
    city_2_routes = 0
    for i in range(len(individual)):
        route = individual[i]

        if route[0] == city_1:
            route = city_2, route[1], __calculate_cities_distance(city_2, route[1], cities)
            city_1_routes += 1
            if route[1] == city_2:
                route = route[0], city_1, __calculate_cities_distance(route[0], city_1, cities)
                city_2_routes += 1
        elif route[1] == city_1:
            route = route[0], city_2, __calculate_cities_distance(route[0], city_2, cities)
            city_1_routes += 1
            if route[0] == city_2:
                route = city_1, route[1], __calculate_cities_distance(city_1, route[1], cities)
                city_2_routes += 1
        elif route[0] == city_2:
            route = city_1, route[1], __calculate_cities_distance(city_1, route[1], cities)
            city_2_routes += 1
            if route[1] == city_1:
                route = route[0], city_2, __calculate_cities_distance(route[0], city_2, cities)
                city_1_routes += 1
        elif route[1] == city_2:
            route = route[0], city_1, __calculate_cities_distance(route[0], city_1, cities)
            city_2_routes += 1
            if route[0] == city_1:
                route = city_2, route[1], __calculate_cities_distance(city_2, route[1], cities)
                city_1_routes += 1

        individual[i] = route

        if city_1_routes == 2 and city_2_routes == 2:
            break


def __selection(population, selection_type, num_individuals, num_descendants):
    if selection_type == 1:
        return __roulette_selection(population, num_individuals)
    elif selection_type == 2:
        return __round_selection(population, num_individuals, num_descendants)
    elif selection_type == 3:
        return __elitist_selection(population, num_individuals)
    else:
        return population[0:num_individuals]


def __roulette_selection(population, num_individuals):
    factor = sum([__get_fitness(i) for i in population])
    weights = [__get_fitness(i) / factor for i in population]

    return __choices_no_replacement(population, weights, num_individuals)


def __round_selection(population, num_individuals, num_descendants):
    shuffle(population)
    round_size = num_descendants + 1

    new_population = []
    for i in range(0, num_individuals):
        population_slice = population[i * round_size:round_size * (i + 1)]
        new_population.append(__get_best_individual(population_slice))

    return new_population


def __elitist_selection(population, num_individuals):
    new_population = []

    for i in range(num_individuals):
        best_individual = __get_best_individual(population)
        new_population.append(best_individual.copy())
        population.remove(best_individual)

    return new_population


def __get_best_individual(population):
    best_individual = None
    best_fitness = None
    for individual in population:
        fitness = __get_fitness(individual)
        if best_fitness is None or fitness < best_fitness:
            best_individual = individual
            best_fitness = fitness

    return best_individual


def __get_fitness(individual):
    return sum([route[2] for route in individual])


def __calculate_distance(orig_lat, dest_lat, orig_long, dest_long):
    return math.sqrt((orig_lat - dest_lat) ** 2 + (orig_long - dest_long) ** 2)


def __choices_no_replacement(l, weights, k):
    result = []
    indices = list(range(len(l)))
    weights_copy = weights.copy()
    while k > 0:
        index = choices(population=indices, weights=weights_copy, k=1)[0]
        result.append(l[index].copy())
        i = indices.index(index)
        del indices[i]
        del weights_copy[i]
        k -= 1

    return result
