import sys
import pickle
import matplotlib.pyplot as plt
import numpy as np

data = pickle.load(open(sys.argv[1]))
image_width = 28
weights = {}

for line in data:
    try:
        weights[line[2]][line[0]][line[1]] = line[3]
    except KeyError:
        if not weights.has_key(line[2]):
            weights[line[2]] = np.zeros((image_width,image_width))
        weights[line[2]][line[0]][line[1]] = line[3]

for n,w in weights.items():
    plt.figure()
    #plt.hist(weights,bins=100)
    #cmap = plt.get_cmap('grey')
    plt.title(str(n))
    plt.imshow(w)
    plt.colorbar()

plt.show()
