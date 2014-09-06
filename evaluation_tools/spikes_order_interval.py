import argparse
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('--start', help='beginning of interval', type=float, dest='start')
parser.add_argument('--stop', help='ending of interval', type=float, dest='stop')

args=parser.parse_args()

# load spike data
data = np.loadtxt(args.filename, delimiter=',')

for sp in data:
    if sp[1] > args.stop:
        break
    if sp[1] >= args.start:
        print sp[0]

