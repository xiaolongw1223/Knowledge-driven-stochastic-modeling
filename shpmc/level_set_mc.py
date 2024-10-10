#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import random
from tqdm import tqdm
import skfmm
from shpmc.loss_functions import (
    loss_function_binary, 
    model_sign_dist_to_data, 
    loss_ordinary_procrustes_analysis,
    find_sketch_cross_section
    )


def level_set_perturbation(model_sign_dist_current, velocity_field, max_step):
    
    """
    
    Model perturbation using level set method
    This function is applicable to 2D and 3D cases.
    
    Parameters
    ----------
    model_sign_dist_current : array
        signed distance of the current model
    velocity_field : TYPE
        a gaussian field
    max_step : float
        a scale parameter to control the degree of model perturbation

    Returns
    -------
    model_sign_dist_candidate : array
        signed distance of the candidate model

    """
    
    ndim = velocity_field.ndim
    
    # Perturbation
    [_, F_eval] = skfmm.extension_velocities(
        model_sign_dist_current, 
        velocity_field, 
        dx = np.ones(ndim), 
        order = 1
        )
    
    # Step size
    step_i  = np.random.uniform(low=0, high=max_step, size=1)[0]
    dt = step_i / np.max(F_eval)
    delta_phi = dt * F_eval
    model_update = model_sign_dist_current - delta_phi # Advection
    model_sign_dist_candidate = skfmm.distance(model_update)
    
    return model_sign_dist_candidate    



class StochasticLevelSet3D(object):
    
    
    def __init__ (self, data, model_initial, gaussian_field, max_step, contribution):
        
        
        """
        
        Parameters
        ----------
        data : list
            multiple types of data, e.g., boreholes, outcrops, and geological sketches. Each data is an array.
        model_initial : array
            initial model
        gaussian_field : array
            gaussian field to guide the model perturbations
        max_step : float
            a scale parameter to control the degree of model perturbation
        contribution : int/float
            hyperparameter controls the contribution of the loss function
    
    
        """
        
        if not isinstance(data, list):
            raise TypeError("'data' must be a list!")
            
        if not isinstance(model_initial, list):
            raise TypeError("'model_initial' must be a list!")
            
        if not isinstance(contribution, list):
            raise TypeError("'contribution' must be a list!")
        
        assert len(data) == len(contribution), "The number of data sets and contributions must be the same!"
        
        self.data = data
        self.nd = len(data)
        # self.ndim = model_initial[0].ndim
        
        self.model = model_initial
        self.gaussian_field = gaussian_field
        self.max_step = max_step
        self.c = contribution
        
        
    def loss_computation(self, model_sign_dist):
        
        """
        
        Loss function computation for both binary observations (e.g., boreholes and outcrops) and geological sketches
        This function is applicable to the 3D case.

        Parameters
        ----------
        model_sign_dist_current : array
            signed distance of the current model

        Returns
        -------
        loss_total : float
            total loss value for multiple data sets
        loss_individual : array
            loss values for each data set

        """
        
        loss_individual = np.zeros(self.nd)
        
        for count, ele in enumerate(self.data):
            
            # Geological sketch
            if isinstance(ele, list):
                
                # Extract model profile to compare with the geological sketch
                comparision_shape = find_sketch_cross_section(
                    model = model_sign_dist, 
                    ind_ = ele[1], 
                    direction = ele[2]
                    )
                
                # Difference between reference shape (i.e., geological sketch) and comparison shape
                dist_procrustes, Z, translation = loss_ordinary_procrustes_analysis(ele[0], comparision_shape, self.c[count])
                loss_individual[count] = dist_procrustes
        
            # Binary observations, such as drillholes and outcrops
            else:
                obs, obs_sign_dist, obs_sign_dist_contact = model_sign_dist_to_data(
                    model_sign_dist, 
                    ele
                    )
            
                loss_individual[count] = loss_function_binary(
                    obs, 
                    obs_sign_dist, 
                    obs_sign_dist_contact, 
                    self.c[count]
                    )

        loss_total = np.sum(loss_individual)
        
        return loss_total, loss_individual


    def mcmc_sampling_single_chain(self, iter_num, temperature = 1):
        
        """
    
        Parameters
        ----------
        iter_num : int
            iteration number
        temperature : int
            temeprature value to relax loss function and improve acceptance ratio
            
        Returns
        -------
        list
            outputs from the sampling
            
        """
        
        assert len(self.model) == 1, "Single chain can only have one initial model!"
        
        # Initialization
        sample_models = np.zeros((iter_num, *self.model[0].shape))
        loss_values = np.zeros((iter_num, self.nd))
        
        model_sign_dist_current = skfmm.distance(self.model[0])
        loss_total_current, loss_individual_current = self.loss_computation(model_sign_dist_current)
        
        # Storing initials
        loss_values[0, :] = loss_individual_current
        sample_models[0, :] = model_sign_dist_current
        
        acceptance_count = 1
        
        for ii in tqdm(np.arange(iter_num-1)):
        
            # Create velocity fields
            velocity_field, theta = self.gaussian_field.field_3d
            
            # Model perturbation
            model_sign_dist_candidate = level_set_perturbation(model_sign_dist_current, velocity_field, self.max_step)
            
            # Loss function
            loss_total_candidate, loss_individual_candidate = self.loss_computation(model_sign_dist_candidate)
            
            acceptance_ratio = (loss_total_current**2 - loss_total_candidate**2) / temperature
            
            # Accept
            if np.log(np.random.uniform(0, 1)) <= acceptance_ratio:
                loss_values[ii+1, :] = loss_individual_candidate
                acceptance_count += 1
                model_sign_dist_current = model_sign_dist_candidate
                loss_total_current = loss_total_candidate
            
            # Reject
            else:
                loss_values[ii+1, :] = loss_values[ii, :]

            sample_models[ii+1, :] = model_sign_dist_current
    
        return loss_values, sample_models, acceptance_count
    