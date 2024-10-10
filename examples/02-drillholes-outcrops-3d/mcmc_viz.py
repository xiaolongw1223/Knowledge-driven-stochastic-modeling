#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 20
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
from discretize import TensorMesh


#%% Function
def beautify(title, fig=None):
    """Beautify the 3D Slicer result from SimPEG."""

    if fig is None:
        fig = plt.gcf()

    axs = fig.get_children()


    fig.suptitle(title, y=0.95, va="center")
    plt.setp(axs[1].yaxis.get_majorticklabels(), rotation=90)
    for label in axs[1].yaxis.get_ticklabels():
        label.set_visible(True)
    for label in axs[1].yaxis.get_ticklabels()[::3]:
        label.set_visible(True)
    axs[1].set_ylabel("Northing (m)")
    axs[1].locator_params(nbins=2, axis='y')

    # Adjust x- and y-labels on the second subplot (XZ)
    axs[2].set_xlabel("Easting (m)")
    plt.setp(axs[2].yaxis.get_majorticklabels(), rotation=90)
    axs[2].set_ylabel("Depth (m)")

    # Adjust x-labels on the third subplot (ZY)
    axs[3].set_xlabel("Depth (m)")

    # Adjust colorbar
    axs[4].set_ylabel(" ", rotation=270, labelpad=20)

    # Ensure sufficient margins so nothing is clipped
    plt.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.9)


#%% Read files
path_i = './inputs/'
path_o = './outputs/'

mesh = TensorMesh._readUBC_3DMesh(path_i + "mesh.txt")
ind_active = np.loadtxt(path_i + 'ind_active.txt', dtype=bool)

# Outcrops contact locations for visualization
outcrops = mesh.read_model_UBC(path_i + "outcrops.txt")
outcrops_contact_ind = np.where(outcrops==0.5)[0]
outcrops_contact_coord = mesh.cell_centers[outcrops_contact_ind, :]

# Drillholes locations on the surface for visualization
drillholes_coord = np.loadtxt(path_i + "drillholes_coordinate.txt")

# Compute mean and std models
# For visualization, please refer to examples/02-drillholes-outcrops-3d
model = np.loadtxt(path_o + 'output_model_unique_1d.txt')

model_std = np.std(model, axis=-1)
model_std[~ind_active] = np.nan

model_mean = np.mean(model, axis=-1)
model_mean[~ind_active] = np.nan


#%% Drillholes and outcrops
slice_x_ind, slice_y_ind, slice_z_ind = 20, 27, 25

slice_x = mesh.cell_centers_x[slice_x_ind]
slice_y = mesh.cell_centers_y[slice_y_ind]
slice_z = mesh.cell_centers_z[slice_z_ind]

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
axs[1].scatter(*zip(*outcrops_contact_coord[:,0:2]), c='k', s=10)
axs[1].scatter(*zip(*drillholes_coord[:,0:2]), c='yellow', s=100, marker='*')
beautify("", fig = fig)
plt.savefig(path_o + 'fig_model_std.png', bbox_inches="tight", dpi=300)  


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
axs[1].scatter(*zip(*outcrops_contact_coord[:,0:2]), c='k', s=10)
axs[1].scatter(*zip(*drillholes_coord[:,0:2]), c='yellow', s=100, marker='*')
beautify("", fig = fig)
plt.savefig(path_o + 'fig_model_mean.png', bbox_inches="tight", dpi=300)  


#%% Loss function
loss = np.loadtxt(path_o + 'output_loss.txt')
labels=["Drillholes", "Outcrops"]

fig = plt.figure(figsize=(10,4))
ax = plt.subplot()
plt.plot(np.sum(loss, -1), label="Total")   
for i in range(len(labels)):
    plt.plot(loss[:, i], label="{}".format(labels[i]))
ax.set_yscale('log')
ax.set_xlabel('Sampling steps')
ax.set_ylabel('Loss value')
plt.legend(loc='upper right', edgecolor='white', ncol=2)
plt.savefig(path_o +'fig_loss.png', bbox_inches="tight", dpi=300)