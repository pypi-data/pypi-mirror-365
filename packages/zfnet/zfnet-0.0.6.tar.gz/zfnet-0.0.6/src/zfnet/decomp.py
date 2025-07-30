import tensorly as tl
from tensorly.decomposition import non_negative_parafac, non_negative_parafac_hals
from tensorly.decomposition._cp import initialize_cp
from tensorly.cp_tensor import CPTensor
import time
from copy import deepcopy


def tensor_decomp(data, rank):
    data_tensor = tl.tensor(data)
    start_time = time.time()
    weights_init, factors_init = initialize_cp(
    data_tensor, non_negative=True, init="random", rank=rank
    )

    cp_init = CPTensor((weights_init, factors_init))

    tic = time.time()
    tensor_hals, errors_hals = non_negative_parafac_hals(
        data_tensor, rank=rank, init=deepcopy(cp_init), return_errors=True
    )
    cp_reconstruction_hals = tl.cp_to_tensor(tensor_hals)
    time_hals = time.time() - tic

    print("reconstructed tensor\n", cp_reconstruction_hals[10:12, 10:12, 10:12], "\n")
    print("input data tensor\n", data_tensor[10:12, 10:12, 10:12])
    print(str(f"{time_hals:.2f}") + " " + "seconds")

    return tensor_hals, time_hals, errors_hals

