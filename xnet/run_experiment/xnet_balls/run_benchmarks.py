import os, sys
sys.path.append('../../python')
from benchmarks import ball_benchmark

num_repetitions = 800

benchmarks = ball_benchmark.BallBenchmark(num_repetitions)
benchmarks.append('rect_hard_nodelay','../../bin/xnet_balls_rect 0')
benchmarks.append('rect_hard_delays','../../bin/xnet_balls_rect 10')
benchmarks.evaluate_all()
benchmarks.save()
