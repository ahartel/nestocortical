import os, sys
sys.path.append('../../python')
import matplotlib.pyplot as plt
from benchmarks import ball_benchmark

benchmarks = ball_benchmark.BallBenchmark.check_and_load_state(80)
performance = benchmarks.evaluate_all()
#print performance
benchmarks.plot_performance()
plt.show()
