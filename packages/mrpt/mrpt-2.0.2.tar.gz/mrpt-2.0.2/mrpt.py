import numpy as np
from os import name as os_name

import mrptlib


class MRPTIndex(object):
    """
    An MRPT index object
    """

    def __init__(self, data, shape=None, mmap=False):
        """
        Initializes an MRPT index object.
        :param data: Input data either as a NxDim numpy ndarray or as a filepath to a binary file containing the data.
        :param shape: Shape of the data as a tuple (N, dim). Needs to be specified only if loading the data from a file.
        :param mmap: If true, the data is mapped into memory. Has effect only if the data is loaded from a file.
        :return:
        """
        if isinstance(data, np.ndarray):
            if len(data) == 0 or len(data.shape) != 2:
                raise ValueError("The data matrix should be non-empty and two-dimensional")
            if data.dtype != np.float32:
                raise ValueError("The data matrix should have type float32")
            if not data.flags["C_CONTIGUOUS"] or not data.flags["ALIGNED"]:
                raise ValueError("The data matrix has to be C_CONTIGUOUS and ALIGNED")
            n_samples, dim = data.shape
        elif isinstance(data, str):
            if not isinstance(shape, tuple) or len(shape) != 2:
                raise ValueError(
                    "You must specify the shape of the data as a tuple (N, dim) "
                    "when loading data from a binary file"
                )
            n_samples, dim = shape
        elif data is not None:
            raise ValueError("Data must be either an ndarray or a filepath")

        if mmap and os_name == "nt":
            raise ValueError("Memory mapping is not available on Windows")

        if data is not None:
            self.index = mrptlib.MrptIndex(data, n_samples, dim, mmap)
            self.dim = dim

        self.built = False
        self.autotuned = False

    def _compute_sparsity(self, projection_sparsity):
        if projection_sparsity == "auto":
            return 1.0 / np.sqrt(self.dim)
        if projection_sparsity is None:
            return 1
        if not (0 < projection_sparsity <= 1):
            raise ValueError("Sparsity should be in (0, 1]")
        return projection_sparsity

    def build(self, depth, n_trees, projection_sparsity="auto"):
        """
        Builds a normal MRPT index.
        :param depth: The depth of the trees; should be in the set {1, 2, ..., floor(log2(n))}.
        :param n_trees: The number of trees used in the index.
        :param projection_sparsity: Expected ratio of non-zero components in a projection matrix.
        :return:
        """
        if self.built:
            raise RuntimeError("The index has already been built")

        projection_sparsity = self._compute_sparsity(projection_sparsity)
        self.index.build(n_trees, depth, projection_sparsity)
        self.built = True

    def build_autotune(
        self,
        target_recall,
        Q,
        k,
        trees_max=-1,
        depth_min=-1,
        depth_max=-1,
        votes_max=-1,
        projection_sparsity="auto",
        shape=None,
    ):
        """
        Builds an autotuned MRPT index.
        :param target_recall: The target recall level (float) or None if the target recall level
                              is set later using the subset function.
        :param Q: A matrix of test queries used for tuning, one per row.
        :param k: Number of nearest neighbors searched for.
        :param trees_max: Maximum number of trees grown; can be used to control the building time
                          and memory usage; a default value -1 sets this to min(sqrt(n), 1000).
        :param depth_min: Minimum depth of trees considered when searching for optimal parameters;
                          a default value -1 sets this to min(log2(n), 5).
        :param depth_max: Maximum depth of trees considered when searching for optimal parameters;
                          a default value -1 sets this to log2(n) - 4:
        :param votes_max: Maximum number of votes considered when searching for optimal parameters;
                          a default value -1 sets this to max(trees / 10, 10).
        :param projection_sparsity: Expected ratio of non-zero components in a projection matrix
        :param shape: Shape of the test query matrix as a tuple (n_test, dim). Needs to be specified
                      only if loading the test query matrix from a file.
        :return:
        """
        if self.built:
            raise RuntimeError("The index has already been built")

        if isinstance(Q, np.ndarray):
            if len(Q) == 0 or len(Q.shape) != 2:
                raise ValueError("The test query matrix should be non-empty and two-dimensional")
            if Q.dtype != np.float32:
                raise ValueError("The test query matrix should have type float32")
            if not Q.flags["C_CONTIGUOUS"] or not Q.flags["ALIGNED"]:
                raise ValueError("The test query matrix has to be C_CONTIGUOUS and ALIGNED")
            n_test, dim = Q.shape
        elif isinstance(Q, str):
            if not isinstance(shape, tuple) or len(shape) != 2:
                raise ValueError(
                    "You must specify the shape of the data as a tuple (n_test, dim) "
                    "when loading the test query matrix from a binary file"
                )
            n_test, dim = shape
        else:
            raise ValueError("The test query matrix must be either an ndarray or a filepath")

        if dim != self.dim:
            raise ValueError(
                "The test query matrix should have the same number of columns as the data matrix"
            )

        self.built = target_recall is not None
        self.autotuned = True

        if target_recall is None:
            target_recall = -1

        projection_sparsity = self._compute_sparsity(projection_sparsity)
        self.index.build_autotune(
            target_recall,
            Q,
            n_test,
            k,
            trees_max,
            depth_min,
            depth_max,
            votes_max,
            projection_sparsity,
        )

    def build_autotune_sample(
        self,
        target_recall,
        k,
        n_test=100,
        trees_max=-1,
        depth_min=-1,
        depth_max=-1,
        votes_max=-1,
        projection_sparsity="auto",
    ):
        """
        Builds an autotuned MRPT index.
        :param target_recall: The target recall level (float) or None if the target recall level
                              is set later using the subset function.
        :param k: Number of nearest neighbors searched for.
        :param n_test: Number of test queries to sample.
        :param trees_max: Maximum number of trees grown; can be used to control the building time
                          and memory usage; a default value -1 sets this to min(sqrt(n), 1000).
        :param depth_min: Minimum depth of trees considered when searching for optimal parameters;
                          a default value -1 sets this to min(log2(n), 5).
        :param depth_max: Maximum depth of trees considered when searching for optimal parameters;
                          a default value -1 sets this to log2(n) - 4:
        :param votes_max: Maximum number of votes considered when searching for optimal parameters;
                          a default value -1 sets this to max(trees / 10, 10).
        :param projection_sparsity: Expected ratio of non-zero components in a projection matrix
        :return:
        """
        if self.built:
            raise RuntimeError("The index has already been built")

        self.built = target_recall is not None
        self.autotuned = True

        if target_recall is None:
            target_recall = -1

        projection_sparsity = self._compute_sparsity(projection_sparsity)
        self.index.build_autotune_sample(
            target_recall,
            n_test,
            k,
            trees_max,
            depth_min,
            depth_max,
            votes_max,
            projection_sparsity,
        )

    def subset(self, target_recall):
        """
        Create a new index for a specified target recall level by copying trees from an autotuned index grown
        without a prespecified recall level.
        :param target_recall: The target recall level.
        :return: A new MRPT object autotuned for the specified recall level.
        """
        if not self.autotuned:
            raise RuntimeError("Only an autotuned index can be subset")

        new_index = MRPTIndex(None)
        new_index.index = self.index.subset(target_recall)
        new_index.dim = self.dim
        new_index.built = True
        new_index.autotuned = True
        return new_index

    def parameters(self):
        """
        Get the parameters of the index.
        :return: A dictionary of the hyperparameters of the index.
        """
        n_trees, depth, votes, k, qtime, recall = self.index.parameters()

        if self.index.is_autotuned():
            return {
                "n_trees": n_trees,
                "depth": depth,
                "k": k,
                "votes": votes,
                "estimated_qtime": qtime,
                "estimated_recall": recall,
            }
        return {"n_trees": n_trees, "depth": depth}

    def save(self, path):
        """
        Saves the MRPT index to a file.
        :param path: Filepath to the location of the saved index.
        :return:
        """
        if not self.built:
            raise RuntimeError("Cannot save index before building")
        self.index.save(path)

    def load(self, path):
        """
        Loads the MRPT index from a file.
        :param path: Filepath to the location of the index.
        :return:
        """
        self.index.load(path)
        self.built = True
        self.autotuned = self.index.is_autotuned()

    def ann(self, q, k=None, votes_required=None, return_distances=False):
        """
        Performs an approximate nearest neighbor query for a single query vector or multiple query vectors
        in parallel. The queries are given as a numpy vector or a numpy matrix where each row contains a query.
        :param q: The query object. Can be either a single query vector or a matrix with one query vector per row.
        :param k: The number of nearest neighbors to be returned, has to be specified if the index has not been autotuned.
        :param votes_required: The number of votes an object has to get to be included in the linear search part of the query;
                               has to be specified if the index has not been autotuned.
        :param return_distances: Whether the distances are also returned.
        :return: If return_distances is false, returns a vector or matrix of indices of the approximate
                 nearest neighbors in the original input data for the corresponding query. Otherwise,
                 returns a tuple where the first element contains the nearest neighbors and the second
                 element contains their distances to the query.
        """
        if not self.built:
            raise RuntimeError("Cannot query before building index")
        if q.dtype != np.float32:
            raise ValueError("The query matrix should have type float32")

        if not self.autotuned and (k is None or votes_required is None):
            raise ValueError("k and votes_required must be set if the index has not been autotuned")

        if k is None:
            k = -1
        if votes_required is None:
            votes_required = -1

        return self.index.ann(q, k, votes_required, return_distances)

    def exact_search(self, q, k, return_distances=False):
        """
        Performs an exact nearest neighbor query for a single query several queries in parallel. The queries are
        given as a numpy matrix where each row contains a query. Useful for measuring accuracy.
        :param q: The query object. Can be either a single query vector or a matrix with one query vector per row.
        :param k: The number of nearest neighbors to return.
        :param return_distances: Whether the distances are also returned.
        :return: If return_distances is false, returns a vector or matrix of indices of the exact
                 nearest neighbors in the original input data for the corresponding query. Otherwise,
                 returns a tuple where the first element contains the nearest neighbors and the second
                 element contains their distances to the query.
        """
        if q.dtype != np.float32:
            raise ValueError("The query matrix should have type float32")

        if k < 1:
            raise ValueError("k must be positive")

        return self.index.exact_search(q, k, return_distances)
