#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 17:05:57 2023

@author: xwei2
"""

import gstools as gs
import numpy as np


# def generate_gaussian_field_3D(theta, x, y, z, seed = None):
    
#     """
    
#     Parameters
#     ----------
#     theta : array
#         an array contains 7 elems of variogram, i.e., mean, var, range x, range y, range z, anisotropy ratios x-y, anisotropy ratios x-z
#     x,y,z : array
#         spatial coords
#     seed : int/float

#     Returns
#     -------
#     field : array
#         3D random gaussian field

#     """
    
    
#     model = gs.Gaussian(
#         dim = 3, 
#         var = theta[1], 
#         len_scale = [theta[2],theta[3],theta[4]], 
#         angles = [theta[5]*np.pi/180, theta[6]*np.pi/180]
#         )
    
#     if seed:
#         srf = gs.SRF(model, seed=seed)
#     else: 
#         srf = gs.SRF(model)
        
#     field = srf.structured([x, y, z]) + theta[0]
    
#     return field


class GaussianField(object):
    """
    
    Generate deterministic or random gaussian fields in 2D or 3D.
    
    """
    
    
    def __init__ (
            self, 
            mean,
            variance,
            range_x, 
            range_y, 
            range_z, 
            anisotropy_xy,
            anisotropy_xz,
            x, 
            y, 
            z,
            random = False,
            output_params = False,
            ):
        
        """
    
        Parameters
        ----------
        mean: float or list
            mean of gaussian field
        variance: float or lit
            variance of gaussian field
        vel_range_x : float or list
            velocity range in x
        vel_range_y : float or list
            velocity range in y
        vel_range_z : float or list
            velocity range in z
        anisotropy_xy : float or list
            anisotropy angle in xy panel
        anisotropy_xz : float or list
            anisotropy angle in xz panel
        x, y, x: array
            spatial coordinates in three directions
        random: bool, default: False
            generate random gaussian field
        output_params: bool, default: False
            output the parameters for random gaussian field

        """
        
        self.mean, self.variance = mean, variance
        self.range_x, self.range_y, self.range_z = range_x, range_y, range_z
        self.anisotropy_xy, self.anisotropy_xz = anisotropy_xy, anisotropy_xz
        self.x, self.y, self.z = x, y, z
        
        self.random = random
        self.output = output_params
        
    
    def field_function_3d(self, theta, x, y, z):
        """
        
        Gaussian field in 3D

        Parameters
        ----------
        theta : array
            contains gaussian field parameters
        x : array
            spatial coordinates in X
        y : array
            spatial coordinates in Y
        z : array
            spatial coordinates in Z

        Returns
        -------
        TYPE
            3D gaussian field

        """

        model = gs.Gaussian(
            dim = 3, 
            var = theta[1], 
            len_scale = [theta[2], theta[3], theta[4]], 
            angles = [theta[5] * np.pi/180, theta[6] * np.pi/180],
            )

        srf = gs.SRF(model)
        
        return srf.structured([x, y, z]) + theta[0]
    
    
    
    def field_function_2d(self, theta, x, y):
        """
        
        Gaussian field in 2D

        """

        model = gs.Gaussian(
            dim = 2, 
            var = theta[1], 
            len_scale = [theta[2], theta[3]], 
            angles = [theta[4] * np.pi/180],
            )

        srf = gs.SRF(model)
        
        return srf.structured([x, y]) + theta[0]
    
    
    @property    
    def field_3d(self):
        """
        
        Gaussian field in 3D


        Returns
        -------
        array
            a 3D gaussian field and the parameters
            
        """
        

        if self.random:
            
            theta = np.array([
                np.random.uniform(self.mean[0], self.mean[1]),
                np.random.uniform(self.variance[0], self.variance[1]),
                np.random.uniform(self.range_x[0], self.range_x[1]),
                np.random.uniform(self.range_y[0], self.range_y[1]),
                np.random.uniform(self.range_z[0], self.range_z[1]),
                np.random.uniform(self.anisotropy_xy[0], self.anisotropy_xy[1]),
                np.random.uniform(self.anisotropy_xz[0], self.anisotropy_xz[1])
                ])
            
            field =  self.field_function_3d(theta, self.x, self.y, self.z)
            
        else:
            
            theta = np.array([
                self.mean, self.variance,
                self.range_x, self.range_y, self.range_z,
                self.anisotropy_xy, self.anisotropy_xz
                ])
            
            field =  self.field_function_3d(theta, self.x, self.y, self.z)
        
        if self.output:
            
            return field, theta
        
        else:
            
            return field



    @property    
    def field_2d(self):
        """
        
        Gaussian field in 2D


        Returns
        -------
        array
            a 2D gaussian field and the parameters
            
        """

        if self.random:
            
            theta = np.array([
                np.random.uniform(self.mean[0], self.mean[1]),
                np.random.uniform(self.variance[0], self.variance[1]),
                np.random.uniform(self.range_x[0], self.range_x[1]),
                np.random.uniform(self.range_y[0], self.range_y[1]),
                np.random.uniform(self.anisotropy_xy[0], self.anisotropy_xy[1])
                ])
            
            field =  self.field_function_2d(theta, self.x, self.y)
            
        else:
            
            theta = np.array([
                self.mean, self.variance,
                self.range_x, self.range_y,
                self.anisotropy_xy
                ])
            
            field =  self.field_function_2d(theta, self.x, self.y)
        
        if self.output:
            
            return field, theta
        else:
            
            return field
        