
import ProjectClasses as pc
import numpy as np
import itertools as it
import timeit as ti

#this is an example of Boolean network
#later on we'll create a class to create network instances

#now we describe the network manually, but later this info will be decoded
#from a string

#if I declared name,inputs and function at the beginning, the name of the
#inputs would't find any match because yet undeclared, so...

##############################################################################
#let's make a function to create a random network
#we need to specify our CONSTRAINTS:
# n of inputs
# n of outputs
# total number of nodes
# maximum n of inputs
# type of function

def RandomNtw(n_inputs, n_outputs, n_nodes, max_inputs):
    #first, just declare the nodes
    #for the inputs
    for i in range(n_inputs):
        #create node objects
        print("debug")
    
    #for the "mechanism" nodes
    
    #and for the outputs
    
    


##############################################################################

##create an instance for each node
input1 = pc.node("input1")
input2 = pc.node("input2")

node1 = pc.node("node1")
node2 = pc.node("node2")
node3 = pc.node("node3")
node4 = pc.node("node4")

output = pc.node("output")

##create the network node list
network = [input1, input2, node1, node2, node3, node4, output]
#at this time you can also associate inputs_pos to each node

node1.set_info([node2,node3],[0,0,0,1],network)
node2.set_info([node2,input1],[0,1,0,1],network)
node3.set_info([node4,input2],[0,1,1,1],network)
node4.set_info([node1,node4],[1,1,0,0],network)

output.set_info([node4],[1,0],network)

NtwLen = len(network)

##############################################################################

#it will contain an adjacency matrix (to represent it graphically later on)
def am1():  #RELIC
    AdjMat = np.zeros((NtwLen,NtwLen), dtype=np.bool)
##remember that no node appears in the network list twice, so index() is fine,
##but it fails if the element is not in the list
    for i in range(NtwLen):
        for j in network[i].inputs:
            if (j):   #can you move the if before to spare computations?
                AdjMat[network.index(j),i] = True
    return AdjMat
#test: 1000times -> 0.0438389778137 sec

def am2():
    AdjMat = np.zeros((NtwLen,NtwLen), dtype=np.bool)
    for i in range(NtwLen):
        if (network[i].inputs):
            for j in network[i].inputs:
                AdjMat[network.index(j),i] = True
    return AdjMat
#test: 1000times -> 0.0379509925842 sec

def am3():  #RELIC
    AdjMat = np.zeros((NtwLen,NtwLen), dtype=np.bool)
    for i in network:
        if (i.inputs):
            for j in i.inputs:
                AdjMat[network.index(j),network.index(i)] = True
    return AdjMat
#test: 1000times -> 0.0714998245239

def am4():  #RELIC
    AdjMat = np.zeros((NtwLen,NtwLen), dtype=np.int)
    for i in range(NtwLen):
        if (network[i].inputs):
            for j in network[i].inputs:
                AdjMat[network.index(j),i] = 1
    return(AdjMat)
#test: 1000times -> 0.0718200206757

##############################################################################
        
##it will contain a transition table (to help me in calculating trajectories)
##bad idea. Table is OPTIONAL. just think of an update function.
##what about a dictionary, to map every t to the corresponding t+1?

#let's create an UPDATE FUNCTION

#what if every node had a function to calculate its own update? done!
#now I can exploit it to get the t+1 state

#t is a list of tuples. each tuple is a state (combination of inputs)
t = list(it.product([0,1], repeat=NtwLen))

#calculate the inputs that affects a given node
#not to be called if node has no inputs
def PersonalInputs1(node, status):  #RELIC
    result = []
    for i in node.inputs:
        result.append(status[network.index(i)])
        #also indexing every time is not a good idea
        #why don't you create an attribute "inputs positions"?
    return(tuple(result))

def PersonalInputs2(node, status):  #RELIC
    result = []
    for i in node.inputs_pos:
        result.append(status[i])
    return(tuple(result))
    
def PersonalInputs3(node, status):
    return(tuple([status[i] for i in node.inputs_pos]))

def UpdateStatus(status):
    sp1 = []
    #for each node in the network
    for i in range(NtwLen):
        #if the node has inputs, then...
        if (network[i].inputs):
            #calculate its next value according to its personal inputs
            sp1.append(network[i].update1(PersonalInputs3(network[i],status)))
        #if the node has no inputs, then...
        else:
            sp1.append(status[i])
            #sp1.append(status[network.index(network[i])])
    return(tuple(sp1))

def TransTable():
    tp1 = []
    for i in t:
        tp1.append(UpdateStatus(i))
    return(tp1)
#test: 1000times -> 6.58059978485 sec
#test: 1000times -> 6.12356996536 sec removing tt construction every update
#test: 1000times -> 1.11633419991 sec removing indexing every update! :D
#apparently, indexing operations destroy performance...
#test: 1000times -> 0.753097057343 sec with PersonalInputs3
#test: 1000times -> 0.521726131439 sec removing another useless indexing

##############################################################################

#it will have a SIMULATE FUNCTION (method)
#taking an initial state as parameter
def Simulate(initial):
    trajectory = []
    current = initial
    #loop = 0
    while (True):
        tmp = UpdateStatus(current)
        #do I really need to check EVERY element in trajectory?
        if (tmp not in trajectory):
            trajectory.append(tmp)
            current = tmp
        else:
            #loop = trajectory.index(tmp)
            break
    print(trajectory)
    return(trajectory)
    #return trajectory[:loop], trajectory[loop:]
#test: 1000times t[60]-> 0.0255160331726 sec
#test: 1000times t[60]-> 0.00012993812561 sec using break instead of flag :D

def MassiveSimulation():
    for i in t:
        Simulate(i)
#test: 1000times -> 0.0153961181641 sec


############################## TIME TEST ##############################
##def f_name():
##    instructions
##    
##print ti.timeit("f_name()", setup = "from __main__ import f_name", number=1)

