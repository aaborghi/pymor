# This file is part of the pyMOR project (https://www.pymor.org).
# Copyright pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (https://opensource.org/licenses/BSD-2-Clause)

import itertools

import numpy as np
import scipy.linalg as spla

from pymor.core.base import BasicObject
from pymor.models.transfer_function import TransferFunction
from pymor.tools.random import new_rng


class pAAAReductor(BasicObject):
    """Reductor implementing the parametric AAA algorithm.

    The reductor implements the parametric AAA algorithm and can be used either with
    data or a given full-order model which can be a |TransferFunction| or any model which
    has a `transfer_function` attribute. MIMO and non-parametric data is accepted. See
    :cite:`NST18` for the non-parametric and :cite:`CRBG20` for the parametric version of
    the algorithm.

    Parameters
    ----------
    sampling_values
        Values where sample data has been evaluated or the full-order model should be evaluated.
        Sampling values are represented as a nested list `svs` such that `svs[i]` corresponds
        to sampling values of the `i`-th variable. The first variable is the Laplace variable.
    samples_or_fom
        Can be either a full-order model (|TransferFunction| or |Model| with a `transfer_function`
        attribute) or data sampled at the values specified in `sampling_values`. Samples are
        represented as a tensor `S`. E.g., for 3 inputs `S[i,j,k]` corresponds to the sampled
        value at `(sampling_values[0][i],sampling_values[1][j],sampling_values[2][k])`. In the
        MIMO case `S[i,j,k]` represents a matrix of dimension `dim_output` times `dim_input`.
    conjugate
        Whether to compute complex conjugates of first sampling variables and enforce
        interpolation in complex conjugate pairs (allows for constructing real system matrices).
    nsp_tol
        Tolerance for null space of higher-dimensional Loewner matrix to check for
        interpolation or convergence.
    post_process
        Whether to do post-processing or not. If the Loewner matrix has a null space
        of dimension greater than 1, it is assumed that the algorithm converged to
        a non-minimal order interpolant which may cause numerical issues. In this case,
        the post-processing procedure computes an interpolant of minimal order.
    L_rk_tol
        Tolerance for ranks of 1-D Loewner matrices computed in post-processing.
    """

    def __init__(self, sampling_values, samples_or_fom, conjugate=True, nsp_tol=1e-16, post_process=True,
                 L_rk_tol=1e-8):
        if isinstance(samples_or_fom, TransferFunction) or hasattr(samples_or_fom, 'transfer_function'):
            fom = samples_or_fom
            if not isinstance(samples_or_fom, TransferFunction):
                fom = fom.transfer_function
            self.num_vars = 1 + fom.parameters.dim

            assert len(sampling_values) == self.num_vars
            self.parameters = fom.parameters
            self.samples = np.empty([len(sv) for sv in sampling_values] + [fom.dim_output, fom.dim_input],
                                    dtype=sampling_values[0].dtype)
            for idx, vals in zip(np.ndindex(self.samples.shape[:-2]),
                                 itertools.product(*sampling_values)):
                params = fom.parameters.parse(vals[1:])
                self.samples[idx] = fom.eval_tf(vals[0], mu=params)
            if fom.dim_input == fom.dim_output == 1:
                self.samples = self.samples.reshape(self.samples.shape[:-2])
        else:
            self.samples = samples_or_fom
            self.num_vars = len(sampling_values)
            self.parameters = {'p': self.num_vars-1}

        self.__auto_init(locals())

    def reduce(self, tol=1e-7, itpl_part=None, max_itpl=None):
        """Reduce using p-AAA.

        Parameters
        ----------
        tol
            Convergence tolerance for relative error of `rom` over the set of samples.
        itpl_part
            Initial partition for interpolation values. Should be `None` or a nested list
            such that `itpl_part[i]` corresponds to indices of interpolated values with
            respect to the `i`-th variable. I.e., `self.sampling_values[i][itpl_part[i]]`
            represents a list of all initially interpolated samples of the `i`-th variable.
            If `None` p-AAA will start with no interpolated values.
        max_itpl
            Maximum number of interpolation points to use with respect to each
            variable. Should be `None` or a list such that `self.num_vars == len(max_itpl)`.
            If `None` `max_itpl[i]` will be set to `len(self.sampling_values[i]) - 1`.

        Returns
        -------
        rom
            Reduced |TransferFunction| model.
        """
        svs = self.sampling_values.copy()
        samples = self.samples.copy()

        # add complex conjugate samples
        if self.conjugate:
            s_conj_list = []
            samples_conj_list = []
            for i, s in enumerate(svs[0]):
                if s.conj() not in svs[0]:
                    s_conj_list.append(s.conj())
                    samples_conj_list.append(samples[i, None].conj())
            if s_conj_list:
                svs[0] = np.append(svs[0], s_conj_list)
                samples = np.vstack([samples] + samples_conj_list)

        num_vars = len(svs)
        max_samples = np.max(np.abs(samples))
        rel_tol = tol * max_samples

        # Transform samples for MIMO case
        if len(samples.shape) != len(svs):
            assert len(samples.shape) == len(svs) + 2
            dim_input = samples.shape[-1]
            dim_output = samples.shape[-2]
            samples_T = np.empty(samples.shape[:-2], dtype=samples.dtype)
            rng = new_rng(0)
            if any(np.iscomplex(svs[0])):
                w = 1j * rng.normal(scale=np.sqrt(2)/2, size=(dim_output,)) \
                    + rng.normal(scale=np.sqrt(2)/2, size=(dim_output,))
                v = 1j * rng.normal(scale=np.sqrt(2)/2, size=(dim_input,)) \
                    + rng.normal(scale=np.sqrt(2)/2, size=(dim_input,))
            else:
                w = rng.normal(size=(dim_output,))
                v = rng.normal(size=(dim_input,))
            w /= np.linalg.norm(w)
            v /= np.linalg.norm(v)
            samples_T = samples @ v @ w
            samples_orig = samples
            samples = samples_T
        else:
            dim_input = 1
            dim_output = 1

        # initialize data partitions, error, max iterations
        err = np.inf
        if itpl_part is None:
            self.itpl_part = [[] for _ in range(num_vars)]
        else:
            assert len(itpl_part) == num_vars
            self.itpl_part = itpl_part
        if max_itpl is None:
            max_itpl = [len(s)-1 for s in svs]

        assert len(max_itpl) == len(svs)

        # start iteration with constant function
        bary_func = np.vectorize(lambda *args: np.mean(samples))

        # iteration counter
        j = 0

        while any(len(i) < mi for i, mi in zip(self.itpl_part, max_itpl)):

            # compute approximation error over entire sampled data set
            grid = np.meshgrid(*svs, indexing='ij')
            err_mat = np.abs(bary_func(*grid) - samples)

            # set errors to zero such that new interpolation points are consistent with max_itpl
            zero_idx = []
            for i in range(num_vars):
                if len(self.itpl_part[i]) >= max_itpl[i]:
                    zero_idx.append(list(range(samples.shape[i])))
                else:
                    zero_idx.append(self.itpl_part[i])
            err_mat[np.ix_(*zero_idx)] = 0
            err = np.max(err_mat)

            j += 1
            self.logger.info(f'Relative error at step {j}: {err/max_samples:.5e}, '
                             f'number of interpolation points {[len(ip) for ip in self.itpl_part]}')

            # stopping criterion based on relative approximation error
            if err <= rel_tol:
                break

            greedy_idx = np.unravel_index(err_mat.argmax(), err_mat.shape)
            for i in range(num_vars):
                if greedy_idx[i] not in self.itpl_part[i] and len(self.itpl_part[i]) < max_itpl[i]:
                    self.itpl_part[i].append(greedy_idx[i])

                    # perform double interpolation step to enforce real state-space representation
                    if i == 0 and self.conjugate and np.imag(svs[i][greedy_idx[i]]) != 0:
                        conj_sample = np.conj(svs[i][greedy_idx[i]])
                        conj_idx = np.where(svs[0] == conj_sample)[0]
                        self.itpl_part[i].append(conj_idx[0])

            # solve LS problem
            L = full_nd_loewner(samples, svs, self.itpl_part)

            _, S, V = spla.svd(L, lapack_driver='gesvd')
            VH = V.T.conj()
            coefs = VH[:, -1:]

            # post-processing for non-minimal interpolants
            d_nsp = np.sum(S/S[0] < self.nsp_tol)
            if d_nsp > 1:
                if self.post_process:
                    self.logger.info('Non-minimal order interpolant computed. Starting post-processing.')
                    pp_coefs, pp_itpl_part = _post_processing(samples, svs, self.itpl_part, d_nsp, self.L_rk_tol)
                    if pp_coefs is not None:
                        coefs, self.itpl_part = pp_coefs, pp_itpl_part
                    else:
                        self.logger.warning('Post-processing failed. Consider reducing "L_rk_tol".')
                else:
                    self.logger.warning('Non-minimal order interpolant computed.')

            # update barycentric form
            itpl_samples = samples[np.ix_(*self.itpl_part)]
            itpl_samples = np.reshape(itpl_samples, -1)
            itpl_nodes = [sv[lp] for sv, lp in zip(svs, self.itpl_part)]
            bary_func = np.vectorize(make_bary_func(itpl_nodes, itpl_samples, coefs))

            if self.post_process and d_nsp >= 1:
                self.logger.info('Converged due to non-trivial null space of Loewner matrix after post-processing.')
                break

        # in MIMO case construct barycentric form based on matrix/vector samples
        if dim_input != 1 or dim_output != 1:
            itpl_samples = samples_orig[np.ix_(*self.itpl_part)]
            itpl_samples = np.reshape(itpl_samples, (-1, dim_output, dim_input))

        bary_func = make_bary_func(itpl_nodes, itpl_samples, coefs)

        if self.num_vars > 1:
            return TransferFunction(dim_input, dim_output,
                                    lambda s, mu: bary_func(s, *(mu[p] for p in self.parameters)),
                                    parameters=self.parameters)
        else:
            return TransferFunction(dim_input, dim_output, lambda s: bary_func(s))


def nd_loewner(samples, svs, itpl_part):
    """Compute higher-dimensional Loewner matrix using only LS partitions.

    .. note::
       For non-parametric data this is simply the regular Loewner matrix.

    Parameters
    ----------
    samples
        Tensor of samples (see :class:`pAAAReductor`).
    svs
        List of sampling values (see :class:`pAAAReductor`).
    itpl_part
        Nested list such that `itpl_part[i]` is a list of indices for interpolated
        sampling values in `svs[i]`.

    Returns
    -------
    L
        (Parametric) Loewner matrix based only on LS partition.
    """
    d = len(samples.shape)
    ls_part = _ls_part(itpl_part, svs)

    s0 = svs[0]
    s = s0[itpl_part[0]]
    sh = s0[ls_part[0]]
    sd = sh[:, np.newaxis] - s[np.newaxis]
    sdpd = sd
    for i in range(1, d):
        p0 = svs[i]
        p = p0[itpl_part[i]]
        ph = p0[ls_part[i]]
        pd = ph[:, np.newaxis] - p[np.newaxis]
        sdpd = np.kron(sdpd, pd)
    samples0 = samples[np.ix_(*itpl_part)]
    samples0 = np.reshape(samples0, (-1, np.prod(samples0.shape)))
    samples1 = samples[np.ix_(*ls_part)]
    samples1 = np.reshape(samples1, (-1, np.prod(samples1.shape)))
    samplesd = samples1.T - samples0

    return samplesd / sdpd


def full_nd_loewner(samples, svs, itpl_part):
    """Compute higher-dimensional Loewner matrix using all combinations of partitions.

    .. note::
       For non-parametric data this is simply the regular Loewner matrix.

    Parameters
    ----------
    samples
        Tensor of samples (see :class:`pAAAReductor`).
    svs
        List of sampling values (see :class:`pAAAReductor`).
    itpl_part
        Nested list such that `itpl_part[i]` is a list of indices for interpolated
        sampling values in `svs[i]`.

    Returns
    -------
    L
        (Parametric) Loewner matrix based on all combinations of partitions.
    """
    L = nd_loewner(samples, svs, itpl_part)
    range_S = range(len(svs))

    # consider all combinations of variables coming from interpolation vs LS partition
    for i in itertools.product(*([0, 1] for _ in range_S)):

        # skip cases corresponding to all interpolated or all LS fit
        if i == tuple(len(svs)*[0]) or i == tuple(len(svs)*[1]):
            continue

        for j in itertools.product(*(itpl_part[k] for k in range_S if i[k] == 0)):
            l_j = list(j)
            for ii in range(len(i)):
                if i[ii] == 1:
                    l_j.insert(ii, slice(None))
            samples0 = samples[tuple(l_j)]
            svs0 = [svs[k] for k in range_S if i[k] == 1]
            itpl_part0 = [itpl_part[k] for k in range_S if i[k] == 1]
            T_mat = 1
            for k in range_S:
                if i[k] == 1:
                    T_new = np.eye(len(itpl_part[k]))
                else:
                    idx = np.where(np.array(itpl_part[k]) == l_j[k])[0][0]
                    T_new = np.eye(1, len(itpl_part[k]), idx)
                T_mat = np.kron(T_mat, T_new)
            LL = nd_loewner(samples0, svs0, itpl_part0)
            L = np.vstack([L, LL @ T_mat])
    return L


def make_bary_func(itpl_nodes, itpl_vals, coefs, removable_singularity_tol=1e-14):
    """Return function handle for (multivariate) barycentric form.

    Parameters
    ----------
    itpl_nodes
        Nested list such that `itpl_nodes[i]` contains interpolated sampling values
        of the `i`-th variable.
    itpl_vals
        Vector of interpolation values.
    coefs
        Vector of barycentric coefficients.
    removable_singularity_tol
        Tolerance for evaluating the barycentric function at a removable singularity
        and performing pole cancellation.

    Returns
    -------
    bary_func
        (Multi-variate) Loewner matrix based on all combinations of partitions.
    """
    def bary_func(*args):
        pd = 1
        # this loop is for pole cancellation which occurs at interpolation nodes
        for i in range(len(itpl_nodes)):
            d = args[i] - itpl_nodes[i]
            d_zero = d[np.abs(d) < removable_singularity_tol]
            if len(d_zero) > 0:
                d_min_idx = np.argmin(np.abs(d))
                d = np.eye(1, len(d), d_min_idx)
            else:
                d = 1 / d
            pd = np.kron(pd, d)
        m = coefs.T * pd
        num = np.tensordot(m, itpl_vals, axes=1)
        denom = np.inner(coefs.T, pd)
        nd = num / denom
        return np.atleast_2d(nd[0])

    return bary_func


def _ls_part(itpl_part, svs):
    """Compute least-squares partition based on interpolation partition."""
    ls_part = []
    for p, s in zip(itpl_part, svs):
        idx = np.arange(len(s))
        idx = np.delete(idx, p)
        ls_part.append(list(idx))
    return ls_part


def _post_processing(samples, svs, itpl_part, d_nsp, L_rk_tol):
    """Compute coefficients/partition to construct minimal interpolant."""
    num_vars = len(svs)
    max_idx = np.argmax([len(ip) for ip in itpl_part])
    max_rks = []
    for i in range(num_vars):
        max_rk = 0
        # we don't need to compute this max rank since we exploit nullspace structure
        if i == max_idx:
            max_rks.append(len(itpl_part[max_idx])-1)
            continue
        shapes = []
        for j in range(num_vars):
            if i != j:
                shapes.append(samples.shape[j])
        # compute max ranks of all possible 1-D Loewner matrices
        for idc in itertools.product(*(range(s) for s in shapes)):
            l_idc = list(idc)
            l_idc.insert(i, slice(None))
            L = nd_loewner(samples[tuple(l_idc)], [svs[i]], [itpl_part[i]])
            rk = np.linalg.matrix_rank(L, tol=L_rk_tol)
            if rk > max_rk:
                max_rk = rk
        max_rks.append(max_rk)
    # exploit nullspace structure to obtain final max rank
    denom = np.prod([len(itpl_part[k])-max_rks[k] for k in range(len(itpl_part))])
    if denom == 0 or d_nsp % denom != 0:
        return None, None
    max_rks[max_idx] = len(itpl_part[max_idx]) - d_nsp / denom
    max_rks[max_idx] = round(max_rks[max_idx])
    for i in range(len(max_rks)):
        itpl_part[i] = itpl_part[i][0:max_rks[i]+1]

    # solve LS problem
    L = full_nd_loewner(samples, svs, itpl_part)
    _, S, V = spla.svd(L, lapack_driver='gesvd')
    VH = np.conj(V.T)
    coefs = VH[:, -1:]

    return coefs, itpl_part
