#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: xwei2

"""

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 20
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
from discretize import TensorMesh

path_i = './inputs/'
path_o = './outputs/'

mesh = TensorMesh._readUBC_3DMesh(path_i + "mesh.txt")
ind_active = np.loadtxt(path_i + 'ind_active.txt', dtype=bool)

# Compute mean and std models
# For visualization, please refer to examples/02-drillholes-outcrops-3d
model = np.loadtxt(path_o + 'output_model_unique_1d.txt')

model_std = np.std(model, axis=-1)
model_std[~ind_active] = np.nan

model_mean = np.mean(model, axis=-1)
model_mean[~ind_active] = np.nan


#%% Loss function
loss = np.loadtxt(path_o + 'output_loss.txt')

fig = plt.figure(figsize=(10,4))
ax = plt.subplot()
ax.plot(loss, c='k', linewidth=2, label='Borehole')
ax.set_yscale('log')
ax.set_xlabel('Sampling steps')
ax.set_ylabel('Loss value')
plt.legend(loc='upper right', edgecolor='white')
plt.savefig(path_o + 'fig_loss.png', bbox_inches="tight", dpi=300)


#%% Drillholes
drillholes = mesh.read_model_UBC(path_i + 'drillholes.txt')
drillholes[np.where(drillholes==0.5)[0]] = 1
drillholes[np.where(drillholes==0)[0]] = np.nan

ind_list = [15, 25, 35, 38] # The index of drillhole locations at X cross-section

for i in range(len(ind_list)):
    
    # Plot standard deviation model with drillholes
    fig = plt.figure(figsize=(6,6))
    ax1 = plt.subplot(111)
    im = mesh.plot_slice(model_std, ax=ax1, normal='X', ind=ind_list[i],
                grid=False, clim=(-0.1, 0.6), pcolor_opts={"cmap":"RdBu_r"})
    mesh.plot_slice(drillholes, ax=ax1, normal='X', ind=ind_list[i],
                grid=False, clim=(0, 1), pcolor_opts={"cmap":"binary"})
    ax1.set_xlabel('Northing (m)')
    ax1.set_ylabel('Depth (m)')
    ax1.set_title('')
    ax1.set_title('Drillhole {}'.format(i+1), loc='left')
    ax1.set_aspect('2')
    ax1.ticklabel_format(useOffset=False, style="plain")
    ax1.locator_params(nbins=3, axis='x')
    pos1 = ax1.get_position()
    cb_ax = fig.add_axes([pos1.x0+0.7, pos1.y0+0.1, pos1.width *0.04, pos1.height*0.7])
    kwargs = {'format': '%.1f'}
    cb = plt.colorbar(im[0], cax=cb_ax, orientation="vertical", **kwargs)
    cb.set_label('Standard deviation', rotation=270, labelpad=20)
    plt.savefig(path_o + 'fig_model_std_drillhole_{}.png'.format(i), bbox_inches="tight", dpi=300)  

    # Plot mean model with drillholes
    fig = plt.figure(figsize=(6,6))
    ax1 = plt.subplot(111)
    im = mesh.plot_slice(model_mean, ax=ax1, normal='X', ind=ind_list[i],
                grid=False, clim=(-0.1, 1), pcolor_opts={"cmap":"RdBu_r"})
    mesh.plot_slice(drillholes, ax=ax1, normal='X', ind=ind_list[i],
                grid=False, clim=(0, 1), pcolor_opts={"cmap":"binary"})
    ax1.set_xlabel('Northing (m)')
    ax1.set_ylabel('Depth (m)')
    ax1.set_title('')
    ax1.set_title('Drillhole {}'.format(i+1), loc='left')
    ax1.set_aspect('2')
    ax1.ticklabel_format(useOffset=False, style="plain")
    ax1.locator_params(nbins=3, axis='x')
    pos1 = ax1.get_position()
    cb_ax = fig.add_axes([pos1.x0+0.7, pos1.y0+0.1, pos1.width *0.04, pos1.height*0.7])
    kwargs = {'format': '%.1f'}
    cb = plt.colorbar(im[0], cax=cb_ax, orientation="vertical", **kwargs)
    cb.set_label('Mean', rotation=270, labelpad=20)
    plt.savefig(path_o + 'fig_model_mean_drillhole_{}.png'.format(i), bbox_inches="tight", dpi=300)  
    


