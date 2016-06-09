# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 16:26:47 2016

@author: albertofasian
"""

import inspyred
import random as rnd
import EvolutionaryFunctionsRef as ef
#import ProjectClasses as pc
import functools as ft

#FITNESS TABLE
MyFtt = ef.ftt(['Input1','Input2'],['Output1'],([0],[0],[0],[1]))
MyNtwParams = (2,1,10,3)

MyAlgorithm = inspyred.ec.GA(None)
MyAlgorithm.selector = inspyred.ec.selectors.tournament_selection
#MyAlgorithm.variator = [inspyred.ec.variators.uniform_crossover, variate_candidates]
MyAlgorithm.variator = [ef.EC_variator]
#default_replacer makes no replacement at all
MyAlgorithm.replacer = inspyred.ec.replacers.truncation_replacement

random_seed = rnd.randint

partial_generator = ft.partial(ef.EC_generator, random=random_seed, args=0, ntw_parameters=MyNtwParams)
partial_evaluator = ft.partial(ef.EC_fitness, random=random_seed, args=0, circuit_ftt=MyFtt)

final_pop = MyAlgorithm.evolve(generator=partial_generator,
                         evaluator=partial_evaluator,
                         pop_size=100,
                         max_evaluations=100,
                         num_selected=2)

sorted_pop = ef.EC_sort_fitness(final_pop)

#clear networks before sorting them
for i in final_pop:
    i.candidate[0].clear()

size_sorted_pop = ef.EC_sort_fitness_size(final_pop)

#to get a network from individual
#size_sorted_pop[0].candidate[0].print_ntw()

for i in size_sorted_pop:
    print('fitness: '+str(i.fitness)+' - size: '+str(i.candidate[0].NtwLen))