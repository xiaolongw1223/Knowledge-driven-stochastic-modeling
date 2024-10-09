#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 21:15:42 2023

@author: xwei2
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.size'] = 20
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

from discretize import TensorMesh
from SimPEG import maps

import h5py

def sigmoid(x, k, m):
  return 1 / (1 + np.exp(-k*(x-m)))

path_ = '../inputs/'

mesh = TensorMesh._readUBC_3DMesh(path_ + "mesh.txt")
ind_active = np.loadtxt(path_ + "syn_ind_active.txt", dtype=bool)
plotting_map = maps.InjectActiveCells(mesh, ind_active, np.nan)

hf = h5py.File('/Users/xwei2/Documents/My_work_Stanford/Crystal_lake/Synthetic/Level_set/borehole/Sampling_chain_borehole_5k_1.h5', 'r')
model_array = np.array(hf.get('model_dist'))
loss = np.array(hf.get('loss'))
hf.close()
model_array_cut = model_array[-1500:, :, :, :]
model_array_cut_unique = np.unique(model_array_cut, axis=0)

n = model_array_cut_unique.shape[0]
model_1d = np.zeros([mesh.nC, n])
model_dist_1d = np.zeros([mesh.nC, n])
model_dist_sigmoid_1d = np.zeros([mesh.nC, n])

for i in range(n):
    m_dist_1d = np.reshape(model_array_cut_unique[i, :, :, :], -1, order="F")
    
    # 1
    m = np.zeros(mesh.nC)
    m[np.where(m_dist_1d >= 0)[0]] = 1
    model_1d[:, i] = m
    
    # 2
    m = m_dist_1d
    model_dist_1d[:, i] = m
    
    # # 3
    # m = sigmoid(m_dist_1d, 1, 0) 
    # model_dist_sigmoid_1d[:, i] = m


np.savetxt('model_unique_1d.txt', model_1d)
np.savetxt('model_unique_dist_1d.txt', model_dist_1d)
np.savetxt('loss.txt', loss)

