import numpy as np


import scipy.io
# from scipy import signal
# import matplotlib.pyplot as plt

all_frames_data = np.load('../mini_canne/didgeridoo_frames.npy')

# print(all_frames_data.shape[0])
# print(all_frames_data.shape[1])

# fs = 44100

# t = range(all_frames_data.shape[0])

# plt.pcolormesh(t, range(all_frames_data.shape[1]), all_frames_data)


scipy.io.savemat('matlab_frames.mat', mdict={'didg': all_frames_data})

#scipy.io.savemat('test.mat', all_frames_data)