"""
A wrapper for sklearn's `graphical_lasso` implementation
"""

from GmGM import Dataset
from GmGM.core.preprocessing import create_gram_matrices
import numpy as np
from sklearn.covariance import graphical_lasso
import scipy.sparse as sparse

def GLasso(
    dataset: Dataset,
    beta: float,
    use_nonparanormal_skeptic: bool = False,
    max_iter: int = 100,
    tol: float = 1e-5
) -> Dataset:
    if len(dataset.dataset) != 1:
        raise ValueError(
            'DNNLasso only supports one dataset'
        )
    if len(dataset.batch_axes) == 0:
        raise ValueError(
            "Please make the first axis of the dataset a batch axis!"
        )
    tensor = list(dataset.dataset.values())[0]
    if tensor.ndim != 3:
        raise ValueError(
            'DNNLasso only supports two-dimensional (i.e. matrix-variate) datasets, with a batch axis.'
        )
    structure = list(dataset.structure.values())[0]
    row_to_use = structure[-1]
    _, *d = tensor.shape
    tensor = tensor.reshape(-1, tensor.shape[-1])
    
    dataset = create_gram_matrices(
        dataset,
        use_nonparanormal_skeptic=use_nonparanormal_skeptic,
    )
    Ss = {
        axis: matrix
        for axis, matrix
        in dataset.gram_matrices.items()
    }

    _, Psi = graphical_lasso(
        Ss[row_to_use],
        beta,
        tol=tol,
        max_iter=max_iter,
    )
    
    # Only the Psi corresponding with "axis-to-use" is the actual precision matrix,
    # everything else should have an 'independence assumption'
    Psis = {
        axis: (
            sparse.csr_array(np.asarray(Psi))
            if axis == row_to_use
            else sparse.csr_matrix(np.eye(d[i]))
        )
        for i, axis in enumerate(Ss.keys())
    }
    
    dataset.precision_matrices = Psis
    return dataset