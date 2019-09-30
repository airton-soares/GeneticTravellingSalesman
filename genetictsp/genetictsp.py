from argparse import ArgumentParser, ArgumentTypeError
from matplotlib.path import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import genetic_algorithm as ga
import os
import pathlib


def mutation_range(s):
    f = float(s)

    if f < 0.0 or f > 1.0:
        raise ArgumentTypeError("%r not in range [0.0, 1.0]" % (f,))

    return f


def build_args_parser():
    usage = 'python genetictsp.py -i <input file>\n       ' \
            'run with --help for arguments descriptions'
    parser = ArgumentParser(description='A genetic algorithm project to find a good solution the travelling salesman'
                                        'problem',
                            usage=usage)
    parser.add_argument('--in', dest='in_file_path', required=True,
                        help='Path to the file with the cities map description following the TSPLIB'
                             '(http://elib.zib.de/pub/mp-testdata/tsp/tsplib/tsp/)')
    parser.add_argument('--out', dest='out_path', default='results',
                        help='Path to the directory where all the generated data will be saved')
    parser.add_argument('-i', '--individuals', dest='num_individuals', type=int, default=1000,
                        help='Number of individuals in each population during the execution of the algorithm')
    parser.add_argument('-m', '--mutation', dest='mutation_ratio', type=mutation_range, default=0.02,
                        help='Initial mutation ratio for the genetic algorithm. Should be between 0 and 1')
    parser.add_argument('-s', '--selection', dest='selection_type', type=int, default=3, choices=[1, 2, 3],
                        help='Type of selection to be used by the genetic algorithm. Available types:\n       '
                             '1 - Round Robin\n       '
                             '2 - Elitism\n       '
                             '3 - Roulette Wheel Selection\n       ')
    parser.add_argument('-d', '--descendants', dest='num_descendants', type=int, default=5,
                        help='Number of descendants that will be generated during the reproduction')

    return parser


def parse_cities(in_file_path):
    cities = []

    with open(in_file_path) as f:
        content = f.readlines()
        qtd_cities = int(content[3].split(':')[1].strip())
        cities_str = content[6:6 + qtd_cities]

        for i in range(0, len(cities_str)):
            city = tuple(cities_str[i].split())
            cities.append(city)

    return cities


def save_results(best_individual, best_fitness_history, execution_time, in_file_path, out_path, cities):
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    file_path = os.path.join(out_path, 'result_metrics.txt')
    file = open(file_path, 'w')
    file.write('Best Result: ' + str(best_fitness_history[-1]) + '\n')
    file.write('Number of Iterations: ' + str(len(best_fitness_history)) + '\n')
    file.write('Execution Time: ' + str(execution_time) + '\n')

    file_name = os.path.basename(in_file_path)
    file_extension = pathlib.Path(file_name).suffix
    file_name = file_name.replace(file_extension, '.opt.tour')
    file_path = os.path.join(out_path, file_name)
    file = open(file_path, 'w')
    file.write('NAME : ' + file_name + '\n')
    file.write('TYPE : TOUR\n')
    file.write('DIMENSION : ' + str(len(best_individual)) + '\n')
    file.write('TOUR_SECTION\n')
    for route in best_individual:
        file.write(str(route[0]) + '\n')
    file.write('-1\n')
    file.write('EOF\n')
    file.close()

    file_path = os.path.join(out_path, 'fitness_history.txt')
    file = open(file_path, 'w')
    for fit in best_fitness_history:
        file.write(str(fit) + '\n')
    file.close()

    plt.plot(best_fitness_history)
    plt.xlabel('Iteration')
    plt.ylabel('Distance')
    plt.savefig(out_path + '/fitness_history.png')


def main():
    args_parser = build_args_parser()
    args = args_parser.parse_args()

    cities = parse_cities(args.in_file_path)
    best_individual, best_fitness_history, execution_time = ga.execute(cities, args.num_individuals,
                                                                       args.mutation_ratio, args.selection_type,
                                                                       args.num_descendants)
    save_results(best_individual, best_fitness_history, execution_time, args.in_file_path, args.out_path, cities)


if __name__ == '__main__':
    main()
