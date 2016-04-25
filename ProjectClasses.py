
import itertools as it

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
        
    def set_inputs(self, a=[]):
        self.inputs = a
        self.tt = list(it.product([0,1], repeat=len(self.inputs)))
    
    def set_function(self, a=[]):
        self.function = a

    def set_inputs_pos(self, network):
        for i in self.inputs:
            self.inputs_pos.append(network.index(i))

    def update1(self, in_values=()):     #parameter is a tuple!!!
        #exploit the correspondence between tt and self.function
        return(self.function[self.tt.index(in_values)])

