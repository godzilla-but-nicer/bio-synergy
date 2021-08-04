def residual_tpms(M):
    """
    Given a TPM of a system X of N interacting binary elements, 
    returns the TPMs of the system with each element excluded.
    Each TPM is 2**(N-1) x 2**(N-1).
    Removed elements go from left to right according to the standard binary 
    naming schema.
    """
    pi = equilibrium_dist(M)
    # Since M is the TPM for a system of binary elements, the number of elements is log2 of the number of states.
    num_elements = int(np.log2(M.shape[0]))
    states = ["".join(x) for x in product(["0", "1"], repeat=num_elements)]
    resid_states = ["".join(x)
                    for x in product(["0", "1"], repeat=num_elements-1)]
    pi_dict = {states[i]: pi[i] for i in range(len(pi))}
    # Rather than attempting fancy indexing on M, it is *much* easier to do it all in a hash-table.
    M_dict = {}
    for i in range(M.shape[0]):
        for j in range(M.shape[0]):
            # The key is a tuple (state_i, state_j) and the value is the probability of transition to state_j conditional on being in state_i
            M_dict[(states[i], states[j])] = M[i][j]
    resid_mats = [np.zeros((2**(num_elements-1), 2**(num_elements-1)))
                  for x in range(num_elements)]
    for e in range(len(resid_mats)):
        resid_mat = resid_mats[e]
        for i in range(resid_mat.shape[0]):
            for j in range(resid_mat.shape[1]):
                spec_states = [x for x in states if (
                    x[:e:] + x[e+1::]) == resid_states[i]]
                s_array = np.zeros(len(spec_states))
                for s in range(len(spec_states)):
                    s_array[s] = pi_dict[spec_states[s]] * sum([M_dict[x] for x in M_dict.keys() if
                                                                ((x[0][:e:] + x[0][e+1::]) == resid_states[i]) and
                                                                ((x[1][:e:] + x[1][e+1::]) == resid_states[j]) and
                                                                x[0] == spec_states[s]])
                resid_mat[i][j] = np.mean(s_array)
        for i in range(resid_mat.shape[0]):
            resid_mat[i] = resid_mat[i] / np.sum(resid_mat[i])
    return resid_mats
