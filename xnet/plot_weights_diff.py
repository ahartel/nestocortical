import sys
import numpy as np
import matplotlib.pyplot as plt

initial = np.loadtxt(sys.argv[1],delimiter=' ')
final = np.loadtxt(sys.argv[2],delimiter=' ')
width = int(sys.argv[3])
height = int(sys.argv[4])

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

plt.imshow(complete_image)

plt.show()
