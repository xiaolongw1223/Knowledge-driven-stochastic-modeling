#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 21:15:42 2023

@author: xwei2
"""

import pandas as pd
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib

plt.rcParams['font.size'] = 20
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

from discretize import TensorMesh
from SimPEG import maps

#%% Function
def beautify(title, fig=None):
    """Beautify the 3D Slicer result."""

    # Get figure handle if not provided
    if fig is None:
        fig = plt.gcf()

    # Get principal figure axes
    axs = fig.get_children()

    # Set figure title
    fig.suptitle(title, y=0.95, va="center")

    # Adjust the y-labels on the first subplot (XY)
    plt.setp(axs[1].yaxis.get_majorticklabels(), rotation=90)
    for label in axs[1].yaxis.get_ticklabels():
        label.set_visible(True)
    for label in axs[1].yaxis.get_ticklabels()[::3]:
        label.set_visible(True)
    axs[1].set_ylabel("Northing (m)")
    # axs[1].set_title('(a)', loc='right')
    axs[1].locator_params(nbins=2, axis='y')

    # Adjust x- and y-labels on the second subplot (XZ)
    axs[2].set_xlabel("Easting (m)")
    plt.setp(axs[2].yaxis.get_majorticklabels(), rotation=90)
    axs[2].set_ylabel("Depth (m)")
    # axs[2].set_title('(b)', loc='left')

    # Adjust x-labels on the third subplot (ZY)
    axs[3].set_xlabel("Depth (m)")
    # axs[3].set_title('(c)', loc='left')

    # Adjust colorbar
    # axs[4].set_ylabel("Standard deviation", rotation=270, labelpad=20)
    axs[4].set_ylabel("")
    # axs[4].set_ylabel("Sigmoid signed distance")

    # Ensure sufficient margins so nothing is clipped
    plt.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.9)



#%% Read files
path_ = '../inputs/'

mesh = TensorMesh._readUBC_3DMesh(path_ + "mesh.txt")
ind_active = np.loadtxt(path_ + "syn_ind_active.txt", dtype=bool)
plotting_map = maps.InjectActiveCells(mesh, ind_active, np.nan)

slice_z_ind = 25
slice_z = mesh.cell_centers_z[slice_z_ind]
slice_y_ind = 27
slice_y = mesh.cell_centers_y[slice_y_ind]
slice_x_ind = 20
slice_x = mesh.cell_centers_x[slice_x_ind]

outcrop = mesh.read_model_UBC(path_ + "syn_outcrop_ternary_UBC.txt")
outcrop_ind = np.where(outcrop==0.5)[0]
outcrop_x, outcrop_y, outcrop_z = mesh.cell_centers[outcrop_ind, 0], mesh.cell_centers[outcrop_ind, 1], mesh.cell_centers[outcrop_ind, 2]
# # outcrop_ind_topo = np.where(outcrop_z>slice_z)[0]
# # outcrop_x, outcrop_y = outcrop_x[outcrop_ind_topo], outcrop_y[outcrop_ind_topo]

borehole_coord = np.loadtxt(path_ + "syn_drillhole_locs.txt")


#%% Plot all models for GIF
model = np.loadtxt('model_unique_1d.txt')

n = model.shape[0]


model_std = np.std(model, axis=-1)
model_std = model_std[ind_active]
model_std = plotting_map * model_std

fig = plt.figure(figsize=(6,6))
mesh.plot_3d_slicer(
    model_std,
    xslice = slice_x,
    yslice = slice_y,
    zslice = slice_z,
    clim=(-0.1, 0.6),
    v_type = "CC",
    view = "real",
    axis = "xy",
    aspect = "auto",
    pcolor_opts = {"cmap": "RdBu_r"},
    fig = fig
    )

axs = fig.get_children()
axs[1].scatter(outcrop_x, outcrop_y, c='k', s=10)
axs[1].scatter(borehole_coord[:, 0], borehole_coord[:, 1], c='yellow', s=100, marker='*')
beautify("", fig = fig)
plt.savefig('fig_model_std.png', bbox_inches="tight", dpi=300)  


model_mean = np.mean(model, axis=-1)
model_mean = model_mean[ind_active]
model_mean = plotting_map * model_mean

fig = plt.figure(figsize=(6, 6))
mesh.plot_3d_slicer(
    model_mean,
    xslice = slice_x,
    yslice = slice_y,
    zslice = slice_z,
    clim=(-0.1, 1),
    v_type = "CC",
    view = "real",
    axis = "xy",
    aspect = "auto",
    pcolor_opts = {"cmap": "RdBu_r"},
    fig = fig
    )

axs = fig.get_children()
axs[1].scatter(outcrop_x, outcrop_y, c='k', s=10)
axs[1].scatter(borehole_coord[:, 0], borehole_coord[:, 1], c='yellow', s=100, marker='*')
beautify("", fig = fig)
plt.savefig('fig_model_mean.png', bbox_inches="tight", dpi=300)  



#%% Model signed distance standard deviation and mean

model_dist = np.loadtxt('model_unique_dist_1d.txt')

model_dist_std = np.std(model_dist, axis=-1)
model_dist_std = model_dist_std[ind_active]
model_dist_std = plotting_map * model_dist_std

fig = plt.figure(figsize=(6, 6))
mesh.plot_3d_slicer(
    model_dist_std,
    xslice = slice_x,
    yslice = slice_y,
    zslice = slice_z,
    # clim=(-0.1, 0.6),
    v_type = "CC",
    view = "real",
    axis = "xy",
    aspect = "auto",
    pcolor_opts = {"cmap": "RdBu_r"},
    fig = fig
    )

axs = fig.get_children()
axs[1].scatter(outcrop_x, outcrop_y, c='k', s=10)
axs[1].scatter(borehole_coord[:, 0], borehole_coord[:, 1], c='yellow', s=100, marker='*')
beautify("", fig = fig)
plt.savefig('fig_dist_std.png', bbox_inches="tight", dpi=300)  


model_dist_mean = np.mean(model_dist, axis=-1)
model_dist_mean = model_dist_mean[ind_active]
model_dist_mean = plotting_map * model_dist_mean

fig = plt.figure(figsize=(10, 6))
mesh.plot_3d_slicer(
    model_dist_mean,
    xslice = slice_x,
    yslice = slice_y,
    zslice = slice_z,
    # clim=(-0.1, 1),
    v_type = "CC",
    view = "real",
    axis = "xy",
    aspect = "auto",
    pcolor_opts = {"cmap": "RdBu_r"},
    fig = fig
    )

axs = fig.get_children()
axs[1].scatter(outcrop_x, outcrop_y, c='k', s=10)
axs[1].scatter(borehole_coord[:, 0], borehole_coord[:, 1], c='yellow', s=100, marker='*')
beautify("", fig = fig)
plt.savefig('fig_dist_mean.png', bbox_inches="tight", dpi=300)  
 


#%% Drillholes
drillholes = mesh.read_model_UBC(path_+'syn_drillholes_ternary_UBC.txt')

drillholes[np.where(drillholes==0.5)[0]] = 1
drillholes[np.where(drillholes==0)[0]] = np.nan

drillholes = drillholes[ind_active]
drillholes = plotting_map * drillholes

ind_list = [15, 25, 35, 38]

# Models
for i in range(len(ind_list)):
    fig = plt.figure(figsize=(6,6))
    ax1 = plt.subplot(111)
    im = mesh.plot_slice(model_std, ax=ax1, normal='X', ind=ind_list[i],
                grid=False, clim=(-0.1, 0.6), pcolor_opts={"cmap":"RdBu_r"})
    mesh.plot_slice(drillholes, ax=ax1, normal='X', ind=ind_list[i],
                grid=False, clim=(0, 1), pcolor_opts={"cmap":"binary"})
    ax1.set_xlabel('Northing (m)')
    ax1.set_ylabel('Depth (m)')
    ax1.set_title('')
    ax1.set_title('Borehole {}'.format(i+1), loc='left')
    ax1.set_aspect('2')
    ax1.ticklabel_format(useOffset=False, style="plain")
    ax1.locator_params(nbins=3, axis='x')
    pos1 = ax1.get_position()
    
    cb_ax = fig.add_axes([pos1.x0+0.7, pos1.y0+0.1, pos1.width *0.04, pos1.height*0.7])
    kwargs = {'format': '%.1f'}
    cb = plt.colorbar(im[0], cax=cb_ax, orientation="vertical", **kwargs)
    cb.set_label('Standard deviation', rotation=270, labelpad=20)

    plt.savefig('fig_model_std_borehole_{}.png'.format(i), bbox_inches="tight", dpi=300)  



    fig = plt.figure(figsize=(6,6))
    ax1 = plt.subplot(111)
    im = mesh.plot_slice(model_mean, ax=ax1, normal='X', ind=ind_list[i],
                grid=False, clim=(-0.1, 1), pcolor_opts={"cmap":"RdBu_r"})
    mesh.plot_slice(drillholes, ax=ax1, normal='X', ind=ind_list[i],
                grid=False, clim=(0, 1), pcolor_opts={"cmap":"binary"})
    ax1.set_xlabel('Northing (m)')
    ax1.set_ylabel('Depth (m)')
    ax1.set_title('')
    ax1.set_title('Borehole {}'.format(i+1), loc='left')
    ax1.set_aspect('2')
    ax1.ticklabel_format(useOffset=False, style="plain")
    ax1.locator_params(nbins=3, axis='x')
    pos1 = ax1.get_position()
    
    cb_ax = fig.add_axes([pos1.x0+0.7, pos1.y0+0.1, pos1.width *0.04, pos1.height*0.7])
    kwargs = {'format': '%.1f'}
    cb = plt.colorbar(im[0], cax=cb_ax, orientation="vertical", **kwargs)
    cb.set_label('Mean', rotation=270, labelpad=20)

    plt.savefig('fig_model_mean_borehole_{}.png'.format(i), bbox_inches="tight", dpi=300)  
    
    
    
# Signed distance
for i in range(len(ind_list)):
    fig = plt.figure(figsize=(6,6))
    ax1 = plt.subplot(111)
    im = mesh.plot_slice(model_dist_std, ax=ax1, normal='X', ind=ind_list[i],
                grid=False, pcolor_opts={"cmap":"RdBu_r"})
    mesh.plot_slice(drillholes, ax=ax1, normal='X', ind=ind_list[i],
                grid=False, clim=(0, 1), pcolor_opts={"cmap":"binary"})
    ax1.set_xlabel('Northing (m)')
    ax1.set_ylabel('Depth (m)')
    ax1.set_title('')
    ax1.set_title('Borehole {}'.format(i+1), loc='left')
    ax1.set_aspect('2')
    ax1.ticklabel_format(useOffset=False, style="plain")
    ax1.locator_params(nbins=3, axis='x')
    pos1 = ax1.get_position()
    
    cb_ax = fig.add_axes([pos1.x0+0.7, pos1.y0+0.1, pos1.width *0.04, pos1.height*0.7])
    kwargs = {'format': '%.1f'}
    cb = plt.colorbar(im[0], cax=cb_ax, orientation="vertical", **kwargs)
    cb.set_label('Standard deviation', rotation=270, labelpad=20)

    plt.savefig('fig_dist_std_borehole_{}.png'.format(i), bbox_inches="tight", dpi=300)  



for i in range(len(ind_list)):
    fig = plt.figure(figsize=(6,6))
    ax1 = plt.subplot(111)
    im = mesh.plot_slice(model_dist_mean, ax=ax1, normal='X', ind=ind_list[i],
                grid=False, pcolor_opts={"cmap":"RdBu_r"})
    mesh.plot_slice(drillholes, ax=ax1, normal='X', ind=ind_list[i],
                grid=False, clim=(0, 1), pcolor_opts={"cmap":"binary"})
    ax1.set_xlabel('Northing (m)')
    ax1.set_ylabel('Depth (m)')
    ax1.set_title('')
    ax1.set_title('Borehole {}'.format(i+1), loc='left')
    ax1.set_aspect('2')
    ax1.ticklabel_format(useOffset=False, style="plain")
    ax1.locator_params(nbins=3, axis='x')
    pos1 = ax1.get_position()
    
    cb_ax = fig.add_axes([pos1.x0+0.7, pos1.y0+0.1, pos1.width *0.04, pos1.height*0.7])
    kwargs = {'format': '%.1f'}
    cb = plt.colorbar(im[0], cax=cb_ax, orientation="vertical", **kwargs)
    cb.set_label('Mean', rotation=270, labelpad=20)

    plt.savefig('fig_dist_mean_borehole_{}.png'.format(i), bbox_inches="tight", dpi=300)  

    
#%% Loss function

loss = np.loadtxt('loss.txt')
fig = plt.figure(figsize=(10,4))
ax = plt.subplot()
ax.plot(loss, c='k', linewidth=2, label='Borehole')
ax.set_yscale('log')
ax.set_xlabel('Sampling steps')
ax.set_ylabel('Loss vvalue')
plt.legend(loc='upper right', edgecolor='white')
plt.savefig('fig_loss.png', bbox_inches="tight", dpi=300)


