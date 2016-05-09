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
    def __init__(self, name):
        self.name = name
        #is the followings needed?
        self.inputs = []
        self.inputs_pos = []
        self.function = []
    
    def set_function(self, a=[]):
        self.function = a
            
    def set_inputs_pos(self, a=[]):
        self.inputs_pos = a
        self.tt = list(it.product([0,1], repeat=len(self.inputs_pos)))

    def generate_hcf(self, inputs_pos):
        #create a list filled with "-"
        #WARNING: nodes with no inputs will have a non empty function
        hcf = ['-' for x in range(2**len(inputs_pos))]
        #hierarchical order: create a list and randomize it
        hierarchy = range(len(inputs_pos))
        random.shuffle(hierarchy)
        #sample random canalyzing and output values
        CanValues = [random.randint(0, 1) for j in range(len(inputs_pos))]
        OutValues = [random.randint(0, 1) for j in range(len(inputs_pos))]
        for i in hierarchy:
            for j in range(len(self.tt)):
                if (self.tt[j][i]==CanValues[i] and hcf[j]=='-'):
                    hcf[j] = OutValues[i]
        #now the last value. should I assign it randomly?
        for i in range(len(hcf)):
            if (hcf[i] == '-'):
                hcf[i] = random.randint(0,1)
        self.function = hcf

    def update1(self, in_values=()):     #parameter is a tuple!!!
        #exploit the correspondence between tt and self.function
        return(self.function[self.tt.index(in_values)])

class network:
    def __init__(self, n_inputs, max_n_nodes, n_outputs, max_inputs):
        self.n_inputs = n_inputs
        self.n_nodes = random.randint(1,max_n_nodes)
        self.n_outputs = n_outputs
        self.NtwLen = n_inputs + self.n_nodes + n_outputs
        
        #generate a given number of node instances
        Inputs = [node("Input"+str(i+1)) for i in range(n_inputs)]
        Nodes = [node("Node"+str(i+1)) for i in range(self.n_nodes)]
        Outputs = [node("Output"+str(i+1)) for i in range(n_outputs)]
        #and collect them into a network list
        self.NetworkElements = Inputs + Nodes + Outputs
        
        #generate a list of inputs for Nodes and Outputs elements
        for i in range(n_inputs,self.NtwLen):
            #generate a random number from 0 (or 1?) to max_inputs
            #calculate the number of nodes available for connections
            if ("Node" in self.NetworkElements[i].name):
                InputNumber = min((random.randint(1,max_inputs)),(n_inputs+self.n_nodes))
            else:
                InputNumber = min((random.randint(1,max_inputs)),(self.n_nodes))
            #at this stage I can easily create the input_pos list
            tmp_input_pos = []
            #until all inputs have been assigned
            while (len(tmp_input_pos) < InputNumber):
                #randomly pick a node from Inputs or Nodes. Outputs can't be inputs
                #Outputs should't be allowed to have Inputs elements as inputs??
                #if Node: pick a random node from Inputs or Nodes
                if ("Node" in self.NetworkElements[i].name):
                    tmp = random.randint(0,self.NtwLen - n_outputs - 1)
                #if Output: pick a random node from Nodes
                else:
                    tmp = random.randint(n_inputs,self.NtwLen - n_outputs - 1)
                #so...if randint is not already in the list...append
                if (tmp not in tmp_input_pos):
                    tmp_input_pos.append(tmp)
            #set the inputs_pos attribute
            self.NetworkElements[i].set_inputs_pos(tmp_input_pos)
            #generate a Function for Nodes and Outputs elements
            self.NetworkElements[i].generate_hcf(tmp_input_pos)        
        #WARNING(?): I might come up with "dead end" nodes or inputs
        
        self.status_list = list(it.product([0,1], repeat=self.NtwLen))
        
    def print_ntw(self):
        for i in self.NetworkElements:
            print(i.name + "--->")
            print("has "+str(len(i.inputs_pos))+" inputs:")
            for k in i.inputs_pos:
                print(self.NetworkElements[k].name)
            print(i.function)

    #why don't you run this in __init__???
    def adj_mat(self):
        AdjMat = np.zeros((self.NtwLen,self.NtwLen), dtype=np.bool)
        for i in range(self.NtwLen):
            if (self.NetworkElements[i].inputs_pos):
                for j in self.NetworkElements[i].inputs_pos:
                    AdjMat[j,i] = True
        return AdjMat

    def personal_inputs(self, node, status):
        return(tuple([status[i] for i in node.inputs_pos]))

    def update_status(self, status):
        sp1 = []
        #for each node in the network
        for i in range(self.NtwLen):
            #if the node has inputs, then...
            if (self.NetworkElements[i].inputs_pos):
                #calculate its next value according to its personal inputs
                sp1.append(self.NetworkElements[i].update1(self.personal_inputs(self.NetworkElements[i],status)))
            #if the node has no inputs, then...
            else:
                sp1.append(status[i])
        return(tuple(sp1))

    def transition_table(self):
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
            #do I really need to check EVERY element in trajectory?
            if (tmp not in trajectory):
                trajectory.append(tmp)
                current = tmp
            else:
                loop = trajectory.index(tmp)
                break
        #print(trajectory)
        #return(trajectory)
        return trajectory[:loop], trajectory[loop:]

###############################################################################

    #write a function to draw a graph using graphviz

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











