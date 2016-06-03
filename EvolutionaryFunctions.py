# -*- coding: utf-8 -*-
"""
Created on Fri May 13 10:56:11 2016

@author: albertofasian
"""

import ProjectClasses as pc
import itertools as it
import random as rnd
import BioNetworkBuilder as bnb

###############################################################################
#FITNESS TRUTH TABLE
class ftt:
    #inputs and outputs have to be lists of strings, behaviour must be a tuple
    def __init__(self, inputs, outputs, behav):
        #is composed of a list containing the nodes we need to monitor
        self.monitored = [inputs, outputs]
        #a tuple describing the desired behaviour
        self.behaviour = behav
        #and a truth table to represent the combinations of inputs
        self.input_combs = list(it.product([0,1], repeat=len(self.monitored[0])))


#EXAMPLE
MyFtt = ftt(['Input1','Input2'],['Output1'],(0,0,0,1))

###############################################################################
#GENERATOR FUNCTION
#create a list containing a single network instance
#a generator function has the following arguments:
#   -random
#   -args
#NOTE: n_inputs, n_outputs,n_mechanism and max_inputs cannot be specified as parameters
def EC_generate(random, args):
    return [pc.network(2, 1, 1, 3)]


###############################################################################
#EVALUATOR FUNCTION
#assigns the candidates a score according to a fitness truth table (ftt)
#NOTE: for now this function is designed for single output monitoring only
#an evaluator function has the following arguments:
#   -candidates
#   -random
#   -args



#NOTE: ftt cannot be specified as parameter, so I have to use an object declared outside the function called MyFtt
def EC_fitness(candidates, args):
    scores = []
    for candidate in candidates:
        #find the positions of monitored inputs and outputs in NetworkElements
        monitored_inputs_pos = [candidate[0].ElementsNames.index(i) for i in MyFtt.monitored[0]]
        monitored_outputs_pos = [candidate[0].ElementsNames.index(i) for i in MyFtt.monitored[1]]
        total_score = 0
        #for each status (every element of the status_list)
        for i in candidate[0].status_list:
            #build a tuple with the value of the status' monitored inputs...
            tmp = tuple([i[x] for x in monitored_inputs_pos])
            #...and compare it with the inputs_comb of the ftt to find the corresponding behaviour
            expected_behaviour = MyFtt.input_combs.index(tmp)
            #find the output value(s) of the corresponding behaviour
            expected_value = MyFtt.behaviour[expected_behaviour]
            #print("expected value is: " + str(expected_value))  #debug
            #check how many elements of the loop have such value(s)
            trajectory = candidate[0].simulate(i)
            counter = 0
            for j in trajectory[1]:
                if (j[monitored_outputs_pos[0]] == expected_value):
                    counter += 1
            #print trajectory[1] #debug
            #assign a score accordingly
            state_score = float(counter) / len(trajectory[1])
            #and the score of the status to the total
            total_score += state_score
        relative_score = total_score / len(candidate[0].status_list)
        scores.append(relative_score)
        candidate[0].fitness = relative_score
    return(scores)


###############################################################################
#VARIATOR FUNCTION
def EC_variate(random, candidates, args):
    #variated_candidates = []
    for candidate in candidates:
        #if the candidate's fitness is not 1
        if (candidate[0].fitness < 1):
            options = {0 : candidate[0].new_hcf,
                   1 : candidate[0].rewire_edge,
                   2 : candidate[0].remove_input,
                   3 : candidate[0].add_input}
            #randomly select one of the possible variation methods
            variator = rnd.randint(0, 3)
            print ("variator is: " + str(variator))
            #randomly select a node, but not an input
            node = rnd.randint(candidate[0].n_inputs, candidate[0].NtwLen) - 1
            print ("node is: " + str(node))
            #call one of the methods on one of the nodes
            options[variator](node)
    return candidates
    

###############################################################################
#POPULATION SORTER
def EC_sort_fitness(final_pop):
    newlist = sorted(final_pop, key = lambda x: x.fitness, reverse=True)
    return newlist


#EXAMPLE
#CandidateTest = pc.network(2,1,4,3)
#print EC_fitness(CandidateTest, AndFtt)
#CandidateTest.print_ntw()

print '-----------------------------------------------------------------------'

'''
while(True):
    CandidateTest = pc.network(2,1,3,3)
    tmp = EC_fitness(CandidateTest, AndFtt)
    if (tmp == 1):
        CandidateTest.print_ntw()
        break

BioResult = bnb.BioNetwork(CandidateTest)
BioResult.expand_network()
BioResult.bionetwork_graph('AND_tests','test1')


for i in range(10):
    EC_variate(CandidateTest)
    CandidateTest.print_ntw()
'''

candtest = [[pc.network(2,1,3,3)]]
candtest[0][0].print_ntw()
print '...'
EC_variate(0,candtest,0)
candtest[0][0].print_ntw()
print '...'
EC_fitness(candtest,0)
