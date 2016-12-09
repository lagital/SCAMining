""" Main Neural Network pipe algorithm """

import argparse
import os.path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import config
import cust_trace_to_wav
import cust_trace_preprocessing
from time import gmtime, strftime
from scipy.io.wavfile import read, write
from datetime import datetime

def main():
    #read arguments
    parser = argparse.ArgumentParser(description='Input')
    parser.add_argument('-i', '-interactive', type=bool, help='interactive mode',
    	default=False, dest='interactive')
    parser.add_argument('-t', '-trace', type=str, help='/path/to/trace file',
    	default="", dest='tracepath')
    parser.add_argument('-s', '-stamp', type=str, help='/path/to/timestamp file',
    	default="", dest='timestamppath')
    parser.add_argument('-m', '-mode', type=bool, help='learning mode - True or False',
    	default=True, dest='learning_mode')
    parser.add_argument('-n', '-name', type=str, help='run name - for unique signature names',
    	default=str(strftime("%H:%M:%S", gmtime())), dest='run_name')
    args = parser.parse_args()
    
    interactive = args.interactive
    tracepath = args.tracepath
    timestamppath = args.timestamppath
    learning_mode = args.learning_mode
    run_name = args.run_name
    
    #check interactive mode
    if interactive:
        while not os.path.isfile(tracepath):
            tracepath = input("Enter correct path to trace file[]: ")
        while not os.path.isfile(timestamppath):
            timestamppath = input("Enter correct path to time stamp file[]: ")
    else:
    	if not os.path.isfile(tracepath):
    		print("Wrong path to trace file!")
    	if not os.path.isfile(timestamppath):
    		print("Wrong path to time stamp file!")

    if learning_mode:
    	if config.DROP_C_WEIGHTS_ON_START:
    		#drop C weights
    		print("Dropping C weights ...")
    		print("TODO: drop C weights")
    	if config.DROP_K_WEIGHTS_ON_START:
    		#drop K weights
    		print("Dropping K weights ...")
    		print("TODO: drop K weights")
    	if config.DROP_ITERATIONS_TRAIN_ON_START:
    		#drop iterations
    		print("Dropping old iterations ...")
    		print("TODO: drop iterations")
    	#clean old runs with the same name
    		print("Delete signatures of old runs ...")

    timestamp = pd.read_csv(timestamppath, header=None)
    timestamp.columns = ['plain', 'key', 'cypher', 'time']

    #read trace data
    tracepath = cust_trace_to_wav.run(tracepath)
    
    wave_file = read(tracepath)
    wave_data = np.array(wave_file[1],dtype=float)

    sig_count = timestamp.time.size // 2
    debug('Wave data length (points):', wave_data.size)
    debug('Signatures (n):', sig_count)

    #analyze signatures
    sig_time = timestamp.time[1] - timestamp.time[0]
    sig_length = int(np.round(sig_time * config.DEVICE_SAMPLING / config.TIMESTAMP_SAMPLING))
    debug('~signature length:', sig_length)
    sig_length_total = int(np.round((timestamp.time[timestamp.time.size-1] - timestamp.time[0]) 
        * config.DEVICE_SAMPLING / config.TIMESTAMP_SAMPLING))
    debug('Signatures length total:', sig_length_total)

    #convolution calculation    
    max_m = 0
    i_best = 0
    t_range = int(wave_data.size - sig_length_total)

    print('Convolution calculation (' + str(t_range) + ') ...')
    for i in range(t_range):
        convolution = np.convolve(wave_data, wave_data[i:i+sig_length])
        m = np.mean(convolution)
        if i % 1000 == 0:
            print('Step:', i, '/', t_range)
        if max_m < m:
            max_m = m
            i_best = i

    convolution = np.convolve(wave_data, wave_data[i_best:i_best+sig_length])
    
    #draw plot, do not stop calculations
    plt.plot(convolution)
    plt.ylabel('Convolution')
    plt.show(block=False)

    sig_count = 5
    for i in range(sig_count):
    	next_sig_start = int(np.round((timestamp.time[i*2] - timestamp.time[0]) 
        * config.DEVICE_SAMPLING / config.TIMESTAMP_SAMPLING))
    	sig = wave_data[i_best+next_sig_start:i_best+next_sig_start+sig_length]
    	sig_name = "sig_" + run_name + '_k_' + timestamp.key + '_c_' + timestamp.cypher  + '_p_' + timestamp.plain
    	
    	sig = cust_trace_preprocessing.run(sig)

    	print("Write signature file" + sig_name + '...')
    	print("TODO: writing signature files into DB")
    	#write(sig_name, config.DEVICE_SAMPLING, sig)

    	FNULL = open(os.devnull, 'w')
    	args = "test.bat"
    	subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=True)

def debug(t1, t2):
    if config.DEBUG:
        print (t1, t2)

if __name__ == "__main__":
    main()