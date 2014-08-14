import math, sys
import AER
import pickle
import numpy as np
import matplotlib.pyplot as plt

class Neurons:
	def __init__(self,num):
		self.__tau = 5 #ms
		self.__Vt = 10000 #unit?
		self.__Tinhibit = 1.5 #ms
		self.__Trefrac = 10.0 #ms
		self.__winhibit = 500.0 #unit?
		self.__u      = [0 for i in range(num)]
		self.__spikes = [[] for i in range(num)]
		self.__synapses = [[] for i in range(num)]
		self.__tlast_update = [0 for i in range(num)]
		self.__tlast_spike  = [0 for i in range(num)]
		self.__num = num

		self.__record_membrane = False
		self.__membrane_record = [[(0,0,0)] for i in range(num)]

	def evolve(self,neuron_number,weight,t):
		if t > (max(self.__tlast_spike) + self.__Tinhibit):
			last_spike = self.__tlast_spike[neuron_number]
			if (t-last_spike) > self.__Trefrac:
				last_t = self.__tlast_update[neuron_number]
				last_u = self.__u[neuron_number]
				self.__u[neuron_number] = last_u*math.exp(-(t-last_t)/self.__tau) + weight
				self.__tlast_update[neuron_number] = t

				if self.__u[neuron_number] > self.__Vt:
					self.__tlast_spike[neuron_number] = t
					self.__spikes[neuron_number].append(t)
					self.update_synapses(neuron_number,t)
					for n in range(self.__num):
						self.__u[n] = 0

			if self.__record_membrane:
				self.__membrane_record[neuron_number].append((t,self.__u[neuron_number],weight))

	def update_synapses(self,neuron_number,t):
		for syn in self.__synapses[neuron_number]:
			syn(t)

	def get_spikes(self):
		return self.__spikes

	def get_membrane_potential(self):
		return self.__membrane_record

	def get_id(self):
		return self.__id

	def register_synapse(self,neuron,synapse_update):
		self.__synapses[neuron].append(synapse_update)

	def get_synapses(self,neuron):
		return self.__synapses[neuron]

class Neurons_softinhibit(Neurons):
	def __init__(self,num):
		super(Neurons_softinhibit,self).__init__(num)

	def evolve(self,neuron_number,weight,t):
		last_spike = self.__tlast_spike[neuron_number]
		if (t-last_spike) > self.__Trefrac:
			last_t = self.__tlast_update[neuron_number]
			last_u = self.__u[neuron_number]
			self.__u[neuron_number] = last_u*math.exp(-(t-last_t)/self.__tau) + weight
			self.__tlast_update[neuron_number] = t

			if self.__u[neuron_number] > self.__Vt:
				self.__tlast_spike[neuron_number] = t
				self.__spikes[neuron_number].append(t)
				self.update_synapses(neuron_number,t)
				for n in range(self.__num):
					if n == neuron_number:
						self.__u[n] = 0
					else:
						self.__u[n] -= self.__winhibit

		if self.__record_membrane:
			self.__membrane_record[neuron_number].append((t,self.__u[neuron_number],weight))

class Synapse:
	def __init__(self,id,neurons,post_neuron):
		self.__id = id
		self.__neurons = neurons
		self.__psn = post_neuron
		self.__w = np.random.normal(800,160)
		self.__last_pre_spike = 0
		self.__TLTP = 2 # ms
		self.__alpha_minus = np.random.normal(100,20)
		self.__alpha_plus = np.random.normal(50,10)
		self.__wmin = np.random.normal(1,0.2)
		self.__wmax = np.random.normal(1000,200)

		self.register_at_neuron()

	def pre(self,t):
		#print 'sending spike to neuron ',self.__psn,' with weight ',self.__w
		self.__last_pre_spike = t
		self.__neurons.evolve(self.__psn,self.__w,t)

	def register_at_neuron(self):
		self.__neurons.register_synapse(self.__psn,self.update)

	def update(self,t):
		if t-self.__last_pre_spike > self.__TLTP and self.__w > self.__wmin:
			self.__w -= self.__alpha_minus
		elif t-self.__last_pre_spike <= self.__TLTP and self.__w < self.__wmax:
			self.__w += self.__alpha_plus

		if self.__w > self.__wmax:
			self.__w = self.__wmax
		elif self.__w < self.__wmin:
			self.__w = self.__wmin

class DVSLoader:
	def __init__(self,filename):
		self.__data,self.__time = AER.load_AER(filename)
		self.__pointer = 0

	def get_events(self):
		while self.__pointer <= len(self.__data):
			self.__pointer += 1
			yield self.__time[self.__pointer-1],self.__data[self.__pointer-1]

class DVS:
	def __init__(self,image_width=28,image_height=28):
		self.__image_width = image_width
		self.__image_height = image_height
		self.__previous_image = np.zeros((self.__image_width,self.__image_height))

	def calculate_spikes(self,image):
		image_diff = image - self.__previous_image
		#print image_diff
		self.__previous_image = image
		return image_diff

class BallCamera:
	def __init__(self,angle,velocity,radius,image_width=28,image_height=28):
		self.image_width = image_width
		self.image_height = image_height
		self.__angle = angle
		self.__velocity = velocity
		self.__ball_radius = radius
		self.__start_time = 0
		self.calculate_ball_start()

	def generate_image(self,t):
		ball_center = np.array([math.cos(self.__angle),math.sin(self.__angle)])*self.__velocity*(t-self.__start_time) - self.__ball_start
		image = np.zeros((self.image_width,self.image_height))
		for x in range(self.image_width):
			for y in range(self.image_height):
				if self.distance(x,y,ball_center) < self.__ball_radius:
					image[x][y] = 1.0

		return image

	def distance(self,x,y,center):
		return math.sqrt(math.pow(x-center[0],2)+math.pow(y-center[1],2))

	def calculate_ball_start(self):
		self.__ball_start = np.array([math.cos(self.__angle),math.sin(self.__angle)])*self.__ball_radius*2

	def reset_and_angle(self,angle,t):
		self.__angle = angle
		self.__start_time = t
		self.calculate_ball_start()

if __name__  == '__main__':
	image_width = 16
	image_height = 16
	num_neurons = 48
	num_dvs_addresses = 2 * image_width * image_height
	dt = 1.0
	num_repetitions = 100

	dvs = DVS(image_width,image_height)
	cam = BallCamera(
            angle=math.pi/4,
            velocity=0.48,
            radius=6,
            image_width=image_width,
            image_height=image_height
        )
	neurons = Neurons(num_neurons)
	synapses = [[Synapse(i*num_dvs_addresses+j,neurons,j) for j in range(num_neurons)] for i in range(num_dvs_addresses)]


	time = 0
	for rep in range(num_repetitions):
		print 'rep ',rep
		for angle in range(0,360,45):
			cam.reset_and_angle(angle,time)
			for t in np.arange(0.0,100.0,dt):
				on_pixels = 0
				off_pixels = 0
				#print '-------- time = ' + str(time) + ' ----------'
				image = cam.generate_image(time)
				#plt.figure()
				#plt.imshow(image)
				image_diff = dvs.calculate_spikes(image)
				for row,pixels in enumerate(image_diff):
					for col,pixel in enumerate(pixels):
						if pixel > 0:
							on_pixels += 1
							for synapse in synapses[(row*image_width+col)*2]:
								synapse.pre(time)
							#print row,col,pixel
						elif pixel < 0:
							off_pixels += 1
							for synapse in synapses[(row*image_width+col)*2+1]:
								synapse.pre(time)
							#print row,col,pixel

				#print image_diff
				#print on_pixels, off_pixels
				time += dt
			# add a time-step of 100 ms between each run
			time += 100.0

	spikes = neurons.get_spikes()
	for n in range(num_neurons):
		#if len(spikes[n]) > 0:
		#	print n,len(spikes[n])
		plt.plot(spikes[n],np.ones(len(spikes[n]))*n,'o')
	for n in range(num_repetitions*8*2):
		plt.axvline(n*100)

	pickle.dump(spikes,open('spikes.dat','wb'))

	#plt.figure()
	#record = neurons.get_membrane_potential()
	#record = np.array(record)

	#for n in range(num_neurons):
	#	times = []
	#	membranes = []
	#	for tpl in record[n]:
	#		times.append(tpl[0])
	#		membranes.append(tpl[1])
	#	plt.plot(times,membranes)

	plt.show()

# vim: set noexpandtab
