import time
import numpy as np
from sklearn.metrics import pairwise_distances
from threadpoolctl import threadpool_limits

from anglekmeans.akmc_ import myakm_py

# @_threadpool_controller_decorator(limits=1, user_api="blas")
def _kmeans_single_lloyd(
    X,
    centers_init,
    max_iter=300,
    verbose=False,
    tol=1e-4,
    n_threads=1,
):
    """A single run of k-means lloyd, assumes preparation completed prior.

    Parameters
    ----------
    X : {ndarray, sparse matrix} of shape (n_samples, n_features)
        The observations to cluster. If sparse matrix, must be in CSR format.

    centers_init : ndarray of shape (n_clusters, n_features)
        The initial centers.

    max_iter : int, default=300
        Maximum number of iterations of the k-means algorithm to run.

    verbose : bool, default=False
        Verbosity mode

    tol : float, default=1e-4
        Relative tolerance with regards to Frobenius norm of the difference
        in the cluster centers of two consecutive iterations to declare
        convergence.
        It's not advised to set `tol=0` since convergence might never be
        declared due to rounding errors. Use a very small number instead.

    n_threads : int, default=1
        The number of OpenMP threads to use for the computation. Parallelism is
        sample-wise on the main cython loop which assigns each sample to its
        closest center.

    Returns
    -------
    centroid : ndarray of shape (n_clusters, n_features)
        Centroids found at the last iteration of k-means.

    label : ndarray of shape (n_samples,)
        label[i] is the code or index of the centroid the
        i'th observation is closest to.

    inertia : float
        The final value of the inertia criterion (sum of squared distances to
        the closest centroid for all observations in the training set).

    n_iter : int
        Number of iterations run.
    """

    # ############ align X, C, C_new
    # t_start = time.time()
    # X_arg = align_padding_py(X, row_padding=False)
    # centers_init_arg = align_padding_py(centers_init, row_padding=True)
    # n_clusters = centers_init.shape[0]
    # n_clusters_arg = centers_init_arg.shape[0]
    # dim = centers_init_arg.shape[1]
    # centers_new_arg = malloc_align_py(n_clusters_arg, dim)

    # centers_arg = centers_init_arg
    labels = np.full(X.shape[0], -1, dtype=np.int32)
    count = np.zeros(max_iter, dtype=np.int64)
    time = np.zeros(4, dtype=np.int64)
    # labels_old = labels.copy()

    # weight_in_clusters = malloc_align_py(n_clusters_arg, 1)
    # weight_in_clusters = weight_in_clusters.reshape(-1)
    # weight_in_clusters[:] = 0

    # center_shift = np.zeros(n_clusters_arg, dtype=X.dtype)

    # # fast var
    # x_norm = malloc_align_py(X_arg.shape[0], 1)
    # x_norm = x_norm.reshape(-1)
    # x_norm[:] = np.einsum('ij,ij->i', X_arg, X_arg)  

    # # c_norm: squared, 
    # # D_CC: squared, 
    # # OCiCj: may be nan
    # c_norm = malloc_align_py(n_clusters_arg, 1)
    # c_norm = c_norm.reshape(-1)

    # D_CC = malloc_align_py(n_clusters_arg, n_clusters_arg)

    # COS_OCiCj = malloc_align_py(n_clusters_arg, n_clusters_arg)
    # SIN_OCiCj = malloc_align_py(n_clusters_arg, n_clusters_arg)

    # compute_COS_OCiCj_py(centers_arg, c_norm, D_CC, COS_OCiCj, SIN_OCiCj)

    # # OCX, r2, is null, first time
    # cos_ocx = malloc_align_py(X_arg.shape[0], 1)
    # cos_ocx = cos_ocx.reshape(-1)  

    # sin_ocx = malloc_align_py(X_arg.shape[0], 1)
    # sin_ocx = sin_ocx.reshape(-1)  

    # r2 = malloc_align_py(X_arg.shape[0], 1)
    # r2 = r2.reshape(-1)  

    # count = np.zeros(X.shape[0], dtype=np.int32)
    # total_c = 0

    # # lloyd_iter = lloyd_iter_chunked_dense
    # lloyd_iter = update_chunk_omp_py
    # _inertia = _inertia_dense

    # # openmp allocation
    # thread_num = 20
    # cen_new_chunk_all = malloc_align_py(thread_num * n_clusters_arg, dim)
    # wc_new_chunk_all  = malloc_align_py(thread_num, n_clusters_arg)

    # strict_convergence = False

    # t_iter = 0
    # t_var = 0

    # time_omp = 0
    # time_cen = 0
    # time_arr = np.zeros(2, dtype=np.int64)

    iters = myakm_py(X, centers_init, labels, count, time, verbose, tol=1e-6, n_threads=20, max_iter=100)

    # inertia = _inertia(X_arg, centers_arg[:n_clusters, :], labels, n_threads)

    # t_end = time.time()
    # t_all = t_end - t_start

    return labels, count, time, iters