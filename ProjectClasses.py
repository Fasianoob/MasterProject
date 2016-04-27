
import itertools as it
import numpy as np
import graphviz as gv
import random

class node:
    def __init__(self, name):
        self.name = name
        #are the followings needed?
        self.inputs = []
        self.inputs_pos = []
        self.function = []

    def set_info(self, a=[], b=[], c=[]):
        self.set_inputs(a)
        self.set_function(b)
        self.set_inputs_pos(c)
        
    #this is not actually used    
    def set_inputs(self, a=[]):
        self.inputs = a
        self.tt = list(it.product([0,1], repeat=len(self.inputs)))
    
    def set_function(self, a=[]):
        self.function = a

    def set_inputs_pos(self, network):
        for i in self.inputs:
            self.inputs_pos.append(network.index(i))
            
    #the following is used in the random ntw generator
    def set_inputs_pos1(self, a=[]):
        self.inputs_pos = a
        self.tt = list(it.product([0,1], repeat=len(self.inputs_pos)))

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
        
        #collect them into a network list
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
            self.NetworkElements[i].set_inputs_pos1(tmp_input_pos)
            #generate a Function list for Nodes and Outputs elements
            tmp_b_fun = [random.randint(0, 1) for j in range(2**InputNumber)]
            #WARNING: what happens if there was the possibility of 0 inputs?
            self.NetworkElements[i].set_function(tmp_b_fun)
        
        #WARNING(?): I might come up with "dead end" nodes or inputs
        
        self.status_list = list(it.product([0,1], repeat=self.NtwLen))
        
    def print_ntw(self):
        for i in self.NetworkElements:
            print(i.name + "--->")
            print("has "+str(len(i.inputs_pos))+" inputs:")
            for k in i.inputs_pos:
                print(self.NetworkElements[k].name)
            print(i.function)

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

    #write a function to draw a graph using graphviz






