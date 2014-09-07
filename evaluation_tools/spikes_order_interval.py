import argparse
import numpy as np
import matplotlib.pyplot as plt

def spikes_order_interval(filename,start,stop):
    # load spike data
    data = np.loadtxt(filename, delimiter=',')

    ret = []
    for sp in data:
        if sp[1] > stop:
            break
        if sp[1] >= start:
            ret.append(sp[0])

    return ret

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('--start', help='beginning of interval', type=float, dest='start')
    parser.add_argument('--stop', help='ending of interval', type=float, dest='stop')

    args=parser.parse_args()

    for sp in spikes_order_interval(args.filename, args.start, args.stop):
        print sp
