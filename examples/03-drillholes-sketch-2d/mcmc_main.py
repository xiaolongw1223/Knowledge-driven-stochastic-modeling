#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append('../../')
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 16
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

from discretize import TensorMesh
import skfmm
from tqdm import tqdm

from shpmc.level_set_mc import level_set_perturbation
from shpmc.geo_stats import GaussianField
from shpmc.loss_functions import (
    loss_function_binary, 
    model_sign_dist_to_data, 
    loss_ordinary_procrustes_analysis,
    )

#%% Initialization
path_i = './inputs/'
path_o = './outputs/'

# Construct mesh
dh = 1
hx = [(dh, 70)]
hz = [(dh, 50)]
mesh = TensorMesh([hx, hz], "00")
cell_centers = mesh.cell_centers

# Define data
drillholes_2d = np.loadtxt(path_i + 'drillhole_vertical.txt')
sketch_2d = np.loadtxt(path_i + 'sketch.txt')
sketch_coord = cell_centers[np.where(sketch_2d.reshape(-1, order='F')==1)[0], :]

# Initial model
initial_2d = np.loadtxt(path_i + 'initial_model.txt')
initial_2d = initial_2d - 0.5

# Define params for 3d gaussian random fields
gf = GaussianField(
    mean = [0, 0],
    variance = [1, 1],
    range_x = [1, 4], 
    range_y = [1, 4], 
    range_z = None, 
    anisotropy_xy = [0, 180],
    anisotropy_xz = None,
    x = mesh.cell_centers_x, 
    y = mesh.cell_centers_y, 
    z = None,
    random = True,
    output_params = True,
  )


# Parameters of MCMC
cd = 1 # Contribution of drillhole
cs = 5 # Contribution of sketch
temperature = 5
max_step = 1
iter_num = 5000
sample_models = np.zeros((iter_num, *mesh.shape_cells)) # change for 2d
loss_values = np.zeros((iter_num, 2))

model_sign_dist_current = skfmm.distance(initial_2d)

# Loss drillhole
obs, obs_sign_dist, obs_sign_dist_contact = model_sign_dist_to_data(model_sign_dist_current, drillholes_2d)
loss_drillhole = loss_function_binary(obs, obs_sign_dist, obs_sign_dist_contact, cd)

# Loss sketch
comparision_shape = np.zeros_like(sketch_2d)
comparision_shape[model_sign_dist_current>0] = 1
index = np.where(comparision_shape.reshape(-1, order='F')==1)[0]
comparision_shape_coord = cell_centers[index, :]
dist, Z, translation = loss_ordinary_procrustes_analysis(sketch_coord, comparision_shape_coord, cs)

# Loss total
loss_total_current = loss_drillhole + dist

# Storing initials
loss_individual_current = [loss_drillhole, dist]
loss_values[0, :] = loss_individual_current
sample_models[0, :] = model_sign_dist_current

acceptance_count = 1

#%% Level set MCMC
for ii in tqdm(np.arange(iter_num-1)):

    # Create velocity fields
    velocity_field, theta = gf.field_2d
    
    # Model perturbation
    model_sign_dist_candidate = level_set_perturbation(model_sign_dist_current, velocity_field, max_step)
    
    # Loss drillhole
    obs, obs_sign_dist, obs_sign_dist_contact = model_sign_dist_to_data(model_sign_dist_candidate, drillholes_2d)
    loss_drillhole = loss_function_binary(obs, obs_sign_dist, obs_sign_dist_contact, cd)
    
    # Loss sketch
    comparision_shape = np.zeros_like(sketch_2d)
    comparision_shape[model_sign_dist_candidate>0] = 1
    index = np.where(comparision_shape.reshape(-1, order='F')==1)[0]
    comparision_shape_coord = cell_centers[index, :]
    dist, Z, translation = loss_ordinary_procrustes_analysis(sketch_coord, comparision_shape_coord, cs)
    
    # Loss total
    loss_individual_candidate = [loss_drillhole, dist]
    loss_total_candidate = loss_drillhole + dist
    
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
    

#%% Save data
import h5py
num_chain = 2
hf = h5py.File(path_o + 'output_sampling_chain_{}.h5'.format(num_chain), 'w')
hf.create_dataset('loss', data = loss_values)
hf.create_dataset('acceptance', data = acceptance_count)
hf.create_dataset('model_dist', data = sample_models)
hf.close()


#%% Processing
cut_off = 2000
independence = -1*np.arange(0, cut_off, 2)
model_array_cut = sample_models[independence, :, :]

n = model_array_cut.shape[0]
model_1d = np.zeros([mesh.nC, n])
model_dist_1d = np.zeros([mesh.nC, n])

for i in np.arange(n):
    m_dist_1d = np.reshape(model_array_cut[i, :, :], -1, order="F")
    m = np.zeros(mesh.nC)
    m[np.where(m_dist_1d >= 0)[0]] = 1
    model_1d[:, i] = m


#%% Visualization
# Fig 1
labels=["Drillhole", "Sketch"]
fig = plt.figure(figsize=(6,4))
ax = plt.subplot()
ax.plot(np.sum(loss_values, -1), label="Total")   
for i in range(2):
    ax.plot(loss_values[:, i], label="{}".format(labels[i]))
ax.set_yscale('log')
ax.set_xlabel('Sampling steps')
ax.set_ylabel('Loss value')
plt.legend(loc='upper right', edgecolor='white', ncol=1)
plt.savefig(path_o +'fig_loss.png', bbox_inches="tight", dpi=300)


# Fig 2
std = np.std(model_1d, 1)
std_2d = std.reshape(mesh.shape_cells[0], mesh.shape_cells[1], order='F')
fig = plt.figure()
plt.imshow(std_2d.T, origin='lower')
plt.imshow(drillholes_2d.T, origin='lower', cmap='binary')
plt.xlabel('X')
plt.ylabel('Z')
plt.savefig(path_o + 'fig_std.png')

# Fig 3
mean = np.mean(model_1d, 1)
mean_2d = mean.reshape(mesh.shape_cells[0], mesh.shape_cells[1], order='F')
fig = plt.figure()
plt.imshow(mean_2d.T, origin='lower')
plt.imshow(drillholes_2d.T, origin='lower', cmap='binary')
plt.xlabel('X')
plt.ylabel('Z')
plt.savefig(path_o + 'fig_mean.png')


