import numpy as np
import networkx as nx
from bio_synergy.tpm_builder import parse_logic_file, build_tpm

LOGIC_FILE = 'bio_synergy/tests/tester_logic_file.txt'
NODE3_LUT = np.array([[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 1]])
KNOWN_TPM = np.loadtxt('bio_synergy/tests/tester_tpm.txt', delimiter=',')
ADJ_MAT = np.loadtxt('bio_synergy/tests/tester_adjacency_matrix.txt', dtype=int, delimiter=',')


def test_parse_logic_file():
    logic_dict = parse_logic_file(LOGIC_FILE)
    assert logic_dict[1]['inputs'] == [5] and np.array_equal(logic_dict[3]['lut'], NODE3_LUT)

def text_get_maxent_probs():
    pass

def test_build_tpm():
    logic_dict = parse_logic_file(LOGIC_FILE)
    mb_graph = nx.from_numpy_array(ADJ_MAT, create_using=nx.DiGraph)
    tpm = build_tpm(logic_dict, mb_graph)
    assert np.array_equal(tpm, KNOWN_TPM)