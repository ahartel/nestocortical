#include <map>
#include <vector>
#include <tuple>
#include <algorithm>
#include <math.h>
#include <iostream>
#include <fstream>
#include <random>
#include "xnet_types.h"

#define EPSILON 0.0001

using namespace std;

class Synapse;

class Neurons
{
	private:
		vector<tuple<float,float>> spikes;
		vector<vector<Synapse*>> synapses;
		vector<vector<tuple<float,float,float>>> membrane_record;
		vector<float> u;
		vector<Time_t> tlast_update, tlast_spike;
		float tau, Vt;
		int num;
		float Tinhibit, Trefrac, winhibit;
		bool record_membrane;

	public:
	Neurons(int num) : u(num,0.0), membrane_record(num), tlast_update(num,0.0), tlast_spike(num,0.0), synapses(num)
	{
		this->tau = 5; //ms
		this->Vt = 10000; //unit?
		this->Tinhibit = 1.5; //ms
		this->Trefrac = 10.0; //ms
		this->winhibit = 500.0; //unit?
		this->num = num;
		this->record_membrane = false;
		// not necessary for this type:
		//this->spikes = [[] for i in range(num)]
		//this->synapses = [[] for i in range(num)]
		//this->tlast_update = [0 for i in range(num)]
		//this->tlast_spike  = [0 for i in range(num)]

		for (int i=0; i<num; ++i)
		{
			this->membrane_record[i].push_back(make_tuple(0.0,0.0,0.0));
		}
	}

	void evolve(int neuron_number, float weight, Time_t t)
	{
		if (t > (*max_element(tlast_spike.begin(),tlast_spike.end()) + Tinhibit) || t < EPSILON)
		{
			float last_spike = tlast_spike[neuron_number];
			if (((t-last_spike) > Trefrac) || t < EPSILON)
			{
				float last_t = tlast_update[neuron_number];
				float last_u = u[neuron_number];
				u[neuron_number] = last_u*exp(-(t-last_t)/tau) + weight;
				tlast_update[neuron_number] = t;

				if (u[neuron_number] > Vt)
				{
					tlast_spike[neuron_number] = t;
					spikes.push_back(make_tuple(neuron_number,t));
					update_synapses(neuron_number,t);
					for (int n=0; n < num; ++n)
						u[n] = 0;
				}
			}
			if (this->record_membrane)
				this->membrane_record[neuron_number].push_back(make_tuple(t,this->u[neuron_number],weight));
		}
	}

	void update_synapses(int neuron_number, Time_t t);

	vector<tuple<float,float>> get_spikes() const {
		return this->spikes;
	}

	vector<vector<tuple<float,float,float>>> get_membrane_potential()
	{
		return this->membrane_record;
	}

	void register_synapse(unsigned int neuron, Synapse* synapse)
	{
		this->synapses[neuron].push_back(synapse);
	}

	vector<Synapse*> get_synapses(int neuron) const
	{
		return this->synapses[neuron];
	}
};

//class Neurons_softinhibit(Neurons):
//	def __init__(self,num):
//		super(Neurons_softinhibit,self).__init__(num)
//
//	def evolve(self,neuron_number,weight,t):
//		last_spike = self.__tlast_spike[neuron_number]
//		if (t-last_spike) > self.__Trefrac:
//			last_t = self.__tlast_update[neuron_number]
//			last_u = self.__u[neuron_number]
//			self.__u[neuron_number] = last_u*math.exp(-(t-last_t)/self.__tau) + weight
//			self.__tlast_update[neuron_number] = t
//
//			if self.__u[neuron_number] > self.__Vt:
//				self.__tlast_spike[neuron_number] = t
//				self.__spikes[neuron_number].append(t)
//				self.update_synapses(neuron_number,t)
//				for n in range(self.__num):
//					if n == neuron_number:
//						self.__u[n] = 0
//					else:
//						self.__u[n] -= self.__winhibit
//
//		if self.__record_membrane:
//			self.__membrane_record[neuron_number].append((t,self.__u[neuron_number],weight))

class Synapse
{
	private:
		Neurons& neurons;
		unsigned int psn, id;
		float w, wmin, wmax;
		Time_t last_pre_spike;
		float alpha_minus, alpha_plus;
		Time_t TLTP;


	public:

	Synapse(unsigned int i, Neurons& neurons_ref, unsigned int post_neuron) :
			neurons(neurons_ref),
			psn(post_neuron),
			id(i),
			last_pre_spike(0)
	{
		w = 800; // TODO: should be normally distributed with mu=800, sigma=160
		TLTP = 2; // ms
		alpha_minus = 100; // TODO: should be normally distributed with mu=100, std=20
		alpha_plus  = 50; // TODO: should be normally distributed with mu=50, std=10
		wmin = 1.0; // TODO: should be normally distributed with mu=1.0, std=0.2
		wmax = 1000.0; // TODO: should be normally distributed with mu=1000, std=200

		register_at_neuron();
	}

	Synapse(unsigned int i,
		    Neurons& neurons_ref,
		    unsigned int post_neuron,
		    float weight=800.0,
		    float aminus=100.0,
		    float aplus=50.0,
			float wmin_=1.0,
			float wmax_=1000.0
		) : neurons(neurons_ref),
			psn(post_neuron),
			id(i),
			last_pre_spike(0),
			w(weight),
			alpha_minus(aminus),
			alpha_plus(aplus),
			wmin(wmin_),
			wmax(wmax_)
	{
		TLTP = 2; // ms

		register_at_neuron();
	}

//	def __init__(self,id,neurons,post_neuron):
//		self.__w = np.random.normal(800,160)
//		self.__last_pre_spike = 0
//		self.__TLTP = 2 # ms
//		self.__alpha_minus = np.random.normal(100,20)
//		self.__alpha_plus = np.random.normal(50,10)
//		self.__wmin = np.random.normal(1,0.2)
//		self.__wmax = np.random.normal(1000,200)
//
//		self.register_at_neuron()

	void pre(Time_t t)
	{
		last_pre_spike = t;
		neurons.evolve(psn,w,t);
	}
//	def pre(self,t):
//		#print 'sending spike to neuron ',self.__psn,' with weight ',self.__w
//		self.__last_pre_spike = t
//		self.__neurons.evolve(self.__psn,self.__w,t)

	void register_at_neuron()
	{
		neurons.register_synapse(psn, this);
	}
//	def register_at_neuron(self):
//		self.__neurons.register_synapse(self.__psn,self.update)

	void update(Time_t t)
	{
		if (t-last_pre_spike > TLTP && w > wmin)
		{
			w -= alpha_minus;
		}
		else if (t-last_pre_spike <= TLTP && w < wmax)
		{
			w += alpha_plus;
		}

		if (w > wmax)
			w = wmax;
		else if (w < wmin)
			w = wmin;
	}
//	def update(self,t):
//		if t-self.__last_pre_spike > self.__TLTP and self.__w > self.__wmin:
//			self.__w -= self.__alpha_minus
//		elif t-self.__last_pre_spike <= self.__TLTP and self.__w < self.__wmax:
//			self.__w += self.__alpha_plus
//
//		if self.__w > self.__wmax:
//			self.__w = self.__wmax
//		elif self.__w < self.__wmin:
//			self.__w = self.__wmin
};

void Neurons::update_synapses(int neuron_number, Time_t t)
{
	for (auto syn : this->synapses[neuron_number])
		syn->update(t);
}


class DVS
{
private:
	vector<vector<bool>> previous_image;
	int image_width, image_height;

public:
	DVS(int image_width, int image_height) : previous_image(image_height,vector<bool>(image_width,false))
	{
		this->image_width = image_width;
		this->image_height = image_height;
	}

	vector<vector<int>> calculate_spikes(vector<vector<bool>> image)
	{
		vector<vector<int>> image_diff (image_height,vector<int>(image_width,0) );
		for (int x=0; x<image_width; ++x)
		{
			for (int y=0; y<image_height; ++y)
			{
				image_diff[y][x] = int(image[y][x]) - int(previous_image[y][x]);
			}
		}
		previous_image = image;
		return image_diff;
	}
};

class BallCamera
{
private:
	int image_width, image_height;
	float angle, velocity, ball_radius, start_time;
	vector<double> ball_start;

public:
	BallCamera(float angle, float velocity, float radius, int image_width=28, int image_height=28)
	{
		this->image_width = image_width;
		this->image_height = image_height;
		this->angle = angle;
		this->velocity = velocity;
		this->ball_radius = radius;
		this->start_time = 0;
		calculate_ball_start();
	}

	vector<vector<bool>> generate_image(float t)
	{
		cout << ball_start[0] << "," << ball_start[1] << endl;
		vector<double> ball_center = {
			cos(angle)*velocity*(t-start_time) - ball_start[0],
			sin(angle)*velocity*(t-start_time) - ball_start[1]
		};
		cout << ball_center[0] << "," << ball_center[1] << endl;
		vector<vector<bool>> image(image_height,vector<bool>(image_width,false) );
		//unsigned int cnt = 0;
		for (int x=0; x<image_width; ++x)
		{
			for (int y=0; y<image_height; ++y)
			{
				if (distance(x,y,ball_center) < ball_radius)
				{
					//++cnt;
					image[y][x] = true;
				}
			}
		}
		return image;
	}

	float distance(float x, float y, vector<double> center)
	{
		float dist = sqrt(pow(x-center[0],2)+pow(y-center[1],2));
		//cout << dist << endl;
		return dist;
	}

	void calculate_ball_start()
	{
		ball_start = {cos(angle)*ball_radius*2.0,sin(angle)*ball_radius*2.0};
	}

	void reset_and_angle(float angle, float t)
	{
		this->angle = angle;
		this->start_time = t;
		calculate_ball_start();
	}
};

int main()
{
	int image_width = 16;
	int image_height = 16;
	int num_neurons = 48;
	int num_dvs_addresses = 2 * image_width * image_height;
	float dt = 1.0;
	int	num_repetitions = 100;

	DVS dvs(image_width,image_height);
	BallCamera cam {
            3.1416/4.,
            0.48,
            6.0,
            image_width,
            image_height
	};

//	neurons = Neurons_softinhibit(num_neurons)
	Neurons neurons(num_neurons);

	std::default_random_engine generator;
	std::normal_distribution<float> weight_distribution(800.0,160.0);
	std::normal_distribution<float> am_distribution(100.0,20.0);
	std::normal_distribution<float> ap_distribution(50.0,10.0);
	std::normal_distribution<float> wmin_distribution(1.0,0.2);
	std::normal_distribution<float> wmax_distribution(1000.0,200.0);

	vector<vector<Synapse>> synapses;
	for (int i=0; i<num_dvs_addresses; ++i)
	{
		synapses.push_back({});
		for (int j=0; j<num_neurons; ++j)
			synapses.back().push_back(
				Synapse(i*num_dvs_addresses+j,neurons,j,
						weight_distribution(generator),
						am_distribution(generator),
						ap_distribution(generator),
						wmin_distribution(generator),
						wmax_distribution(generator)
						));
	}

	float time = 0;
	for (int rep=0; rep<num_repetitions; ++rep)
	{
		cout << "rep " << rep << endl;
		for (float angle=0; angle<360; angle+=45)
		{
			cout << "angle " << angle << endl;
			cam.reset_and_angle(angle,time);
			for (float t=0.0; t<100.0; t+=dt)
			{
				int on_pixels = 0;
				int off_pixels = 0;
				auto image = cam.generate_image(time);
				//for (auto row : image)
				//{
				//	cout << row.size() << endl;
				//	for (auto col : row)
				//	{
				//		cout << col << endl;
				//	}
				//}

				auto image_diff = dvs.calculate_spikes(image);
				for (int row=0; row<image_height; ++row)
				{
					for (int col=0; col<image_width; ++col)
					{
						if (image_diff[row][col] > 0)
						{
							on_pixels += 1;
							for (Synapse synapse : synapses[(row*image_width+col)*2])
								synapse.pre(time);
//							for synapse in synapses[(row*image_width+col)*2]:
//								synapse.pre(time)
//							#print row,col,pixel
						}
						else if (image_diff[col][row] < 0)
						{
							off_pixels += 1;
							for (Synapse synapse : synapses[(row*image_width+col)*2+1])
								synapse.pre(time);
//							for synapse in synapses[(row*image_width+col)*2+1]:
//								synapse.pre(time)
//							#print row,col,pixel
						}
					}
				}
//				#print image_diff
				if (on_pixels > 0 || off_pixels > 0)
				{
					cout << "ON: " << on_pixels << ", OFF: " << off_pixels << endl;
				}
				cout << "-------- time = " << time << " ----------" << endl;
				time += dt;
			}
			// add a time-step of 100 ms between each run
			time += 100.0;
		}
	}

	auto spikes = neurons.get_spikes();
	ofstream file("spikes.dat",ios::out);
	for (auto pair : spikes)
	{
		file << get<0>(pair) << "," << get<1>(pair) << "\n";
	}
	file.close();
//		#if len(spikes[n]) > 0:
//		#	print n,len(spikes[n])
//		plt.plot(spikes[n],np.ones(len(spikes[n]))*n,'o')
//	for n in range(num_repetitions*8*2):
//		plt.axvline(n*100)
//
//	pickle.dump(spikes,open('spikes.dat','wb'))
//
//	#plt.figure()
//	#record = neurons.get_membrane_potential()
//	#record = np.array(record)
//
//	#for n in range(num_neurons):
//	#	times = []
//	#	membranes = []
//	#	for tpl in record[n]:
//	#		times.append(tpl[0])
//	#		membranes.append(tpl[1])
//	#	plt.plot(times,membranes)
//
//	plt.show()
//
}
//# vim: set noexpandtab
