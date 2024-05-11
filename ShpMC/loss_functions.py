#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 16:12:37 2023

@author: xwei2
"""

import numpy as np
from scipy.spatial import procrustes
import random


def loss_function_binary(observations, observations_sign_dist, observations_sign_dist_contact, c):
    
    """
    
    Loss function for the binary observations
    
    Parameters
    ----------
    observations : array
        binary observations, where 0 and 1 correspond to non-target and target, respectively. 0.5 specifically indicates contact points
    observations_sign_dist : array
        signed distance of the observations, where positive inside the target, negative outside the target, zero is the boundary
    observations_sign_dist_contact : array
        signed distance at contact points only
    c : int/float
        hyperparameter controls the contribution of the loss function

    Returns
    -------
    loss : TYPE
        loss function
    O_ik : TYPE
        logistic loss func, i.e., the number of mismatch points
    O_bias : TYPE
        square mean error (bias) at borehole contact points 
    O_var : TYPE
        mean square error (var) at borehole contact points

    """

    # Logistic loss function for observations
    # Non-intrusive observations
    O_0k = (np.log(1+np.exp(observations_sign_dist[observations==0]))/np.log2(2)).sum()
    
    # Intrusive observations
    O_1k = (np.log(1+np.exp(-observations_sign_dist[observations==1]))/np.log2(2)).sum()
    
    O_ik = O_0k+O_1k
    
    # Square mean error (bias) at contact points 
    O_bias = np.square(np.mean(observations_sign_dist_contact))
    
    # Mean square errors (var) at contact points
    O_var = np.mean(np.square(observations_sign_dist_contact))

    if np.isnan(O_ik): O_ik = 1e5
        
    loss = c * (O_ik + O_bias + O_var)
    
    return loss


def model_sign_dist_to_data(model_sign_dist, data):
    
    """
    
    Transform model signed distance to the observations
    
    Parameters
    ----------
    model_sign_dist : array
        signed distance model
    data_3d : list
        data list that includes multiple data sets, e.g., borehole, outcrop, and sketch

    Returns
    -------
    obs : array
        binary observations
    obs_sign_dist : array
        signed distance of the observations
    obs_sign_dist_contact : array
        signed distance of the observations at contact points only

    """
    
    data_index = ~np.isnan(data)
    
    obs = data[data_index]
    obs[obs > 0] = 1 # Binary observations

    # Signed dist for all observations
    obs_sign_dist = model_sign_dist[data_index]
    
    # Signed dist for contact points
    obs_sign_dist_contact = model_sign_dist[data == 0.5]
    
    return obs, obs_sign_dist, obs_sign_dist_contact


def find_sketch_from_model_3d(model, ind_, direction):
    
    """
    
    Find the geological sketch profile
    
    Parameters
    ----------
    model : array
        randomly sampled 3D model
    ind_ : int or list
        index of the geological profile
    direction : str
        profile direction ("X", "Y", "Z")

    Returns
    -------
    comparision_shape : array
        the model profile to be compared with the geological sketch

    """
    
    
    if isinstance(ind_, list):
        ind_tmp = random.randint(ind_[0], ind_[-1])
        if direction == 'x': model_sketch = model[ind_tmp, :, :]
        if direction == 'y': model_sketch = model[:, ind_tmp, :]
        if direction == 'z': model_sketch = model[:, :, ind_tmp]
    
    else:
        if direction == 'x': model_sketch = model[ind_, :, :]
        if direction == 'y': model_sketch = model[:, ind_, :]
        if direction == 'z': model_sketch = model[:, :, ind_]
        
    comparision_shape = np.zeros_like(model_sketch)
    comparision_shape[model_sketch>0] = 1
    
    return comparision_shape



def loss_ordinary_procrustes_analysis(shape_reference, shape_comparision, contribution):

    """
    
    Loss function for ordinary procrustes analysis (OPA)
    
    Parameters
    ----------
    shape_reference : array
        shape for the reference, e.g., geological sketch
    shape_comparision : array
        shape for the comparision, e.g., randomly sampled model shape
    contribution : int/float
        hyperparameter controls the contribution of the loss function

    Returns
    -------
    procrustes_distance : float
        the distance measures the structural similarity of two geometries

    """


    row_ref, col_ref = shape_reference.shape
    
    row_comp, col_comp = shape_comparision.shape

    mu_ref = shape_reference.mean(0)
    mu_comp = shape_comparision.mean(0)

    # Centered
    shape_reference_centered = shape_reference - mu_ref
    shape_comparision_centered = shape_comparision - mu_comp

    square_sum_ref = (shape_reference_centered**2.).sum()
    square_sum_comp = (shape_comparision_centered**2.).sum()

    # Frobenius norm
    F_norm_ref = np.sqrt(square_sum_ref)
    F_norm_comp = np.sqrt(square_sum_comp)

    # scale to equal (unit) norm
    shape_reference_centered /= F_norm_ref
    shape_comparision_centered /= F_norm_comp

    if row_ref > row_comp:
        shape_comparision_centered = np.concatenate((shape_comparision_centered, np.zeros([row_ref - row_comp, 2])), 0)
        
    if row_ref < row_comp:
        shape_reference_centered = np.concatenate((shape_reference_centered, np.zeros([row_comp - row_ref, 2])), 0)
        
    # Optimal rotation matrix
    A = np.dot(shape_reference_centered.T,shape_comparision_centered)
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    R = np.dot(Vt.T, U.T)

    trace_s = s.sum()

    # Optimum scaling
    beta = trace_s * F_norm_ref / F_norm_comp

    # Procruste distance after normalization
    dist = 1 - trace_s**2

    # Transformed coords
    Z = F_norm_ref * trace_s * shape_comparision_centered + mu_ref

    # Translation matrix
    c = mu_ref - beta * mu_comp
    
    #transformation values 
    transform_params = {'rotation':R, 'scale':beta, 'translation':c}
   
    
    return contribution*dist, Z, transform_params





