#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 15:12:38 2023

@author: xwei2
"""

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 16
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

from discretize import TensorMesh
import skfmm
from ShpMC.level_set_mc2 import StochasticLevelSet
from ShpMC.geo_stats import GaussianField

path_ = './inputs/'

mesh = TensorMesh._readUBC_3DMesh(path_ + "mesh.txt")

# Define data
drillholes = mesh.read_model_UBC(path_+'syn_drillholes_ternary_UBC.txt')
drillholes_3d = drillholes.reshape([mesh.shape_cells[0], mesh.shape_cells[1], mesh.shape_cells[2]], order='F')

boundary = mesh.read_model_UBC(path_+'syn_outcrop_ternary_UBC.txt')
boundary_3d = boundary.reshape([mesh.shape_cells[0], mesh.shape_cells[1], mesh.shape_cells[2]], order='F')

data_3d = [
    drillholes_3d, 
    boundary_3d
    ]

# Initial model
initial = mesh.read_model_UBC(path_ + 'syn_ellipsoid_initial_model_UBC.txt')
initial[np.isnan(initial)] = 0
initial_3d = initial.reshape([mesh.shape_cells[0], mesh.shape_cells[1], mesh.shape_cells[2]], order='F')
initial_3d = [initial_3d - 0.5]

# Define params for 3d gaussian random fields
gf = GaussianField(
    mean = [0, 0],
    variance = [1, 1],
    range_x = [2, 20], 
    range_y = [2, 20], 
    range_z = [2, 10], 
    anisotropy_xy = [0, 180],
    anisotropy_xz = [0, 180],
    x = mesh.cell_centers_x, 
    y = mesh.cell_centers_y, 
    z = mesh.cell_centers_z,
    random = True,
    output_params = True,
  )

# McMC level set
L = StochasticLevelSet(
    data_3d, 
    initial_3d, 
    gaussian_field=gf, 
    max_step=1, 
    contribution=[1, 0.1]
    )

loss_array, model_cache, acceptance_count = L.mcmc_sampling_single_chain(iter_num=5000, temperature=20)

# Save data
import h5py
num_chain = 1
hf = h5py.File('Sampling_chain_borehole_outcrop_5k_{}.h5'.format(num_chain), 'w')
hf.create_dataset('loss', data = loss_array)
hf.create_dataset('acceptance', data = acceptance_count)
hf.create_dataset('model_dist', data = model_cache)
hf.close()

plt.plot(loss_array)
