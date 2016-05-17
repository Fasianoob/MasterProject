# -*- coding: utf-8 -*-
"""
Created on Fri May 13 10:56:11 2016

@author: albertofasian
"""

import ProjectClasses as pc
import itertools as it
import random

#GENERATOR FUNCTION
#create a list containing a defined number of network instances

def EC_generate(population, inputs, outputs, mechanisms, max_inputs):
    return [pc.network(inputs, outputs, mechanisms,
                       max_inputs) for i in range(population)]


#FITNESS FUNCTION
#assigns the candidate a score according to a fitness truth table (ftt)
#NOTE: for now this function is designed for single output monitoring only
def EC_fitness(candidate,ftt):
    #find the positions of monitored inputs and outputs in NetworkElements
    monitored_inputs_pos = [candidate.ElementsNames.index(i) for i in ftt.monitored[0]]
    monitored_outputs_pos = [candidate.ElementsNames.index(i) for i in ftt.monitored[1]]
    total_score = 0
    #for each status (every element of the status_list)
    for i in candidate.status_list:
        #build a tuple with the value of the status' monitored inputs...
        tmp = tuple([i[x] for x in monitored_inputs_pos])
        #...and compare it with the inputs_comb of the ftt to find the corresponding behaviour
        expected_behaviour = ftt.input_combs.index(tmp)
        #find the output value(s) of the corresponding behaviour
        expected_value = ftt.behaviour[expected_behaviour]
        print("expected value is: " + str(expected_value))  #debug
        #check how many elements of the loop have such value(s)
        trajectory = candidate.simulate(i)
        counter = 0
        for j in trajectory[1]:
            if (j[monitored_outputs_pos[0]] == expected_value):
                counter += 1
        print trajectory[1] #debug
        #assign a score accordingly
        state_score = float(counter) / len(trajectory[1])
        #and the score of the status to the total
        total_score += state_score
    relative_score = total_score / len(candidate.status_list)
    return(relative_score)

#VARIATOR FUNCTION
def EC_variate(candidate):
    options = {0 : candidate.new_hcf,
           1 : candidate.rewire_edge,
           2 : candidate.remove_input,
           3 : candidate.add_input,
}
    #randomly select one of the possible variation methods
    variator = random.randint(0, 3)
    print ("variator is: " + str(variator))
    #randomly select a node, but not an input
    node = random.randint(candidate.n_inputs, candidate.NtwLen) - 1
    print ("node is: " + str(node))
    #call one of the methods on one of the nodes
    options[variator](node)
    

#FITNESS TRUTH TABLE
class ftt:
    #inputs and outputs have to be lists of strings, behaviour must be a tuple
    def __init__(self, inputs, outputs, behav):
        #is composed of a list containing the nodes we need do monitor
        self.monitored = [inputs, outputs]
        #a tuple describing the desired behaviour
        self.behaviour = behav
        #and a truth table to represent the combinations of inputs
        self.input_combs = list(it.product([0,1], repeat=len(self.monitored[0])))


#EXAMPLE
AndFtt = ftt(['Input1','Input2'],['Output1'],(0,0,0,1))

#EXAMPLE
CandidateTest = pc.network(2,1,4,3)
print EC_fitness(CandidateTest, AndFtt)
CandidateTest.print_ntw()

'''
while(True):
    CandidateTest = pc.network(2,1,3,3)
    tmp = EC_fitness(CandidateTest, AndFtt)
    if (tmp == 1):
        CandidateTest.print_ntw()
        break
'''

for i in range(10):
    EC_variate(CandidateTest)
    CandidateTest.print_ntw()




