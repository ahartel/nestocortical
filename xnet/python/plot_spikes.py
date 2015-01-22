import sys
import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt(sys.argv[1],delimiter=',',ndmin=2)

plt.plot(data[:,1],data[:,0],'o')
plt.grid()

plt.show()
