#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 16:06:29 2023

@author: xwei2
"""
import numpy as np


def transformation_matrix_2d(orientation_degree, scale=None, shear=None):
    
    """
    
    Parameters
    ----------
    orientation_degree : float, optional
        rotation angle (0 - 360 degrees). The default is None.
    scale : list, optional
        scaling values in x and y directions. Zoom in (scale > 1). The default is None.
    shear : list, optional
        shearing values in x and y directions. The default is None.
    offset : array, optional
        offset values in x and y directions. The default is None.

    Returns
    -------
    mat : array, 2 by 2
        the transformation matrix

    """
    
    
    if orientation_degree is None:
        raise TypeError("'orientation_degree' cannot be None!")
    
    ang = orientation_degree * np.pi / 180.0
    mat = np.array([
        [np.cos(ang), -np.sin(ang)], 
        [np.sin(ang), np.cos(ang)]
        ]) 

    if scale is not None:

        if not isinstance(scale, np.ndarray or list):
            raise TypeError("'scale' must be an array or list!")
        
        mat_scale = np.array([
            [scale[0], 0],
            [0, scale[-1]]
            ]) 
        
        mat = mat @ mat_scale

    if shear is not None:
        
        if not isinstance(shear, np.ndarray or list):
            raise TypeError("'shear' must be an array or list!")
            
        mat_shear = np.array([
            [1, shear[0]],
            [shear[-1], 1]
            ]) 
        
        mat = mat @ mat_shear
    

    return mat



def coord_transformation_2d(data, mat, offset=None):
    
    """
    
    Parameters
    ----------
    data : array dim: N by 2
        the data set to trasform.
    mat : array dim: 2 by 2
        transformation matrix
    offset : array, optional
        Offset values. The default is None.

    Returns
    -------
    The transformed data dim: N by 2
    

    """
    
    data_transformed = data @ mat
    
    if offset is not None:
        
        if not isinstance(offset, np.ndarray):
            raise TypeError("'offset' must be an array!")
            
        assert mat.shape[0] == offset.shape[0], "'offset' should be 2 dimensions! e.g., (2,)"
            
        data_transformed = data_transformed + offset
        
    return data_transformed






