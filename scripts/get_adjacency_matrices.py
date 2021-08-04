import cana
from cana.datasets import bio
import numpy as np
import networkx as nx
from glob import glob

from networkx.linalg.graphmatrix import adjacency_matrix


cc_models = bio.load_all_cell_collective_models()
cc_models.append(bio.DROSOPHILA())
cc_models.append(bio.BREAST_CANCER())
cc_models.append(bio.LEUKEMIA())
cc_models.append(bio.BUDDING_YEAST())

for i, mod in enumerate(cc_models):
    new_name = mod.name.replace(' ', '_').lower()
    net = mod.structural_graph()
    adj_mat = nx.to_numpy_array(net)

    np.savetxt('data/boolean_networks/adjacency_matrix/' + new_name + '.csv', 
    adj_mat, fmt='%d', delimiter=',')

    net = mod.effective_graph()
    eff_gph = nx.to_numpy_array(net)
    np.savetxt('data/boolean_networks/effective_graph/' + new_name + '.csv', 
    eff_gph, delimiter=',')