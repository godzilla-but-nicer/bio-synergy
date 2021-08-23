#%%
import numpy as np
from cana.boolean_node import BooleanNode

# Some helpful fuinctions for converting between individual
# states and ints representing the joint states
def to_binary(n, digits):
    binary_digits = []
    for _ in range(digits):
        binary_digits.append(int(n % 2))
        n = int(n / 2)
    return np.array(binary_digits[::-1])


def to_decimal(b):
    expos = np.arange(len(b), 0, -1) - 1
    enc = 2**expos
    return np.array(b).T.dot(enc)

# this will be the demo string we use for our logic gate
demo_string = """
              000 0
              001 0
              010 1
              011 0
              100 1
              101 1
              110 0
              111 1"""
#%%
# parse the string
k = len(demo_string.split('\n')[1].strip().split(' ')[0])
outputs = [int(line.strip().split(' ')[-1]) for line in demo_string.split('\n') if len(line) > 0]
inputs = [to_binary(i, k) for i in range(2**k)]

# set up the matrix
tpm = np.zeros((2**(k+1), 2**(k+1)))

# iterate over rows, relevant information are the input states
for r in range(tpm.shape[0]):
    # need transition to allocate prob this checks joint input states 
    lut_idx = int(np.floor(r/2))
    transition = outputs[lut_idx]
    # iterate over cols and fill in relevant probabilities
    for c in range(tpm.shape[1]):
        # transition happens to tells us the remainder we expect
        if c % 2 == transition:
            tpm[r, c] = 1 / (2**k)

#%%
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# ok so the real shit is we have to do this with markov blankets
mb_file = "../data/coarse_grained/markov_blankets/apoptosis_network_mb_boolean.csv"
adj_mat = "../data/boolean_networks/adjacency_matrix/apoptosis_network.csv"
logic = "../data/boolean_networks/logic/apoptosis_network.txt"

# we'll focus on just the first markov blanket for now
mb = pd.read_csv(mb_file)
first_mb = mb.iloc[0]['markov_blanket'].replace('[', '').replace(']', '')
fmb = [int(n) for n in first_mb.split(', ')]

# ok we'll also need the adjacency matrix. it will help at least
adj_arr = np.loadtxt(adj_mat, dtype=int, delimiter=',')
fam = nx.from_numpy_array(adj_arr, create_using=nx.DiGraph)
fam_mb_0 = nx.subgraph(fam, fmb)

# draw the markov blanket
options = {
    "font_size": 36,
    "node_size": 3000,
    "node_color": "white",
    "edgecolors": "black",
    "linewidths": 5,
    "width": 5,
}
pos = nx.spring_layout(fam_mb_0, seed=1234)
nx.draw_networkx(fam_mb_0, pos, options)
plt.show()

# %% [markdown]
This is going to be a fucking nightmare
