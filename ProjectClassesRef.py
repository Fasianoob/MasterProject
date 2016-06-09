# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 12:37:05 2016

@author: albertofasian
"""

import itertools as it
import numpy as np
import graphviz as gv
import functools as ft
import random

class node:
    def __init__(self, name, is_input=False, is_output=False):
        self.name = name
        self.input_refs = []
        self.hierarchy = []
        self.function = []
        self.is_input = is_input
        self.is_output = is_output
        self.value_t = 0
        self.value_tp1 = 0
    
    def __del__(self):
        #print('Node ' + self.name + ' destroyed')   #DEBUG
        pass
        
    def add_input_ref(self, input_ref):
        self.input_refs.append(input_ref)
    
    def create_tt(self):
        self.tt = list(it.product([0,1], repeat=len(self.input_refs)))

    def generate_hcf(self):
        #if node has no inputs, do nothing
        if (not self.input_refs):
            return
        #create a 'hierarchy' list containing a list for each input_ref
        #hierarchy contains the input_ref in decreasing canalyzing order
        self.hierarchy = [[i] for i in self.input_refs]
        for i in self.hierarchy:
            #sample random canalyzing and output values and append them to the list containing the input reference
            i.append(tuple([random.randint(0, 1) for j in range(2)]))
        #shuffle the hierarchy list
        random.shuffle(self.hierarchy)
        #populate the hcf
        self.populate_hcf(self.hierarchy)
    
    #NOTE: run this function again every time you alter the hierarchy
    def populate_hcf(self, hierarchy):
        #create the truth table for the node
        self.create_tt()
        #create a list filled with "-"
        hcf = ['-' for x in self.tt]
        #populate the function
        for i in range(len(self.hierarchy)):
            for j in range(len(self.tt)):
                if (self.tt[j][i] == self.hierarchy[i][1][0] and hcf[j]=='-'):
                    hcf[j] = self.hierarchy[i][1][1]
        #the last value has to be complementary to the last input
        if (self.hierarchy[-1][1][1] == 0):
            hcf[hcf.index('-')] = 1
        else:
            hcf[hcf.index('-')] = 0
        self.function = hcf
    
    def update(self):
        #if the node has no input, then return value_t
        if (not self.hierarchy):
            return self.value_t
        #grab the input values in hierarchical order
        in_values = tuple([i[0].value_t for i in self.hierarchy])
        #find the match in tt
        self.value_tp1 = self.function[self.tt.index(in_values)]
        return self.value_tp1

class network:
    def __init__(self, n_inputs, n_outputs, max_n_mechanisms, max_inputs):
        self.n_inputs = n_inputs
        #the minimum number can actually be 0
        self.n_mechanisms = random.randint(0,max_n_mechanisms)
        self.max_n_mechanisms = max_n_mechanisms
        self.n_outputs = n_outputs
        self.NtwLen = n_inputs + self.n_mechanisms + n_outputs
        self.max_inputs = max_inputs
        self.fitness = 0
        #NOTE: if you add or remove a node, then you have to update some of these attributes
        
        #generate a given number of node instances
        self.Inputs = [node("Input"+str(i+1), is_input=True) for i in range(n_inputs)]
        self.Mechanisms = [node("Node"+str(i+1)) for i in range(self.n_mechanisms)]
        self.Outputs = [node("Output"+str(i+1), is_output=True) for i in range(n_outputs)]
        #and collect them into a network list
        self.NetworkElements = self.Inputs + self.Mechanisms + self.Outputs
        self.ElementsNames = [i.name for i in self.NetworkElements]
        
        #generate a list of inputs for Mechanisms and Outputs elements
        for i in self.NetworkElements[self.n_inputs : ]:
            #generate a random number from 0 (or 1?) to max_inputs
            #calculate the number of nodes available for connections
            InputNumber = min((random.randint(1,self.max_inputs)),(self.n_inputs+self.n_mechanisms))
            #create the input_refs list
            #until all inputs have been assigned
            while (len(i.input_refs) < InputNumber):
                #randomly pick a node ref from Inputs or Mechanisms. Outputs can't be inputs
                tmp = random.choice(self.NetworkElements[0 : -self.n_outputs])
                #if tmp is not already in the list, then append
                if (tmp not in i.input_refs):
                    i.add_input_ref(tmp)
            
            #generate a Function for Mechanisms and Outputs elements
            i.generate_hcf()
        
        #generate status list
        self.generate_status_list()
        #print('end of init')    #DEBUG
    
    def generate_status_list(self):
        self.status_list = list(it.product([0,1], repeat=self.NtwLen))
        #NOTE: if you add or remove a node, then you have to update the status list
        
    def print_ntw(self):
        for i in self.NetworkElements:
            print(i.name + '--->')
            if (not i.hierarchy):
                print('has 0 inputs:')
                continue
            print("has "+str(len(i.hierarchy))+" inputs:")
            for k in i.hierarchy:
                print(k[0].name)
            print(i.function)

    def adj_mat(self):
        AdjMat = np.zeros((self.NtwLen,self.NtwLen), dtype=np.bool)
        for i in range(self.NtwLen):
            if (self.NetworkElements[i].input_refs):
                for j in self.NetworkElements[i].input_refs:
                    AdjMat[self.NetworkElements.index(j),i] = True
        return AdjMat

    def update_status(self, status_t):
        #set each node to their value_t
        for i in range(len(self.NetworkElements)):
            self.NetworkElements[i].value_t = status_t[i]
        #fill status_tp1 with the values of the updated nodes
        status_tp1 = tuple([i.update() for i in self.NetworkElements])
        return status_tp1

    def transition_table(self): #RELIC
        tp1 = []
        for i in self.status_list:
            tp1.append(self.update_status(i))
        return(tp1)

    def simulate(self, initial):
        trajectory = [initial]
        current = initial
        loop = 0
        while (True):
            tmp = self.update_status(current)
            if (tmp not in trajectory):
                trajectory.append(tmp)
                current = tmp
            else:
                loop = trajectory.index(tmp)
                break
        return trajectory[:loop], trajectory[loop:]

###############################################################################

#GRAPH GENERATORS

    def graph(self, names, edges, folder_name, file_name):
        #graph = ft.partial(gv.Graph, format='svg')
        digraph = ft.partial(gv.Digraph, format='svg')
        
        def add_nodes(graph, nodes):
            for n in nodes:
                if isinstance(n, tuple):
                    graph.node(n[0], **n[1])
                else:
                    graph.node(n)
            return graph
        
        def add_edges(graph, edges):
            for e in edges:
                if isinstance(e[0], tuple):
                    graph.edge(*e[0], **e[1])
                else:
                    graph.edge(*e)
            return graph
        
        add_edges(
            add_nodes(digraph(), names),
            edges
        ).render(folder_name + "/" + file_name)

    def network_graph(self, folder_name, file_name):
        #so....I need a list of all the names
        names = [i.name for i in self.NetworkElements]
        #...and a list of tuples for each edge
        adj = self.adj_mat()
        edges = []
        for i in range(self.NtwLen):
            for j in range(self.NtwLen):
                if (adj[i,j]):
                    edges.append(tuple([self.NetworkElements[i].name,self.NetworkElements[j].name]))
        self.graph(names, edges, folder_name, file_name)

    def transition_diagram(self, folder_name, file_name):
        names = [(str(i).strip('()')).replace(',', '') for i in self.status_list]
        
        tp1 = [(str(i).strip('()')).replace(',', '') for i in self.transition_table()]
        #print(names)    #debug
        edges = [tuple([names[i],tp1[i]]) for i in range(len(names))]
        self.graph(names, edges, folder_name, file_name)

###############################################################################

#VARIATION OPERATORS
    
    #NOTE: make sure you are passing the node object reference as 'node' parameter

    #method to generate a complete new hcf
    def new_hcf(self, node):
        self.NetworkElements[node].generate_hcf()
    #NOTE: what about just altering canalyzing hierarchy or values?
    
    def shuffle_hierarchy(self, node):
        random.shuffle(node.hierarchy)
        #populate the hcf
        node.populate_hcf(node.hierarchy)
    
    def alter_can_behaviour(self, node):
        #select a random element of the hierarchy
        tmp = random.choice(node.hierarchy)
        print tmp
        #generate a new tuple (value,output)
        while (True):
            new = tuple([random.randint(0, 1) for j in range(2)])
            if (new != tmp[1]):
                break
        #substitute the tuple
        tmp[1] = new
        print tmp
        #run populate_hcf
        node.populate_hcf(node.hierarchy)
    
    def rewire_edge(self, node):
        #output nodes are not available for establishing inputs
        available = self.NetworkElements[0 : -self.n_outputs]
        #if node has no inputs or there are no other available inputs, do nothing
        if ((not node.input_refs) or (len(node.input_refs) == len(available))):
            return
        old = random.choice(node.input_refs)
        while (True):
            new = random.choice(available)
            if (new not in node.input_refs):
                break
        print(old.name) #DEBUG
        print(new.name) #DEBUG
        #substitute old with new both in input_refs and in hierarchy
        node.input_refs = [new if x==old else x for x in node.input_refs]
        for i in node.hierarchy:
            if (i[0] == old):
                i[0] = new
    
    #method to remove an input
    def remove_input(self, node):
        #if there are no inputs, do nothing
        if (not node.input_refs):
            return
        #randomly pick an input
        hit = random.choice(node.input_refs)
        #remove it from the list
        node.input_refs.remove(hit)
        #remove the corresponding element from hierarchy
        for i in node.hierarchy:
            if (i[0] == hit):
                node.hierarchy.remove(i)
        #run populate_hcf
        node.populate_hcf(node.hierarchy)

    #method to add an input
    def add_input(self, node):
        available = self.NetworkElements[0 : -self.n_outputs]
        #if the node has the max number of inputs or is an input or there are no more available inputs, do nothing
        if (len(node.input_refs) == self.max_inputs or node.is_input == True or len(node.input_refs) == len(available)):
            return
        while (True):
            new = random.choice(available)
            if (new not in node.input_refs):
                break
        #add the new input to the input_refs list
        node.input_refs.append(new)
        #generate value and output
        #tmp = [new,tuple([random.randint(0, 1) for j in range(2)])]
        #add the new input to the hierarchy in the last hierarchical position
        node.hierarchy.append([new,tuple([random.randint(0, 1) for j in range(2)])])
        #run populate_hcf
        node.populate_hcf(node.hierarchy)
    
    #method to add a node ('node' is unused)
    def add_node(self, node):
        #if the network has the max number of nodes already, then do nothing
        if (self.n_mechanisms == self.max_n_mechanisms):
            return
        #create a new node and add it to the NetworkElement list before the outputs
        new = node("Node"+str(self.n_mechanisms+1))
        self.NetworkElements.insert(self.n_inputs+self.n_mechanisms, new)
        #update n_mechanisms and NtwLen
        self.n_mechanisms += 1
        self.NtwLen += 1
        #create inputs for the new node
        InputNumber = min((random.randint(1,self.max_inputs)),(self.n_inputs+self.n_mechanisms))
        #create the input_refs list
        #until all inputs have been assigned
        while (len(new.input_refs) < InputNumber):
            #randomly pick a node ref from Inputs or Mechanisms. Outputs can't be inputs
            tmp = random.choice(self.NetworkElements[0 : -self.n_outputs])
            #if tmp is not already in the list, then append
            if (tmp not in new.input_refs):
                new.add_input_ref(tmp)
        #generate a Function for the new node
        new.generate_hcf()
        #update status list
        self.generate_status_list()
    
    #method to remove a node
    def remove_node(self, node):
        #if the number of Mechanisms is lower than 1, then do nothing
        if (self.n_mechanisms < 1):
            return
        #remove node reference from NetworkElements and from every input_refs
        self.NetworkElements.remove(node)
        #remove the respective element from every input_refs and hierarchy
        for i in self.NetworkElements:
            if (node in i.input_refs):
                i.input_refs.remove(node)
            for j in i.hierarchy:
                if (j[0] == node):
                    i.hierarchy.remove(j)
            #run populate_hcf()
            if (i.input_refs):
                i.populate_hcf(i.hierarchy)
            else:
                i.function = []
        #update n_mechanisms, NtwLen, Mechanisms and NetworkElements
        self.n_mechanisms -= 1
        self.NtwLen -= 1
        self.Mechanisms.remove(node)
        self.NetworkElements = self.Inputs + self.Mechanisms + self.Outputs
        #update status list
        self.generate_status_list()
        
###############################################################################

#NETWORK CLEANER
    
    def clear(self):
        #the maximum number of iteration is the number of removable nodes, that is n_mechanisms
        iterate = True
        #for i in range(len(self.n_mechanisms)):
        while (iterate == True and len(self.Mechanisms) > 0):
            #create a list for the connected nodes
            connected = []
            for j in self.NetworkElements[self.n_inputs:]:
                for k in j.input_refs:
                    if (k not in connected):
                        connected.append(k)
            #if an element of NetworkElements is not present in 'connected', then delete it
            #update n_mechanisms and NtwLen
            #optionally, you might want to change the name in the end
            for x in self.Mechanisms:
                if (x not in connected):
                    print('removing ' + x.name) #DEBUG
                    self.Mechanisms.remove(x)
                    self.NetworkElements = self.Inputs + self.Mechanisms + self.Outputs
                else:
                    iterate = False
            #NOTE: but if they are all connected, then exit the routine!!!!
            pass
        pass


#CREATE DETERMINED BOOLEAN NETWORK

class OR(network):
    def __init__(self):
        self.n_inputs = 2
        self.n_nodes = 0
        self.n_outputs = 1
        self.NtwLen = 3
        self.max_inputs = 2
        
        self.NetworkElements = [node('Input1',is_input=True), node('Input2',is_input=True), node('Output',is_output=True)]
        self.ElementsNames = [i.name for i in self.NetworkElements]
        self.status_list = list(it.product([0,1], repeat=self.NtwLen))
        
        self.NetworkElements[2].input_refs = [self.NetworkElements[0],self.NetworkElements[1]]
        self.NetworkElements[2].hierarchy = [[self.NetworkElements[0],(1,1)],[self.NetworkElements[1],(1,1)]]
        self.NetworkElements[2].populate_hcf(self.NetworkElements[2].hierarchy)

class AND(network):
    def __init__(self):
        self.n_inputs = 2
        self.n_nodes = 0
        self.n_outputs = 1
        self.NtwLen = 3
        self.max_inputs = 2
        
        self.NetworkElements = [node('Input1',is_input=True), node('Input2',is_input=True), node('Output',is_output=True)]
        self.ElementsNames = [i.name for i in self.NetworkElements]
        self.status_list = list(it.product([0,1], repeat=self.NtwLen))
        
        self.NetworkElements[2].input_refs = [self.NetworkElements[0],self.NetworkElements[1]]
        self.NetworkElements[2].hierarchy = [[self.NetworkElements[0],(0,0)],[self.NetworkElements[1],(0,0)]]
        self.NetworkElements[2].populate_hcf(self.NetworkElements[2].hierarchy)

class LATCH(network):
    def __init__(self):
        self.n_inputs = 2
        self.n_nodes = 2
        self.n_outputs = 0
        self.NtwLen = 4
        self.max_inputs = 2
        
        self.NetworkElements = [node('Reset',is_input=True), node('Set',is_input=True), node('Q'), node('NOT Q')]
        self.ElementsNames = [i.name for i in self.NetworkElements]
        self.status_list = list(it.product([0,1], repeat=self.NtwLen))
        
        self.NetworkElements[2].input_refs = [self.NetworkElements[0],self.NetworkElements[3]]
        self.NetworkElements[2].hierarchy = [[self.NetworkElements[0],(1,0)],[self.NetworkElements[3],(1,0)]]
        self.NetworkElements[2].populate_hcf(self.NetworkElements[2].hierarchy)
        
        self.NetworkElements[3].input_refs = [self.NetworkElements[1],self.NetworkElements[2]]
        self.NetworkElements[3].hierarchy = [[self.NetworkElements[1],(1,0)],[self.NetworkElements[2],(1,0)]]
        self.NetworkElements[3].populate_hcf(self.NetworkElements[3].hierarchy)


##################################

#TEST
#print '----------------------------'
#ntwtest = network(1,1,4,3)
#ntwtest.print_ntw()
#print ntwtest.adj_mat()












