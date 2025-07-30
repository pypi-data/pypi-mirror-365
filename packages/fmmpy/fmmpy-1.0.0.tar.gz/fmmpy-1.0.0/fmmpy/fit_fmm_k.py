# -*- coding: utf-8 -*-

import numpy as np
from numpy.fft import fft, ifft
from scipy.optimize import minimize
from .auxiliar_functions import szego, mobius, predict2, transition_matrix, split_complex, inner_products_sum_2

def fit_fmm_k(analytic_data_matrix, time_points=None, n_back=None, max_iter=None,
              omega_grid=None, weights=None, channel_weights=None, 
              post_optimize=True, omega_min=0.01, omega_max=1):
    
    if(analytic_data_matrix.ndim == 2):
        n_ch, n_obs = analytic_data_matrix.shape
    elif(analytic_data_matrix.ndim == 1):
        n_obs = analytic_data_matrix.shape[0]
        n_ch = 1
        analytic_data_matrix = analytic_data_matrix[np.newaxis, :]
    else:
        print("Bad data matrix dimensions.")
    
    if(max_iter==None):
        max_iter=1
        
    # Grid definition.
    fmm_grid = np.meshgrid(omega_grid, time_points)
    afd_grid = (1-fmm_grid[0])/(1+fmm_grid[0])*np.exp(1j*(fmm_grid[1]))
    
    modules_grid = (1-omega_grid)/(1+omega_grid)*np.exp(1j*0)
    an_search_len = modules_grid.shape[0]
    
    # base: DFT coefficients of szego kernels with different a's (different modules)
    base = np.zeros((modules_grid.shape[0], n_obs), dtype=complex)
    for i in range(an_search_len):
        base[i,:] = fft(szego(modules_grid[i], time_points), n_obs)
    
    # Parameters (AFD)
    coefs = np.zeros((n_ch, n_back+1), dtype=complex)
    phis = np.zeros((n_ch, n_back+1), dtype=complex)
    a_parameters = np.zeros(n_back+1, dtype=complex)
    sigma_weights = np.copy(weights) 
    
    # Start decomposing: c0 (mean)
    z = np.exp(1j*time_points)
    remainder = np.copy(analytic_data_matrix)
    for ch_i in range(n_ch):
        coefs[ch_i,0] = np.mean(analytic_data_matrix[ch_i,:])
        remainder[ch_i,:] = ((analytic_data_matrix[ch_i,:] - coefs[ch_i,0])/z)
        sigma_weights[ch_i] = 1/np.var((analytic_data_matrix[ch_i,:] - coefs[ch_i,0]).real)
    
    ## 1 Iteration of the backfitting algorithm: fit k waves
    for k in range(1, n_back+1):
        ## STEP 1: Grid search - AFD-FFT formulations
        abs_coefs = 0
        for ch_i in range(n_ch):
            abs_coefs += channel_weights[ch_i] * sigma_weights[ch_i]*np.abs(ifft(np.repeat(fft(
                remainder[ch_i, :], n_obs)[np.newaxis, :], 
                an_search_len, axis=0) * base, n_obs, 1))
        abs_coefs = abs_coefs.T

        mask_used = np.isclose(
            afd_grid[..., np.newaxis], 
            np.array(a_parameters[:k]),  
            atol=1e-10, rtol=1e-5
        ).any(axis=2)

        abs_coefs_masked = np.copy(abs_coefs)
        abs_coefs_masked[mask_used] = -np.inf

        max_loc_tmp = np.argwhere(abs_coefs_masked == np.amax(abs_coefs_masked))
        best_a = afd_grid[max_loc_tmp[0, 0], max_loc_tmp[0, 1]]

        if(post_optimize):
            res = minimize(
                inner_products_sum_2, x0=split_complex(best_a), 
                args=(remainder, time_points, channel_weights * sigma_weights), 
                method='L-BFGS-B', bounds=[(-2*np.pi, 4*np.pi), ((1-omega_max)/(1+omega_max),(1-omega_min)/(1+omega_min))],
                tol=1e-4, options={'disp': False})
            opt_a = res.x[1]*np.exp(1j*res.x[0])
            a_parameters[k] = opt_a
        else:
            a_parameters[k] = best_a

        szego_a = szego(a_parameters[k], time_points)
        for ch_i in range(n_ch):
            coefs[ch_i, k] = (np.conj(szego_a.dot(remainder[ch_i,:].conj().T)) / n_obs).item()
            remainder[ch_i,:] = ((remainder[ch_i,:] - coefs[ch_i,k]*szego_a) 
                                 / mobius(a_parameters[k], time_points))

    if max_iter > 1:
        for iter_j in range(1,max_iter):
            blaschke = z 
            for k in range(1, n_back+1):
                blaschke = blaschke*mobius(a_parameters[k], time_points)
        
            for k in range(1, n_back+1):
                std_remainder = analytic_data_matrix - predict2(np.delete(a_parameters, k, axis=0), analytic_data_matrix, time_points)[0]
                sigma_weights = 1/np.var(std_remainder.real, axis=1, ddof=1)

                blaschke = blaschke / mobius(a_parameters[k], time_points)
                remainder = std_remainder / blaschke

                abs_coefs = 0
                for ch_i in range(n_ch):
                    abs_coefs += channel_weights[ch_i]*sigma_weights[ch_i]*np.abs(ifft(np.repeat(fft(
                        remainder[ch_i, :], n_obs)[np.newaxis, :], 
                        an_search_len, axis=0) * base, n_obs, 1))

                abs_coefs = abs_coefs.T

                mask_used = np.isclose(
                    afd_grid[..., np.newaxis], 
                    np.array(a_parameters[:k]),
                    atol=1e-10, rtol=1e-5
                    ).any(axis=2)

                abs_coefs_masked = np.copy(abs_coefs)
                abs_coefs_masked[mask_used] = -np.inf

                max_loc_tmp = np.argwhere(abs_coefs_masked == np.amax(abs_coefs_masked))
                best_a = afd_grid[max_loc_tmp[0, 0], max_loc_tmp[0, 1]]
                if(post_optimize):
                    res = minimize(
                        inner_products_sum_2, x0=split_complex(best_a), 
                        args=(remainder, time_points, channel_weights*sigma_weights), 
                        method='L-BFGS-B', bounds=[(-2*np.pi, 4*np.pi), ((1-omega_max)/(1+omega_max),(1-omega_min)/(1+omega_min))],
                        options={'disp': False})
                    opt_a = res.x[1]*np.exp(1j*res.x[0])
                    a_parameters[k] = opt_a
                else:
                    a_parameters[k] = best_a
                for ch_i in range(n_ch):
                    coefs[ch_i, k] = (np.conj(szego_a.dot(remainder[ch_i,:].conj().T)) / n_obs).item()

                blaschke = blaschke * mobius(a_parameters[k], time_points)

    AFD2FMM_matrix = transition_matrix(a_parameters)
      
    prediction, coefs = predict2(a_parameters, analytic_data_matrix, time_points)
    phis = np.dot(AFD2FMM_matrix, coefs.T).T

    return a_parameters, coefs, phis, prediction