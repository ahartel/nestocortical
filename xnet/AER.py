"""
Module to deal with the AER (Address Event Representation) format.

Current state:
* load_AER seems fine
* extract_DVS_event is probably fine too, but maybe should be in a "chip" module?

"""

import sys
from numpy import *

import os, datetime, struct
__all__=['load_AER','save_AER',
         'extract_DVS_event', 'extract_AMS_event',
         'AERSpikeGeneratorGroup', 'AERSpikeMonitor']





########### AER loading stuff ######################

def load_multiple_AER(filename, check_sorted = False, relative_time = False, directory = '.'):
    f=open(filename,'rb')
    line = f.readline()
    res = []
    line = line.strip('\n')
    while not line == '':
        res.append(load_AER(os.path.join(directory, line), check_sorted = check_sorted, relative_time = relative_time))
        line = f.readline()
    f.close()
    return res

def load_AER(filename, check_sorted = False, relative_time = True):
    '''
    Loads AER data files for use in Brian.
    Returns a list containing tuples with a vector of addresses and a vector of timestamps (ints, unit is usually usecond).

    It can load any kind of .dat, or .aedat files.
    Note: For index files (that point to multiple .(ae)dat files) it will return a list containing tuples as for single files.
    
    Keyword Arguments:
    If check_sorted is True, checks if timestamps are sorted,
    and sort them if necessary.
    If relative_time is True, it will set the first spike time to zero and all others relatively to that precise time (avoid negative timestamps, is definitely a good idea).
    
    Hence to use those data files in Brian, one should do:

    addr, timestamp =  load_AER(filename, relative_time = True)
    G = AERSpikeGeneratorGroup((addr, timestamps))
    '''
    l = filename.split('.')
    ext = l[-1].strip('\n')
    filename = filename.strip('\n')
    directory = os.path.dirname(filename)
    if ext == 'aeidx':
        #AER data points to different AER files
        return load_multiple_AER(filename, check_sorted = check_sorted, relative_time = relative_time, directory = directory)
    elif not (ext == 'dat' or ext == 'aedat'):
        raise ValueError('Wrong extension for AER data, should be dat, or aedat, it was '+ext)
    
    # This is inspired by the following Matlab script:
    # http://jaer.svn.sourceforge.net/viewvc/jaer/trunk/host/matlab/loadaerdat.m?revision=2001&content-type=text%2Fplain
    f=open(filename,'rb')
    version=1 # default (if not found in the file)
    
    # Skip header and look for version number
    line = f.readline()
    while line[0] == '#':
        if line[:9] == "#!AER-DAT":
            version = int(float(line[9:-1]))
        line = f.readline()
    line += f.read()
    f.close()
    
    if version==1:
        print 'Loading version 1 file '+filename
        '''
        Format is: sequence of (addr = 2 bytes,timestamp = 4 bytes)
        Number format is big endian ('>')
        '''
        ## This commented paragraph is the non-vectorized version
        #nevents=len(line)/6
        #for n in range(nevents):
        #    events.append(unpack('>HI',line[n*6:(n+1)*6])) # address,timestamp
        x=fromstring(line, dtype=int16) # or uint16?
        x=x.reshape((len(x)/3,3))
        addr=x[:,0].newbyteorder('>')
        timestamp=x[:,1:].copy()
        timestamp.dtype=int32
        timestamp=timestamp.newbyteorder('>').flatten()
    else: # version==2
        print 'Loading version 2 file '+filename
        '''
        Format is: sequence of (addr = 4 bytes,timestamp = 4 bytes)
        Number format is big endian ('>')
        '''
        ## This commented paragraph is the non-vectorized version
        #nevents=len(line)/8
        #for n in range(nevents):
        #    events.append(unpack('>II',line[n*8:(n+1)*8])) # address,timestamp
        x = fromstring(line, dtype=int32).newbyteorder('>')
        addr = x[::2]
        if len(addr) == len(x[1::2]):
            timestamp = x[1::2]
        else:
            print """It seems there was a problem with the AER file, timestamps and addr don't have the same length!"""
            timestamp = x[1::2]

    if check_sorted: # Sorts the events if necessary
        if any(diff(timestamp)<0): # not sorted
            ind = argsort(timestamp)
            addr,timestamp = addr[ind],timestamp[ind]
    if (timestamp<0).all():
        print 'Negative timestamps'
    
    if relative_time:
        t0 = min(timestamp)
        timestamp -= t0
    
    return addr,timestamp

HEADER = """#!AER-DAT2.0\n# This is a raw AE data file - do not edit\n# Data format is int32 address, int32 timestamp (8 bytes total), repeated for each event\n# Timestamps tick is 1 us\n# created with the Brian simulator on """

def save_AER(spikemonitor, f):
    '''
    Saves the SpikeMonitor's contents to a file in aedat format.
    File should have 'aedat' extension.
    One can specify an open file, or, alternatively the filename as a string.

    Usage:
    save_AER(spikemonitor, file)
    '''
    if isinstance(spikemonitor, SpikeMonitor):
        spikes = spikemonitor.spikes
    else:
        spikes = spikemonitor
    if isinstance(f, str):
        strinput = True
        f = open(f, 'wb')
    l = f.name.split('.')
    if not l[-1] == 'aedat':
        raise ValueError('File should have aedat extension')
    header = HEADER
    header += str(datetime.datetime.now()) + '\n'
    f.write(header)
    # i,t=zip(*spikes)
    for (i,t) in spikes:
        addr = struct.pack('>i', i)
        f.write(addr)
        time = struct.pack('>i', int(ceil(float(t/usecond))))
        f.write(time)
    if strinput:
        f.close()
    

    
########### AER addressing stuff ######################

def extract_DVS_event(addr):
    '''
    Extracts retina event from an address or a vector of addresses.
    
    Chip: Digital Vision Sensor (DVS)
    http://siliconretina.ini.uzh.ch/wiki/index.php
    
    Returns: x, y, polarity (ON/OFF: 1/-1)
    '''
    retina_size=128

    xmask = 0xfE # x are 7 bits (64 cols) ranging from bit 1-8
    ymask = 0x7f00 # y are also 7 bits
    xshift=1 # bits to shift x to right
    yshift=8 # bits to shift y to right
    polmask=1 # polarity bit is LSB

    x = retina_size - 1 - ((addr & xmask) >> xshift)
    y = (addr & ymask) >> yshift
    pol = 1 - 2*(addr & polmask) # 1 for ON, -1 for OFF
    return x,y,pol

def extract_AMS_event(addr):
    '''
    Extracts cochlea event from an address or a vector of addresses

    Chip: Silicon Cochlea (AMS)
    
    Returns: side, channel, filternature
    
    More precisely:
    side: 0 is left, 1 is right
    channel: apex (LF) is 63, base (HF) is 0
    filternature: 0 is lowpass, 1 is bandpass
    '''
    # Reference:
    # ch.unizh.ini.jaer.chip.cochlea.CochleaAMSNoBiasgen.Extractor in the jAER package (look in the javadoc)
    # also the cochlea directory in jAER/host/matlab has interesting stuff
    # the matlab code was used to write this function. I don't understand the javadoc stuff
    #cochlea_size = 64

    xmask = 31 # x are 5 bits 32 channels) ranging from bit 1-5 
    ymask = 32 # y (one bit) determines left or right cochlea
    xshift=0 # bits to shift x to right
    yshift=5 # bits to shift y to right
    
    channel = 1 + ((addr & xmask) >> xshift)
    side = (addr & ymask) >> yshift
    lpfBpf = mod(addr, 2)
#    leftRight = mod(addr, 4)
    return (lpfBpf, side, channel)

if __name__=='__main__':
    path=r'/home/ahartel/Downloads/'
    filename=r'Tmpdiff128-2008-04-09T15-38-53+0200-0fastDot.dat'

    addr,timestamp=load_AER(sys.argv[1])
    print addr, timestamp
