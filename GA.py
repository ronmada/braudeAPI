
import datetime
import time
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y %m %d %H %M %S')
import logging
logging.basicConfig(filename='generations ' + str(st) + '.log', filemode='w',
                    format=u"%(message)s",level=logging.INFO)
import xlsxwriter
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
        self.workbook = xlsxwriter.Workbook('lessons.xlsx')
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

        self.workbook.close()
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
        logging.info('amount of crossovers = '+str(replacment_counter))
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

        worksheet = self.workbook.add_worksheet(str(len(self.fitness_history)))
        fitness_scores=[]
        logging.info('Generation #'+str(len(self.fitness_history)))
        for solution in self.curent_generation:
            solution.score = solution.objective.evaluation()


        self.curent_generation.sort(key=lambda x: x.score)
        i = 0
        for solution in self.curent_generation:
            fitness_scores.append(solution.score)
            logging.info(str(solution.objective.string_fitness_paramenters()).encode(encoding='UTF-8'))
            print(str(solution.objective.string_fitness_paramenters()))
            solution.ecxel_table(i,worksheet)
            i+=14
        fitness_scores.sort()
        self.fitness_history.append(fitness_scores)
        print (self.fitness_history)


if __name__ == "__main__":

    logging.info('GA')


    # setup start
    args = Utils.parse()
    TableObjective.specific_windows = args.specific_windows
    TableObjective.specific_free_days = args.specific_days_off
    TableObjective.lecturers = args.lecturer
    courses, clusters = load_courses.Classes().run(args)
    structure = courses + clusters

    TableSolution.structure = structure
    # setup end


    genetic_algo = GA(TableSolution, TableObjective, 30, 50, 0.5, 0)
    genetic_algo.start()
