import numpy as np
from networkx import DiGraph
from .utils import to_binary, to_decimal

def parse_logic_file(file_path: str) -> list:
    """
    This function will return the logic of each node in the cnet formatted file
    provided.

    Returns
    -------
    logic: list of dict
        dictionaryu has two keys: 'inputs': a list of inputs and 'outputs': a
            list of transitions in ascending order
    """
    with open(file_path, 'r') as fin:
        # this list will contain all the info for our network
        logic = []
        # we will define this dictionary here so we can use it in the logic
        new_entry = {}
        output_list = []
        for line in fin.readlines():
            # start of lines detailing new node
            if line[0] == '#' and len(new_entry) != 0:
                # add everything to the logic list
                new_entry['lut'] = np.array(output_list[::-1])
                logic.append(new_entry)
                # reset everything
                output_list = []
                new_entry = {}
            # these lines detail the inputs to a node
            elif line[:2] == '.n':
                split_inputs = line.split(' ')
                # cnet format counts from 1 not zero
                new_entry['inputs'] = [int(inp) - 1 for inp in split_inputs[3:]]
            # these detail the transitions in the opposite order that i like
            elif line[0] == '0' or line[0] == '1':
                look_up_table = [int(d) for d in ''.join(line.strip().split(' '))]
                output_list.append(look_up_table)

        # once all lines are parsed we will have to add things one last time
        new_entry['lut'] = np.array(output_list[::-1])
        logic.append(new_entry)
    
    return logic


def build_tpm(node_logic: list, markov_blanket: DiGraph) -> np.array:
    """
    Thakes the list from the parsed logic file and the graph (or maybe just
    the list of nodes idk) and returns the transition probability matrix for all
    possible states.
    This is fucking NON trivial
    """
    # set up the matrix
    N = len(markov_blanket.nodes)
    tpm = np.zeros((2**N, 2**N))

    # sort the markov blanket list so that we know that the first index is the
    # lowest number. Not sure that it matters but for building this thing it
    # will help my brain
    mb_list = sorted(markov_blanket.nodes)

    # I think I also need a dictionary that will let me do reverse lookups
    mb_rev = {nid: i for i, nid in enumerate(markov_blanket.nodes)}

    # lets get a list of nodes that have inputs in the markov blanket we will
    # probably have to get at like the logic here because we dont have all of
    # the inputs in all of the 
    logic_nodes = []
    transition_probs = [[]*N]
    in_mb_inputs = {nid: [] for nid in mb_list}
    prob_tables = {}
    for mbi, nid in enumerate(mb_list):
        # 'protected' networkx attr returned by G.predecessors[node_id]
        node_preds = markov_blanket._pred[nid]
        
        # if the node has any inputs in the markov blanket we have to do tons
        # of shitty bullshit
        if len(node_preds) > 0:
            # add to list of nodes with interesting logic
            logic_nodes.append(nid)
            
            # so we need to pull out the look up tables for each node and get
            # probabilities assuming all unobserved variables obey MaxEnt

            # this gets us a dictionary keyed by the node id with lists of
            # inputs in the markov blanket. we'll need this info later
            keep_cols = []
            for ii, inp in enumerate(node_logic[nid]['inputs']):
                if inp in node_preds:
                   keep_cols.append(ii)
                   in_mb_inputs[nid].append(inp)

            
            # we also need to keep the very last column
            keep_cols.append(-1)

            'this is an absolute fucking nightmare'

            # now we have to collapse the table by counting the number of
            # transitions into either state stored in a matrix with rows
            # for every unique input combination and one column for each output
            node_probs = np.zeros((2**(len(keep_cols) - 1), 2))
            thin_lut = node_logic[nid]['lut'][:, keep_cols]
            for row in thin_lut:
                in_idx = to_decimal(row[:-1])
                out_idx = row[-1]
                node_probs[in_idx, out_idx] += 1

            # turn the rowss into probability distributions
            row_sums = np.sum(node_probs, axis=1)
            node_probs = (node_probs.T / row_sums).T # why this behavior numpy?

            # put the transition array into a dictionary for lookup later
            prob_tables[nid] = node_probs

        # if node has no inputs in the markov blanket we just get to skip it!
        else:
            continue
            

    # we will think of the indices of the matrix as base 10 encodings of binary
    # vectors representing all of the states of all of the nodes. We can now
    # iterate over all positions in the matrix and determine the transitions
    for r in range(tpm.shape[0]):
        state = to_binary(r, N)
        # we can build an array that will have the probabilities of 
        # transitioning to ON or OFF for each node in the 
        transitions = np.zeros((N, 2))
        for nodei, value in enumerate(state):
            # we'll refer to the node id a bunch of times so lets assign it
            nid = mb_list[nodei]
            # if we dont have this nodes input nodes the node transitions
            # completely randomly
            if len(in_mb_inputs[nid]) == 0:
                transitions[nodei, :] = 0.5
            else:
                # we need to look up the probabilities from the tables we
                # we build up earlier
                input_idx = [mb_list.index(inpid) for inpid in in_mb_inputs[nid]]
                table_entry = to_decimal(state[input_idx])
                transitions[nodei, :] = prob_tables[nid][table_entry]
        
        # ok now we can iterate over the columns 
        for c in range(tpm.shape[1]):
            next_state = to_binary(c, N)
            probs = [transitions[i, st] for i, st in enumerate(next_state)]
            tpm[r, c] = np.product(probs)


    return tpm