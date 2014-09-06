import sys
import numpy as np
import matplotlib.pyplot as plt

initial = np.loadtxt(sys.argv[1],delimiter=' ')
final = np.loadtxt(sys.argv[2],delimiter=' ')
width = int(sys.argv[3])
height = int(sys.argv[4])

neuron_initial = [[[] for i in range(height)],[[] for i in range(height)]]
neuron_final   = [[[] for i in range(height)],[[] for i in range(height)]]

row = 0
for ii,w in enumerate(zip(initial,final)):
    print ii,row
    neuron_initial[ii%2][row].append(w[0])
    neuron_final[ii%2][row].append(w[1])
    if (ii > 0 and ii%2==0 and (ii/2)%width==0):
        row += 1

initial_up   = np.array(neuron_initial[0])
initial_down = np.array(neuron_initial[1])
final_up     = np.array(neuron_final[0])
final_down   = np.array(neuron_final[1])

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

plt.imshow(up_diff)
plt.imshow(down_diff)

plt.show()
