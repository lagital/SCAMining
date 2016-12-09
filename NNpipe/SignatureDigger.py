from optparse import OptionParser
import pandas as pd
import numpy as np
from scipy.io.wavfile import read
import matplotlib.pyplot as plt
from scipy import signal

use_debug            = False
device_sampling      = 44100
timestamp_sampling   = 1000000000

def main():
    global use_debug

    parser = OptionParser()
    parser.add_option("-t", "--trace", dest="tracepath",
                  help="/path/to/trace file", metavar="FILE")
    parser.add_option("-s", "--stamp", dest="timestamppath",
                  help="/path/to/timestamp file", metavar="FILE")
    parser.add_option("-d", "--debug", dest="use_debug",
                  help="y or n to turn on/off debugging", metavar="Boolean")
    parser.add_option("-o", "--options", dest="options",
                  help="possible options:")
    (options, args) = parser.parse_args()

    if options.use_debug == 'y':
        use_debug = True

    timestamp = pd.read_csv(options.timestamppath, header=None)
    timestamp.columns = ['plain', 'key', 'cypher', 'time']

    wave_file = read(options.tracepath)
    wave_data = np.array(wave_file[1],dtype=float)

    plt.plot(wave_data)
    plt.ylabel('some numbers')
    plt.show()
    return

    debug('Wave data length (points):', wave_data.size)
    debug('Signatures (n):', timestamp.time.size // 2)

    sig_time = timestamp.time[1] - timestamp.time[0]
    sig_length = int(np.round(sig_time * device_sampling / timestamp_sampling))
    debug('~signature length:', sig_length)
    sig_length_total = int(np.round((timestamp.time[timestamp.time.size-1] - timestamp.time[0]) 
        * device_sampling / timestamp_sampling))
    debug('Signatures length total:', sig_length_total)

    max_m = 0
    i_best = 0
    t_range = int(wave_data.size - sig_length_total)
    print('Convolution calculation (' + str(t_range) + ') ...')
    for i in range(t_range):
        #convolution = signal.fftconvolve(wave_data, wave_data[i:i+sig_length], mode='full')
        convolution = np.convolve(wave_data, wave_data[i:i+sig_length])
        m = np.mean(convolution)
        if i % 1000 == 0:
            print('Step:', i, '/', t_range)
        if max_m < m:
            max_m = m
            i_best = i
            debug('Result was updated', '')

    #convolution = signal.fftconvolve(wave_data, wave_data[i_best:i_best+sig_length], mode='full')
    convolution = np.convolve(wave_data, wave_data[i_best:i_best+sig_length])
    plt.plot(convolution)
    plt.ylabel('some numbers')
    plt.show()

def debug(t1, t2):
    if use_debug == True:
        print (t1, t2)

if __name__ == "__main__":
    main()