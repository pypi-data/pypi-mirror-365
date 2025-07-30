# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import scipy.signal as sc

from .fit_fmm_k import fit_fmm_k
from .fit_fmm_k_restr import (
    fit_fmm_k_restr_alpha_omega,
    fit_fmm_k_restr_betas,
    fit_fmm_k_restr_all_params
)
from .auxiliar_functions import seq_times

from .FMMModel import FMMModel

ERROR_MESSAGES = {
    "exc_data_1": "'data_matrix' is not an instance of 'numpy.ndarray'.",
    "exc_data_2": "'data_matrix' must have 2 dimensions.",
    "exc_omega_restr_1": "Arguments error: Check that: 0 < 'omega_min' < 'omega_max' < 1.",
    "exc_omega_restr_2": "An arc for an individual omega is out of ['omega_min', 'omega_max'].",
    "exc_beta_restr_1": "Invalid beta range: both 'beta_min' and 'beta_max' must be either None or numeric values. Mixed types are not allowed.",
    "exc_beta_restr_2": "Invalid beta range: 'beta_min' and 'beta_max' may be between 0 and 2pi.",
    "exc_beta_restr_3": "Invalid beta range: arc('beta_min', 'beta_max')<pi.",
    "exc_alpha_omega_restr_1": "Arrays containing restrictions have different lengths.",
    "algorithm_arguments": "'n_back' and 'max_iter' must be >1.",
    "grid_arguments": "'omega_grid' and 'length_alpha_grid' must be positive.",
    "post_optimize_arguments": "'post_optimize' must be a logical value.",
    "channel_weight_arguments": "'channel_weights' length do not match the number of channels or weights are not all positives."
}

def fit_fmm(
    data_matrix, time_points=None, n_back=1, max_iter=1, post_optimize=True, channel_weights=None,
    length_alpha_grid=48, omega_min=0.01, omega_max=0.99, length_omega_grid=24,
    omega_grid=None, alpha_restrictions=None, omega_restrictions=None,
    group_restrictions=None, beta_min=None, beta_max=None, beta_restrictions=None):
    """
    Fits a Frequency Modulated Möbius (FMM) model to a multivariate signal.
    
    This function performs FMM-based decomposition of analytic signals, optionally 
    incorporating restrictions on frequencies (omega), phases (alpha), and shape parameters (beta).
    
    Parameters
    ----------
    data_matrix : numpy.ndarray or pandas.DataFrame
        Input data matrix of shape (n_channels, n_timepoints). If a DataFrame is provided, it will be converted.
    
    time_points : array-like or None, optional
        Vector of time points corresponding to columns of `data_matrix`. If None, a default sequence is generated.
    
    n_back : int, optional
        Number of FMM components to include in the decomposition (default is 1). Must be >=1.
    
    max_iter : int, optional
        Maximum number of iterations for the fitting algorithm (default is 1). Must be >=1.
    
    post_optimize : bool, optional
        If True, post-optimization of coefficients is performed (default is True).
        
    channel_weights : numpy.ndarray
        Vector of weights for ecah lead in the optimization funcion (default is all 1). 
    
    length_alpha_grid : int, optional
        Number of points in the alpha grid, only in restricted fittings. Must be > 0. Default is 48.
        
    omega_min : float, optional
        Minimum value for the frequency search grid, must be in (0,1). Default is 0.01.
    
    omega_max : float, optional
        Maximum value for the frequency search grid, must be in (0,1). Default is 0.99.
    
    length_omega_grid : int, optional
        Number of points in the log-scale exponential grid (if `omega_grid` is None). Must be > 0. Default is 24.
    
    omega_grid : array-like or None, optional
        Custom grid of omega values. If None, a default exponential grid is generated.
    
    alpha_restrictions : list of arrays or None, optional
        List of angle intervals (in radians) for each FMM component. Each element should be a tuple (alpha_min, alpha_max).
    
    omega_restrictions : list of arrays or None, optional
        List of frequency intervals for each FMM component. Each element should be a tuple (omega_min, omega_max).
    
    group_restrictions : list of int or None, optional
        Grouping indices for combining alpha and omega restrictions. Must match the length of restrictions if provided.
    
    beta_min : float or None, optional
        Minimum value for beta restriction (in radians). Must be in [0, 2π] if used.
    
    beta_max : float or None, optional
        Maximum value for beta restriction (in radians). Must be in [0, 2π] if used.
        
    beta_restrictions : list of list of tuples or None, optional
        Element [i][j] is a tuple (beta_min, beta_max) defining the allowed range for the j-th component 
        of the i-th channel. If None, uniform restriction is applied from beta_min and beta_max.
    Returns
    -------
    FMMModel
        An object containing the fitted model, including the estimated parameters and prediction.
    
    Raises
    ------
    TypeError
        If `data_matrix` is not a numpy array or cannot be converted to one.
        If `post_optimize` is not a boolean.

    ValueError
        If `data_matrix` is not 2-dimensional.
        If `n_back < 1` or `max_iter < 1`.
        If `channel_weights` length does not match the number of channels of are not positive.
        If `omega_min <= 0` or `omega_max >= 1`.
        If only one of `beta_min` or `beta_max` is provided.
        If `beta_min` or `beta_max` are not in [0, 2π].
        If the arc defined by (`beta_min`, `beta_max`) is greater than π.
        If `length_omega_grid` or `length_alpha_grid` is not positive when required.
        If both `alpha_restrictions` and `omega_restrictions` are provided but have different lengths.
        If `group_restrictions` is provided and does not match the length of both `alpha_restrictions` and `omega_restrictions`.
        If any omega restriction lies outside the interval [`omega_min`, `omega_max`].
    Examples
    --------

    Basic 5-component FMM fit without restrictions:
    
    >>> res = fit_fmm(data_matrix=df,        # Data: shape (n_channels, n_timepoints)
    ...               n_back=5, max_iter=8)  # Model configuration
    
    Fit with restrictions on alpha and omega:
    
    >>> P_alpha = (4.2, 5.4)
    >>> P_ome = (0.05, 0.25)
    >>> QRS_alpha = (5.4, 6.2)
    >>> QRS_ome = (0.01, 0.10)
    >>> T_alpha = (0, 3.14)
    >>> T_ome = (0.1, 0.5)
    
    >>> alpha_restr = np.array([P_alpha, QRS_alpha, QRS_alpha, QRS_alpha, T_alpha])
    >>> omega_restr = np.array([P_ome, QRS_ome, QRS_ome, QRS_ome, T_ome])
    
    >>> res2 = fit_fmm(data_matrix=df,
    ...                n_back=5, max_iter=8, post_optimize=True,
    ...                alpha_restrictions=alpha_restr,
    ...                omega_restrictions=omega_restr,
    ...                omega_min=0.01, omega_max=0.5)
    
    """

    if isinstance(data_matrix, pd.DataFrame):
        data_matrix = data_matrix.values
    if isinstance(data_matrix, (list, tuple, pd.Series)):
        data_matrix = np.array(data_matrix)
    if not isinstance(data_matrix, np.ndarray):
        raise TypeError(ERROR_MESSAGES["exc_data_1"])
    if data_matrix.ndim == 1:
        data_matrix = data_matrix[np.newaxis, :]
    elif data_matrix.ndim != 2:
        raise ValueError(ERROR_MESSAGES["exc_data_2"])

    if (beta_min is None) ^ (beta_max is None):
        raise ValueError(ERROR_MESSAGES["exc_beta_restr_1"])
    if beta_min is not None:
        if beta_min < 0 or beta_min > 2*np.pi or beta_max < 0 or beta_max > 2*np.pi:
            raise ValueError(ERROR_MESSAGES["exc_beta_restr_2"])
        if (beta_max - beta_min) % (2*np.pi) > np.pi:
            raise ValueError(ERROR_MESSAGES["exc_beta_restr_3"])

    if alpha_restrictions is not None and omega_restrictions is not None:
        if group_restrictions is None:
            if len(alpha_restrictions) != len(omega_restrictions):
                raise ValueError(ERROR_MESSAGES["exc_alpha_omega_restr_1"])
        else:
            if not (len(group_restrictions) == len(alpha_restrictions) == len(omega_restrictions)):
                raise ValueError(ERROR_MESSAGES["exc_alpha_omega_restr_1"])

    if omega_min <= 0 or omega_max >= 1:
        raise ValueError(ERROR_MESSAGES["exc_omega_restr_1"])
    if omega_restrictions is not None:
        if any(ome[0] > omega_max or ome[1] < omega_min for ome in omega_restrictions):
            raise ValueError(ERROR_MESSAGES["exc_omega_restr_2"])

    if n_back < 1 or max_iter < 1:
        raise ValueError(ERROR_MESSAGES["algorithm_arguments"])
    if not isinstance(post_optimize, bool):
        raise TypeError(ERROR_MESSAGES["post_optimize_arguments"])
    
    n_ch, n_obs = data_matrix.shape

    if omega_grid is None:
        if length_omega_grid < 1:
            raise ValueError(ERROR_MESSAGES["grid_arguments"])
        omega_grid = np.exp(np.linspace(np.log(omega_min), np.log(omega_max), num=length_omega_grid+2))[1:-2]

    if length_alpha_grid < 1:
        raise ValueError(ERROR_MESSAGES["grid_arguments"])
    alpha_grid = np.linspace(0, 2*np.pi, num=length_alpha_grid, endpoint=False)

    # Dispatch according to restriction configuration
    restricted_flag = False
    if time_points is None:
        time_points = seq_times(n_obs)
    
    if channel_weights is None:
        channel_weights = np.ones(n_ch)
        
    if not (len(channel_weights) == n_ch and np.all(np.array(channel_weights) > 0)):
        raise ValueError(ERROR_MESSAGES["channel_weight_arguments"])
        
    analytic_data_matrix = sc.hilbert(data_matrix, axis=1)
    
    if alpha_restrictions is None and omega_restrictions is None and beta_min is None and beta_max is None:
        a, coefs, phis, prediction = fit_fmm_k(
            analytic_data_matrix=analytic_data_matrix,
            time_points=time_points,
            n_back=n_back,
            max_iter=max_iter,
            omega_grid=omega_grid,
            weights=np.ones(n_ch),
            channel_weights=channel_weights,
            post_optimize=post_optimize,
            omega_min=omega_min,
            omega_max=omega_max
        )
    
    elif beta_min is None and beta_max is None and beta_restrictions is None:
        restricted_flag = True
        group_restrictions = group_restrictions or list(range(n_back))
        a, coefs, phis, prediction = fit_fmm_k_restr_alpha_omega(
            analytic_data_matrix=analytic_data_matrix,
            time_points=time_points,
            n_back=n_back,
            max_iter=max_iter,
            omega_grid=omega_grid,
            weights=np.ones(n_ch),
            channel_weights=channel_weights,
            post_optimize=post_optimize,
            omega_min=omega_min,
            omega_max=omega_max,
            alpha_restrictions=alpha_restrictions,
            omega_restrictions=omega_restrictions,
            group_restrictions=group_restrictions
        )
    
    elif alpha_restrictions is None and omega_restrictions is None:
        restricted_flag = True
        if beta_restrictions is None:
            beta_restrictions = [[(beta_min, beta_max)] * n_back for _ in range(n_ch)]
        else:
            beta_restrictions = [
                [
                    (beta_min, beta_max) if (bmin is None and bmax is None) else (bmin, bmax)
                    for (bmin, bmax) in row
                ] for row in beta_restrictions
            ]
        a, coefs, phis, prediction = fit_fmm_k_restr_betas(
            analytic_data_matrix=analytic_data_matrix,
            time_points=time_points,
            n_back=n_back,
            max_iter=max_iter,
            alpha_grid=alpha_grid,
            omega_grid=omega_grid,
            weights=np.ones(n_ch),
            channel_weights=channel_weights,
            post_optimize=post_optimize,
            omega_min=omega_min,
            omega_max=omega_max,
            beta_restrictions=beta_restrictions
        )
    
    else:
        restricted_flag = True
        group_restrictions = group_restrictions or list(range(n_back))
        if beta_restrictions is None:
            beta_restrictions = [[(beta_min, beta_max)] * n_back for _ in range(n_ch)]
        else:
            beta_restrictions = [
                [(beta_min, beta_max) if (bmin is None and bmax is None) else (bmin, bmax)
                    for (bmin, bmax) in row] for row in beta_restrictions]
            
        a, coefs, phis, prediction = fit_fmm_k_restr_all_params(
            analytic_data_matrix=analytic_data_matrix,
            time_points=time_points,
            n_back=n_back,
            max_iter=max_iter,
            alpha_grid=alpha_grid,
            omega_grid=omega_grid,
            weights=np.ones(n_ch),
            channel_weights=channel_weights,
            post_optimize=post_optimize,
            omega_min=omega_min,
            omega_max=omega_max,
            alpha_restrictions=alpha_restrictions,
            omega_restrictions=omega_restrictions,
            group_restrictions=group_restrictions,
            beta_restrictions=beta_restrictions
        )

    alphas = (np.angle(a[1:]) + np.pi) % (2 * np.pi)
    As = np.abs(phis[:, 1:])
    betas = (np.angle(phis[:, 1:]) + alphas) % (2 * np.pi)

    params = {
        'alpha': alphas,
        'omega': (1 - np.abs(a[1:])) / (1 + np.abs(a[1:])),
        'a': a,
        'M': phis[:, 0].real,
        'A': As,
        'beta': betas,
        'delta': As * np.cos(betas),
        'gamma': As * np.sin(betas),
        'coef': coefs,
        'phi': phis
    }

    model = FMMModel(
        data=data_matrix, time_points=time_points, prediction=prediction.real,
        params=params, restricted=restricted_flag, max_iter=max_iter
    )

    return model
