# -*- coding: utf-8 -*-
"""
Created on Fri May 13 10:56:11 2016

@author: albertofasian
"""

import ProjectClassesRef as pc
import itertools as it
import random as rnd
#import BioNetworkBuilder as bnb

###############################################################################
#FITNESS TRUTH TABLE
class ftt:
    #inputs and outputs have to be lists of STRINGS, behaviour must be a TUPLE containing LISTS
    def __init__(self, inputs, outputs, behav):
        self.inputs = inputs
        self.outputs = outputs
        #a tuple describing the desired behaviour
        self.behaviour = behav
        #and a truth table to represent the combinations of inputs
        self.input_combs = list(it.product([0,1], repeat=len(self.inputs)))


#EXAMPLE
MyFtt = ftt(['Input1','Input2'],['Output1'],([0],[0],[0],[1]))

###############################################################################
#GENERATOR FUNCTION
#create a list containing a single network instance
#a generator function has the following arguments:
#   -random
#   -args
#NOTE: n_inputs, n_outputs,n_mechanism and max_inputs cannot be specified as parameters
def EC_generator(random, args, ntw_parameters):
    #return [pc.network(2, 1, 1, 3)]
    return [pc.network(ntw_parameters[0],ntw_parameters[1],ntw_parameters[2],ntw_parameters[3])]

###############################################################################
#EVALUATOR FUNCTION
#assigns the candidates a score according to a fitness truth table (ftt)
#NOTE: for now this function is designed for single output monitoring only
#an evaluator function has the following arguments:
#   -candidates
#   -random
#   -args
#NOTE: ftt cannot be specified as parameter, so I have to use an object declared outside the function called MyFtt or pass the ftt inside args
def EC_fitness(candidates, random, args, circuit_ftt):
    results = []
    for candidate in candidates:
        results.append(EC_evaluator(candidate[0], circuit_ftt))
    return results

#NOTE: when passing the candidate to this function, remember that every single candidate is contained in a list
def EC_evaluator(candidate, ftt):
    #find the references of the monitored inputs
    monitored_input_refs = []
    for i in ftt.inputs:
        for j in candidate.NetworkElements:
            if (i == j.name):
                #print(j.name)   #DEBUG
                monitored_input_refs.append(j)
    #find the references of the monitored outputs
    monitored_output_refs = []
    for i in ftt.outputs:
        for j in candidate.NetworkElements:
            if (i == j.name):
                #print(j.name)   #DEBUG
                monitored_output_refs.append(j)
    out_scores = [0 for x in monitored_output_refs]
    #for every status
    for i in candidate.status_list:
        trajectory = candidate.simulate(i)
        #for every monitored output
        for j in range(len(monitored_output_refs)):
            #build a tuple with the value of the status' monitored inputs
            tmp = tuple([i[candidate.NetworkElements.index(x)] for x in monitored_input_refs])
            #compare it with the input_combs of the ftt to find the corresponding behaviour
            expected_behaviour = ftt.behaviour[ftt.input_combs.index(tmp)][j]
            loop_counter = 0
            #for every element of the loop
            for k in trajectory[1]:
                #if the monitored outputs are equal to the respective behaviours, then increase the counter
                if (k[candidate.NetworkElements.index(monitored_output_refs[j])] == expected_behaviour):
                    loop_counter += 1
            #check how many elements of the loop have such value(s)
            out_scores[j] += float(loop_counter) / len(trajectory[1])
    out_scores = [(x/len(candidate.status_list)) for x in out_scores]
    return(sum(out_scores) / len(out_scores))

###############################################################################
#VARIATOR FUNCTION
def EC_variator(random, candidates, args):
    #variated_candidates = []
    for candidate in candidates:
        #if the candidate's fitness is not 1
        if (candidate[0].fitness < 1):
            options = {0 : candidate[0].new_hcf,
                   1 : candidate[0].shuffle_hierarchy,
                   2 : candidate[0].alter_can_behaviour,
                   3 : candidate[0].rewire_edge,
                   4 : candidate[0].remove_input,
                   5 : candidate[0].add_input,
                   6 : candidate[0].add_node,
                   7 : candidate[0].remove_node}
            #randomly select one of the possible variation methods
            variator = rnd.randint(0, 7)
            print ("variator is: " + str(variator))
            #randomly select a node, but not an input
            node = rnd.choice(candidate[0].NetworkElements[candidate[0].n_inputs:])
            print ("node is: " + node.name)
            #call one of the methods on one of the nodes
            options[variator](node)
    return candidates

###############################################################################
#POPULATION SORTERS

#sort the population exclusively by fitness value
def EC_sort_fitness(final_pop):
    newlist = sorted(final_pop, key = lambda x: x.fitness, reverse=True)
    return newlist

#sort population according to fitness and network size
def EC_sort_fitness_size(final_pop):
    #NOTE: invert NtwLen to sort them in increasing order
    newlist = sorted(final_pop, key = lambda x: (x.fitness, -1*x.candidate[0].NtwLen), reverse=True)
    return newlist

#EXAMPLE
#CandidateTest = pc.network(2,1,4,3)
#print EC_fitness(CandidateTest, AndFtt)
#CandidateTest.print_ntw()

print '-----------------------------------------------------------------------'

'''
while(True):
    CandidateTest = pc.network(2,1,3,3)
    tmp = EC_evaluator(CandidateTest,MyFtt)
    if (tmp == 1):
        CandidateTest.print_ntw()
        break
'''

#BioResult = bnb.BioNetwork(CandidateTest)
#BioResult.expand_network()
#BioResult.bionetwork_graph('AND_tests','test1')

'''
candtest = [[pc.network(2,1,3,3)]]
candtest[0][0].print_ntw()
print '...'
EC_variate(0,candtest,0)
candtest[0][0].print_ntw()
print '...'
print EC_evaluator(candtest[0][0],MyFtt)
'''









