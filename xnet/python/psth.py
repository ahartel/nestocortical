
def psth(stimuli, spikes, group_count=10):

    stimulus_pos   = 0
    this_stimulus = stimuli[stimulus_pos][0]
    stimulus_count = {this_stimulus:0}
    psth = {
            #this_stimulus: [ [[] for n in neurons] ]
            this_stimulus: [ {} ]
            }

    for spike in spikes:
        neuron = int(spike[0])
        if neuron > 511:
            time = spike[1]
            # check if stimulus has changed
            while stimulus_pos+1<len(stimuli) and time > stimuli[stimulus_pos+1][1]:
                stimulus_pos += 1
                this_stimulus = stimuli[stimulus_pos][0]
                try:
                    stimulus_count[this_stimulus] += 1
                except KeyError:
                    stimulus_count[this_stimulus] = 0

                if stimulus_count[this_stimulus]>0 and stimulus_count[this_stimulus]%group_count == 0:
                    psth[this_stimulus].append( {} )

            try:
                psth[this_stimulus][-1][neuron].append(time-stimuli[stimulus_pos][1])
            except KeyError:
                try:
                    psth[this_stimulus][-1][neuron] = []
                except KeyError:
                    psth[this_stimulus] = [ {} ]
                    psth[this_stimulus][-1][neuron] = []

                psth[this_stimulus][-1][neuron].append(time-stimuli[stimulus_pos][1])

    return psth
