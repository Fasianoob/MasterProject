# -*- coding: utf-8 -*-
"""
Created on Wed May 18 10:15:00 2016

@author: albertofasian
"""

import ProjectClasses as pc
import graphviz as gv
import functools as ft

class BioNode:
    def __init__(self, name, typology, flag=True):
        self.name = name
        # "protein", "gene", "binding_site", "promoter", "const_promoter", "RNA_pol"...
        self.typology = typology
        self.inputs = []
        #flag is used to revert the regulation of further interactions
        self.flag = flag
    
    def add_interaction(self, interaction):
        self.inputs.append(interaction)


class BioInteraction:
    def __init__(self, regulator, predicate, regulation=True, priority=0):
        self.regulator = regulator      #reference to BioNode
        self.regulation = regulation    #activator or inhibitor
        self.priority = priority        #affinity order
        # "binds", "has_binding_site", "activates", "inhibits", "codifies"...
        self.predicate = predicate      


class BioNetwork():
    #INITIALIZATION
    def __init__(self, BoolNetwork):
        #acquire the list of elements from the Boolean network
        self.BoolNetworkElements = BoolNetwork.NetworkElements
        #create a list containing references of "protein" BioNode for each element of BoolNetworkElements
        self.BioNetworkElements = [BioNode(i.name, 'protein') for i in self.BoolNetworkElements]
        #add a node for RNA_pol
        self.BioNetworkElements.append(BioNode('RNA_polimerase','RNA_polimerase'))
        #store a ref to the RNA_pol BioNode for further use
        self.PolRef = self.BioNetworkElements[-1]
        #store the number of inputs to set the counter
        self.n_inputs = BoolNetwork.n_inputs
    
    ###########################################################################
    #MODULE BUILDER FUNCTIONS
    #all these functions add a portion of network and return the docking site for the following piece of network
    #the first parameter is the current docking site, the second parameter is a reference to the input protein
    
    def build_primer_generic(self, BioNodeRef):
        #create a new BioNode for the gene codifying the protein
        new = BioNode('Gene_' + BioNodeRef.name, 'gene')
        #add it to the BioNode list
        self.BioNetworkElements.append(new)
        #establish an interaction named "codifies"
        BioNodeRef.add_interaction(BioInteraction(new,'codifies'))
        #create a new BioNode for the promoter of the gene (ref is "docking")
        docking = BioNode('Promoter_' + BioNodeRef.name, 'promoter')
        #add it to the BioNode list
        self.BioNetworkElements.append(docking)
        #establish an interaction named "of"
        new.add_interaction(BioInteraction(docking, 'of'))
        return docking
    
    def build_00(self, BioNodeRef, current, counter):
        #this is a temporary solution for the termination
        if (BioNodeRef == None):
            print BioNodeRef    #debug
            return
        #create a binding site BioNode belonging to the current input protein (ref is "docking")
        docking = BioNode(current.name + ' (' + str(counter) + ')', 'binding_site')
        #add it to the BioNetworkElements list
        self.BioNetworkElements.append(docking)
        #establish an interaction between the BS and the protein to which it belongs
        docking.add_interaction(BioInteraction(current, 'has_binding_site'))
        #establish an interaction between docking and BioNodeRef whose regulation depends on the flag on the latter
        #the priority of the interaction has to be set:
        #   - equal to the number of inputs of BioNodeRef if BioNodeRef is a promoter
        #   - equal to the number of inputs of BioNodeRef - 1 otherwise (because one interaction is with the whole protein)
        BioNodeRef.add_interaction(BioInteraction(docking, 'binds', BioNodeRef.flag,
            priority = len(BioNodeRef.inputs) if BioNodeRef.typology=='promoter' else len(BioNodeRef.inputs) - 1))
        #the flag of the docking has to be True (this is obtained by default)
        #if the BioNodeRef is a promoter, then docking has to establish an interaction with RNA-pol as well
        if (BioNodeRef.typology == 'promoter'):
            self.PolRef.add_interaction(BioInteraction(docking, 'binds'))
         #return the docking site
        return docking
    
    def build_01(self, BioNodeRef, current, counter):
        #this is a temporary solution for the termination
        if (BioNodeRef == None):
            return
        #create a binding site BioNode belonging to the current input protein (ref is "docking")
        #set the flag = False to revert the following interaction on this BioNode
        docking = BioNode(current.name + ' (' + str(counter) + ')', 'binding_site', flag=False)
        #add it to the BioNetworkElements list
        self.BioNetworkElements.append(docking)
        #establish an interaction between the BS and the protein to which it belongs
        docking.add_interaction(BioInteraction(current, 'has_binding_site'))
        #establish an interaction between docking and BioNodeRef whose regulation depends on the flag on the latter        
        #the priority of the interaction has to be set:
        #   - equal to the number of inputs of BioNodeRef if BioNodeRef is a promoter
        #   - equal to the number of inputs of BioNodeRef - 1 otherwise (because one interaction is with the whole protein)
        BioNodeRef.add_interaction(BioInteraction(docking, 'binds', not BioNodeRef.flag,
            priority = len(BioNodeRef.inputs) if BioNodeRef.typology=='promoter' else len(BioNodeRef.inputs) - 1))
        #if the BioNodeRef is a promoter, then it has to establish an interaction with RNA-pol as well
        if (BioNodeRef.typology == 'promoter'):
            BioNodeRef.add_interaction(BioInteraction(self.PolRef, 'binds', priority = len(BioNodeRef.inputs)))
        #return the docking site
        return docking
    
    def build_10(self, BioNodeRef, current, counter):
        #this is a temporary solution for the termination
        if (BioNodeRef == None):
            return
        #create a binding site BioNode belonging to the current input protein (ref is "new")
        new = BioNode(current.name + ' (' + str(counter) + ')', 'binding_site')
        #add it to the BioNetworkElements list
        self.BioNetworkElements.append(new)
        #establish an interaction between the BS and the protein to which it belongs
        new.add_interaction(BioInteraction(current, 'has_binding_site'))
        #establish an interaction between new and BioNodeRef whose regulation depends on the flag of the latter
        #the priority of the interaction has to be set:
        #   - equal to the number of inputs of BioNodeRef if BioNodeRef is a promoter
        #   - equal to the number of inputs of BioNodeRef - 1 otherwise (because one interaction is with the whole protein)
        BioNodeRef.add_interaction(BioInteraction(new, 'binds', not BioNodeRef.flag,
            priority = len(BioNodeRef.inputs) if BioNodeRef.typology=='promoter' else len(BioNodeRef.inputs) - 1))
        #a fix will be added in the termination phase in case a node only receives 10s
        #return the docking site
        return BioNodeRef
    
    def build_11(self, BioNodeRef, current, counter):
        #this is a temporary solution for the termination
        if (BioNodeRef == None):
            return
        #create a binding site BioNode belonging to the current input protein (ref is "new")
        new = BioNode(current.name + ' (' + str(counter) + ')', 'binding_site')
        #add it to the BioNetworkElements list
        self.BioNetworkElements.append(new)
        #establish an interaction between the BS and the protein to which it belongs
        new.add_interaction(BioInteraction(current, 'has_binding_site'))
        #establish an interaction between new and BioNodeRef whose regulation depends on the flag of the latter
        #the priority of the interaction has to be set:
        #   - equal to the number of inputs of BioNodeRef if BioNodeRef is a promoter
        #   - equal to the number of inputs of BioNodeRef - 1 otherwise (because one interaction is with the whole protein)
        BioNodeRef.add_interaction(BioInteraction(new, 'binds', BioNodeRef.flag,
            priority = len(BioNodeRef.inputs) if BioNodeRef.typology=='promoter' else len(BioNodeRef.inputs) - 1))
        #if the BioNodeRef is a promoter, then new has to establish an interaction with RNA-pol as well
        if (BioNodeRef.typology == 'promoter'):
            self.PolRef.add_interaction(BioInteraction(new, 'binds'))
        #return the docking site
        return BioNodeRef
    
    ###########################################################################
    #NODE EXPANSION    
    def expand_node(self, BoolNodeRef, counter):
        #if the BoolNode has inputs
        if (not BoolNodeRef.inputs_pos):
            print 'has no inputs'  #debug
            return
        #BUILD PRIMER
        #find the BioNodeReference
        BioNodeRef = self.BioNetworkElements[self.BoolNetworkElements.index(BoolNodeRef)]
        #and construct the generic primer, storing the reference of the next docking site
        Docking = self.build_primer_generic(BioNodeRef)
        
        #store the Ref to the promoter for the termination fix
        Promoter = Docking
        
        #retrieve the hyerarchy list from the BoolNode
        CanInputs = BoolNodeRef.hierarchy
        
        Options = {(0,0) : self.build_00,
                   (0,1) : self.build_01,
                    (1,0) : self.build_10,
                    (1,1) : self.build_11}
        
        #ELONGATION/BRANCHING
        #for all the following inputs in the hyerarchy
        for i in CanInputs:
            #retrieve the ref to the BioNode of the input being currently analyzed
            Current = self.BioNetworkElements[i[0]]
            #call a function to build the respective module
            Docking = Options[i[1]](Docking, Current, counter)
        
        #TERMINATION FIX
        #if the Promoter only has negative regulations, then establish an interaction with RNA-pol
        for i in Promoter.inputs:
            if (i.regulation == True):
                return
        Promoter.add_interaction(BioInteraction(self.PolRef, 'binds', priority = len(Promoter.inputs)))
    
    #NETWORK EXPANSION
    def expand_network(self):
        for i in range(len(self.BoolNetworkElements)):
            self.expand_node(self.BoolNetworkElements[i], i - self.n_inputs + 1)
    
    #TRIPLETS LIST
    def triplets_list(self):
        triplets = []
        for i in self.BioNetworkElements:
            for j in i.inputs:
                tmp = tuple([j.regulator.name, j.predicate, i.name])
                triplets.append(tmp)
                print tmp   #for testing
        return triplets
    
    ###########################################################################
    #CREATE NETWORK GRAPH
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


    def bionetwork_graph(self, folder_name, file_name):
        #so....I need a list of all the names
        names = [i.name for i in self.BioNetworkElements]
        #...and a list of tuples for each edge
        edges = []
        #do something
        triplets = self.triplets_list()
        for i in triplets:
            tmp = ((i[0],i[2]), {'label': i[1]})
            edges.append(tmp)
        self.graph(names, edges, folder_name, file_name)

test = pc.network(2,1,4,3)
biotest = BioNetwork(test)

biotest.expand_network()
biotest.bionetwork_graph('BioNtw_tests','test1')
test.print_ntw()


















