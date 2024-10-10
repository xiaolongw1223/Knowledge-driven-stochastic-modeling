#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 21:15:42 2024

@author: xwei2
"""

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 20
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
from discretize import TensorMesh
import h5py

path_i = './inputs/'
path_o = './outputs/'

mesh = TensorMesh._readUBC_3DMesh(path_i + "mesh.txt")

hf = h5py.File(path_o + 'output_sampling_chain_1.h5', 'r')
model_array = np.array(hf.get('model_dist'))
loss = np.array(hf.get('loss'))
hf.close()

cut_off = 100
independence = -1*np.arange(0, cut_off, 2)
model_array_cut = model_array[independence, :, :, :]

n = model_array_cut.shape[0]
model_1d = np.zeros([mesh.nC, n])

for i in range(n):
    m_dist_1d = np.reshape(model_array_cut[i, :, :, :], -1, order="F")
    m = np.zeros_like(m_dist_1d)
    m[np.where(m_dist_1d >= 0)[0]] = 1
    model_1d[:, i] = m

np.savetxt(path_o + 'output_model_unique_1d.txt', model_1d)
np.savetxt(path_o + 'output_loss.txt', loss)

