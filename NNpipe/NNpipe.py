""" Main Neural Network pipe algorithm """

import argparse
import os.path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import time
import config
import sql
import cust_trace_to_wav
import cust_trace_preprocessing
import cust_hypothesis_check
from time import strftime, gmtime
from scipy.io.wavfile import read, write
from datetime import datetime

#container for profiling time 'threads'
PROFILE_THREADS = {'DEEP': 0}

def main():
    profile_start('MAIN')
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
        default=str(strftime("%m_%d_%H_%M", gmtime())), dest='run_name')
    args = parser.parse_args()
    
    interactive = args.interactive
    tracepath = args.tracepath
    timestamppath = args.timestamppath
    learning_mode = args.learning_mode
    run_name = args.run_name

    connection = sql.open_connection()
    
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
            sql.drop_c_weigths(connection)
        if config.DROP_K_WEIGHTS_ON_START:
            #drop K weights
            print("Dropping K weights ...")
            sql.drop_k_weigths(connection)
        if config.DROP_ITERATIONS_TRAIN_ON_START:
            #drop iterations
            print("Dropping old iterations ...")
            sql.drop_training_iterations(connection)
        
    timestamp = pd.read_csv(timestamppath, header=None)
    timestamp.columns = ['plain', 'key', 'cypher', 'time']

    #read trace data
    profile_start('CUST_TRACE_TO_WAV')
    tracepath = cust_trace_to_wav.run(tracepath)
    profile_finish('CUST_TRACE_TO_WAV')

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
    #debug
    sig_length = 5

    #convolution calculation    
    max_m = 0
    i_best = 0
    t_range = int(wave_data.size - sig_length_total)

    print('Convolution calculation (' + str(t_range) + ') ...')
    profile_start('CONVOLUTION_CALC')
    for i in range(t_range):
        convolution = np.convolve(wave_data, wave_data[i:i+sig_length])
        m = np.mean(convolution)
        if i % 500 == 0:
            debug('Steps:', str(i) + '/' + str(t_range))
            #debug
            break
        if max_m < m:
            max_m = m
            i_best = i

    #best convolution
    convolution = np.convolve(wave_data, wave_data[i_best:i_best+sig_length])
    profile_finish('CONVOLUTION_CALC')

    #draw plot, do not stop calculations
    plt.plot(convolution)
    plt.ylabel('Convolution')
    plt.show(block=False)

    profile_start('WORK_WITH_NETWORK')
    for i in range(sig_count):
        #identify each signature based on i_best
        next_sig_start = int(np.round((timestamp.time[i*2] - timestamp.time[0]) * config.DEVICE_SAMPLING / config.TIMESTAMP_SAMPLING))
        sig = wave_data[i_best+next_sig_start:i_best+next_sig_start+sig_length]
        sig_name = "sig_" + run_name + '_' + str(i)

        profile_start('CUST_TRACE_PREPROCESSING')
        sig = cust_trace_preprocessing.run(sig)
        profile_finish('CUST_TRACE_PREPROCESSING')

        debug("Write signature file:", sig_name + config.WAV_EXTENTION)
        print("TODO: writing signature files into DB")
        write(sig_name + config.WAV_EXTENTION, config.DEVICE_SAMPLING, sig)
        
        debug("Write signature info file:", sig_name + config.SIG_INFO_EXTENSION)
        f = open(sig_name + config.SIG_INFO_EXTENSION, 'w')
        f.writelines([str(i), timestamp.key[i*2], timestamp.cypher[i*2], timestamp.plain[i*2]])
        f.close()

        #provide signature into neural network
        debug("Send file into neural network:", sig_name + config.WAV_EXTENTION)
        FNULL = open(os.devnull, 'w')
        args = "test.bat " + sig_name + config.WAV_EXTENTION + ' ' + sig_name + config.SIG_INFO_EXTENSION
        subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=True)

        #read neural network output
        cont = True
        debug("Read neural network results:", sig_name + config.NN_OUTPUT_EXTENTION)
        f = open(sig_name + config.NN_OUTPUT_EXTENTION, 'r')
        y = f.readline()    #global key hypothsis 
        h = f.readline()    #iteration key hypothsis
        hadd = f.readline() #additional vector
        m = f.readline()    #bit mask
        e = f.readline()    #error vector
        eadd = f.readline() #error absolute vector
        k = f.readline()    #key-plaintext link vector
        d = f.readline()    #ciphertexts differences vector
        dt = f.readline()   #what
        ds = f.readline()   #what
        f.close()
        #continue learning or not (default True)
        profile_start('CUST_HYPOTHESIS_CHECK')
        cont = cust_hypothesis_check.run(y, h, hadd, m, e, eadd, k, d, dt, ds)
        profile_finish('CUST_HYPOTHESIS_CHECK')

        #save results into DB
        debug("Saving neural network results into DB", None)
        print("TODO: saving neural network results into DB")

        if learning_mode and not cont:
            print("Learning is finished ...")
            break
    profile_finish('WORK_WITH_NETWORK')
    profile_finish('MAIN')

def debug(t1, t2):
    if config.DEBUG:
        print (t1, t2)

def profile_start(thread_name):
    if config.DEBUG:
        PROFILE_THREADS[thread_name] = time.time()
        PROFILE_THREADS['DEEP'] += 1
        print('-'*PROFILE_THREADS['DEEP'] + thread_name +
            ' STARTED')

def profile_finish(thread_name):
    if config.DEBUG:
        print('-'*PROFILE_THREADS['DEEP'] + thread_name +
            ' FINISHED ' + str(time.time() - PROFILE_THREADS[thread_name]))
        PROFILE_THREADS.pop(thread_name, None)
        PROFILE_THREADS['DEEP'] -= 1

if __name__ == "__main__":
    main()