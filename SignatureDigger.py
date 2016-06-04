from optparse import OptionParser
import pandas as pd
import numpy as np
from scipy.io.wavfile import read

use_debug = True
analyse_signatures = 3

def main():
    parser = OptionParser()
    parser.add_option("-t", "--trace", dest="tracepath",
                  help="/path/to/trace file", metavar="FILE")
    parser.add_option("-l", "--log", dest="timestamppath",
                  help="/path/to/timestamp file", metavar="FILE")
    parser.add_option("-o", "--options", dest="options",
                  help="possible options:")
    (options, args) = parser.parse_args()

    timestamp = pd.read_csv(options.timestamppath, header=None)
    timestamp.columns = ['plain', 'key', 'cypher', 'time']

    wave_file = read(options.tracepath)
    wave_data = np.array(wave_file[1],dtype=float)  

    debug(wave_data[0:5])
    debug(list(timestamp.time))

    total_trace_time = wave_data.size

    total_encryption_time = timestamp.time[timestamp.time.size - 1] - timestamp.time[0]
    print ('Total encryption time (ms):', total_encryption_time)

    search_range = total_trace_time - total_encryption_time
    print ('Search range (points):', search_range)

    #for i in range(total_trace_time - search_range):
    subrange = timestamp.time[2] - timestamp.time[1]
    print (subrange)
    convolution = np.convolve(wave_data[0:subrange], wave_data)

    print (convolution)

def debug(t):
    if use_debug == True:
        print (t)

if __name__ == "__main__":
    main()