import sys
import pickle
import matplotlib.pyplot as plt
import numpy as np

data = [pickle.load(open(sys.argv[1])),pickle.load(open(sys.argv[2]))]

image_width = 28
weights = [{},{}]
targets = []
diff = {}

for t in range(2):
    for line in data[t]:
        try:
            weights[t][line[2]][line[0]][line[1]] = line[3]
        except KeyError:
            if not weights[t].has_key(line[2]):
                targets.append(line[2])
                weights[t][line[2]] = np.zeros((image_width,image_width))
            weights[t][line[2]][line[0]][line[1]] = line[3]

for t in targets:
    diff[t] = np.subtract(weights[1][t],weights[0][t])

for n,w in diff.items():
    plt.figure()
    #plt.hist(weights,bins=100)
    #cmap = plt.get_cmap('grey')
    plt.title(str(n))
    plt.imshow(w)
    plt.colorbar()

plt.show()
