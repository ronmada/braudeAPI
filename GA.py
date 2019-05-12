
import datetime
import time
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y %m %d %H %M %S')
from GADS import Course,Course_Group,Kita,Lect,Cluster
import load_courses
from prettytable import PrettyTable
import random
import Utils
from TableSolution import TableSolution
from TableObjective import TableObjective
from TableObjective import TableObjective
from AbsGAClasses import Solution,Objective

"""
abstract classes for Objective and Solution allows for scalability, we can mix different types of objective methods and 
solution implementation to compare the options.
we do not intend to do this currently but if we will have problems with our current implementation in the future and 
want to compare a new one, the use of abstracts will easily accommodate it.
we can use the same inputs of a few implementations for many time and compare the average convergence of the generation
to the optimal solution. 
"""

class GA:

    #fitness_history is an array of arrays, each array contains the scores of a generation
    fitness_history=[]
    curent_generation=[]


    def __init__(self,create_solution_method,create_objective_method,generation_size,number_of_generations,mutation_rate,crossover_rate):
        self.create_solution_method=create_solution_method
        self.create_objective_method=create_objective_method
        self.generation_size = generation_size
        self.number_of_generations=number_of_generations
        self.mutation_rate=mutation_rate
        self.crossover_rate=crossover_rate


    def link_solution_to_objective(self,solution):
        solution.objective = self.create_objective_method(solution)


    def start(self):
        self.create_first_generation()
        self.document_generation_fitness()
        for _ in range(0,self.number_of_generations):
            self.selection()
            self.crossover()
            self.mutation()
            self.document_generation_fitness()

    def selection(self):
        survivors = []
        self.curent_generation.sort(key=lambda x: x.score)
        for _ in range(0,len(self.curent_generation)-1):
            survivors.append(Utils.decision(self.curent_generation))

        #long live the king:
        survivors.append(self.curent_generation[len(self.curent_generation)-1])

        self.curent_generation = survivors

    def crossover(self):
        replacment_counter=0
        for solution in self.curent_generation:
            # pick number from [0.0,1.0)
            pick = random.random()
            if pick>self.crossover_rate:
                mate = Utils.decision(self.curent_generation)
                first_baby = self.create_solution_method.cross_over(solution,mate)
                self.link_solution_to_objective(first_baby)
                first_baby.score = first_baby.objective.evaluation()
                # can add second baby and make them fight over survival
                self.curent_generation[replacment_counter] = first_baby
                replacment_counter+=1
        print('amount of crossovers = '+str(replacment_counter))

    def mutation(self):
        replacment_counter=0
        for solution in self.curent_generation:
            # pick number from [0.0,1.0)
            pick = random.random()
            if pick > self.mutation_rate:
                solution.mutation()
                replacment_counter+=1
        print('amount of mutations = ' + str(replacment_counter))


    def create_first_generation(self):
        """
        In the beginning, God created the heavens and earth
        """
        for _ in range(0,self.generation_size):
            solution = self.create_solution_method()
            self.link_solution_to_objective(solution)
            self.curent_generation.append(solution)

    def document_generation_fitness(self):

        fitness_scores=[]
        for solution in self.curent_generation:
            solution.score = solution.objective.evaluation()


        self.curent_generation.sort(key=lambda x: x.score)
        i = 0
        for solution in self.curent_generation:
            fitness_scores.append(solution.score)
            print(str(solution.objective.string_fitness_paramenters()))
            i+=14
        fitness_scores.sort()
        self.fitness_history.append(fitness_scores)
        print (self.fitness_history)


def run(courses,clusters,specific_windows,specific_days_off,lecturers):
    """
    example run(['11231','61992','11102'],[['61958', '11102'],['61963','61964','61965']],['(0,2)', '(1,2)', '(2,2)', '(3,2)', '(4,2)'],['0', '2', '4'],['(11102,practice,"דר אדר רון")'])

    :param courses: list of course ids in strings
    :param clusters: lists of lists (clusters) of course id's as strings
    :param specific_windows: list of tuples as strings. for each specific window : (day,period) like so (0,0) means: (yum aleph, 8:30-9:30)') as a string
    :param specific_days_off: list of ints as strings , for each specific day off add: day1 day2... like so -specific_days_off [0,4]
    :param lecturers: list of tuples as strings, add specific prefered lecturer to a courses lectuer  (c_id,lect lype, name)
                             like so (61132,practice,"שגיא אריאלי"), this should only be used for courses and not clusters)
    :return:
    """
    TableObjective.specific_windows = specific_windows
    TableObjective.specific_free_days = specific_days_off
    TableObjective.lecturers = lecturers
    courses, clusters = load_courses.Classes().run(courses,clusters)
    structure = courses + clusters

    TableSolution.structure = structure
    # setup end

    genetic_algo = GA(TableSolution, TableObjective, 30, 50, 0.5, 0)
    genetic_algo.start()


if __name__ == "__main__":
    args = Utils.parse()
    run(args.courses,args.cluster,args.specific_windows,args.specific_days_off,args.lecturer)
    #run(['11231','61992','11102'],[['61958', '11102'],['61963','61964','61965']],['(0,2)', '(1,2)', '(2,2)', '(3,2)', '(4,2)'],['0', '2', '4'],['(11102,practice,"דר אדר רון")'])

