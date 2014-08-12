import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

SEM_input_config = {}
SEM_input_config['image_width'] = 28
SEM_input_config['num_inputs'] = SEM_input_config['image_width']*SEM_input_config['image_width']
SEM_input_config['num_neuron'] = 10
# input image specs
SEM_input_config['input_on_rate'] = 40.0 # Hz
SEM_input_config['input_off_rate'] = 0.0 
SEM_input_config['time_on_image'] = 40.0 # ms
SEM_input_config['time_off_image'] = 10.0 # ms
SEM_input_config['probability_noise_on'] = 0.03
SEM_input_config['probability_gauss_on'] = 0.3
SEM_input_config['covariance_gauss_on'] = 10

SEM_input_config['centers'] = [[14,8],[16,22],[9,15],[20,14]]

def draw_image(center,config):
	noise = np.random.uniform(size=(config['image_width'],config['image_width']))
	signal_samples = np.random.uniform(size=(config['image_width'],config['image_width']))
	signal = np.zeros((config['image_width'],config['image_width']))

	for i in range(config['image_width']):
		for j in range(config['image_width']):
			#signal[i][j] = math.exp((-math.pow(i-center[0],2)-math.pow(j-center[1],2))/2.0/covariance_gauss_on)*probability_gauss_on
			if signal_samples[i][j]>(1-math.exp((-math.pow(i-center[0],2)-math.pow(j-center[1],2))/2.0/config['covariance_gauss_on'])*config['probability_gauss_on']):
				signal[i][j] = 1.0
			elif noise[i][j]>=(1-config['probability_noise_on']):
				signal[i][j] = 1.0

	#print len(signal[signal>0])
	return signal

def generate_input_spikes(image,config):
	y=[[] for i in range(config['num_inputs'])]

	for i in range(config['image_width']):
		for j in range(config['image_width']):
			spikes = []
			if image[i][j] > 0:
				t=0
				while t < config['time_on_image']:
					next_t = int(np.random.exponential(1./config['input_on_rate']*1000.))
					if (next_t+t) < config['time_on_image']:
						t += next_t
						spikes.append(t)
					else:
						break

			y[i*config['image_width']+j] = spikes

	return y

if __name__ == '__main__':
    # initialize membrane potentials
    u = np.zeros(SEM_input_config['num_neuron'])
    # initialize input neurons

    # initialize biases
    biases = np.zeros(SEM_input_config['num_neuron'])
    # initialize weights
    weights = np.random.uniform(size=(SEM_input_config['num_neuron'],SEM_input_config['num_inputs']))

    for i in range(4):
        image = draw_image(SEM_input_config['centers'][i%4],SEM_input_config)
        fig, ax = plt.subplots()
        cax = ax.imshow(image, cmap=cm.coolwarm)
        cbar = fig.colorbar(cax)
        plt.show()

        y = generate_input_spikes(image,SEM_input_config)
        for n in range(SEM_input_config['num_inputs']):
            plt.plot(y[n],np.ones_like(y[n])*n,'+')
        plt.show()

    #test = weights.dot(y)
    #u = biases + weights.dot(y)
    #
    #p = np.exp(u)
    #p = p/np.sum(p)
    #print p

