import sys
import math
import os.path
import argparse
import numpy as np
import matplotlib.pyplot as plt
sys.path.append('../evaluation_tools/')
from spikes_order_interval import spikes_order_interval

parser = argparse.ArgumentParser()
parser.add_argument('--file-spikes')
parser.add_argument('--file-weights')
parser.add_argument('--start', help='beginning of interval', type=float, dest='start')
parser.add_argument('--stop', help='ending of interval', type=float, dest='stop')
parser.add_argument('--width', help='width of image for weight reconstruction', type=int)
parser.add_argument('--height', help='height of image for weight reconstruction', type=int)

args=parser.parse_args()

# get neurons that have fired in intervall
neurons = spikes_order_interval(os.path.abspath(args.file_spikes), args.start, args.stop)
plt.figure()
plt.suptitle(neurons)

x = int(math.sqrt(len(neurons)))
y = int(len(neurons)/x)
if x*y<len(neurons):
    if x<y:
        x += 1
    else:
        y += 1
sp_base = (x,y)
print sp_base

for n,neuron in enumerate(neurons):
    print n,neuron
    initial = np.loadtxt(args.file_weights+'_weights_initial.txt'+str(int(neuron)),delimiter=' ')
    final = np.loadtxt(args.file_weights+'_weights_final.txt'+str(int(neuron)),delimiter=' ')
    width = args.width
    height = args.height

    neuron_initial = [np.zeros((width,height)), np.zeros((width,height))]
    neuron_final   = [np.zeros((width,height)), np.zeros((width,height))]

    row = 0
    col = 0
    for ii,w in enumerate(zip(initial,final)):
        #print ii,row,col
        neuron_initial[ii%2][row][col] = w[0]
        neuron_final  [ii%2][row][col] = w[1]
        if (ii > 0 and (ii+1)%2==0 and ((ii+1)/2)%width==0):
            row += 1
            col = 0
        elif ii%2==1:
            col += 1

    initial_up   = neuron_initial[0]
    initial_down = neuron_initial[1]
    final_up     = neuron_final[0]
    final_down   = neuron_final[1]

    up_diff = final_up - initial_up
    potentiated = up_diff >  0
    depressed   = up_diff <= 0
    up_diff[potentiated] = 1
    up_diff[depressed]   = 0

    down_diff = final_down - initial_down
    potentiated = down_diff >  0
    depressed   = down_diff <= 0
    down_diff[potentiated] = 1
    down_diff[depressed]   = 0

    complete_image = up_diff + 2*down_diff

    plt.subplot(sp_base[0],sp_base[1],n+1)
    plt.title(neuron)
    plt.imshow(complete_image)

plt.colorbar()
plt.show()
