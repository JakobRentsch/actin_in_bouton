import tifffile as tiff
import matplotlib.pyplot as plt
from skimage import exposure
import numpy as np
import os

'''
- take the images (.tif) and zoom-ins from main figure and plot them all with same intensity scaling
- add 1 um scale bar
- export as .svg
'''

dir = ('/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Heatmap')
conditions = ['WT', 'TKO', 'FL', 'IDR']
pixel_size = 20 #nm

def tif_plotter(directory, condition, pixel_size):

    tif_stack = tiff.imread(directory + '/' + condition + '.tif')

    if tif_stack.dtype != 'uint8':
        tif_stack_uint8 = exposure.rescale_intensity(tif_stack, in_range='image', out_range='uint8').astype(np.uint8)

    else:
        tif_stack_uint8=tif_stack

    plt.imshow(tif_stack_uint8, cmap = 'plasma', vmin=0, vmax=150)
    plt.savefig(dir + '/' + condition + '.svg')
    plt.axis('off')
    cbar = plt.colorbar()
    cbar.set_label('Intensity (8bit)')
    plt.gca().set_aspect('equal')

    scale_bar = np.array([[20 , 20], [20 + 1000 / pixel_size , 20]])
    plt.plot(scale_bar[:, 0], scale_bar[:, 1], color = 'white', linewidth = 1)
    plt.savefig(dir + '/' + condition + '.svg')


n=1
for condition in conditions:
    plt.figure(n)
    tif_plotter(dir, condition, 20)
    n+=1
plt.show()
