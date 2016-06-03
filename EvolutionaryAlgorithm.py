# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 16:26:47 2016

@author: albertofasian
"""

import inspyred
#import random as rnd
import EvolutionaryFunctions as ef
#import ProjectClasses as pc

#FITNESS TABLE
MyFtt = ef.ftt(['Input1','Input2'],['Output1'],(0,0,0,1))

MyAlgorithm = inspyred.ec.GA(None)
MyAlgorithm.selector = inspyred.ec.selectors.tournament_selection
#MyAlgorithm.variator = [inspyred.ec.variators.uniform_crossover, variate_candidates]
MyAlgorithm.variator = [ef.EC_variate]
#default_replacer makes no replacement at all
MyAlgorithm.replacer = inspyred.ec.replacers.truncation_replacement

final_pop = MyAlgorithm.evolve(generator=ef.EC_generate,
                         evaluator=ef.EC_fitness,
                         pop_size=100,
                         max_evaluations=500,
                         num_selected=2)

sorted_pop = ef.EC_sort_fitness(final_pop)