from struct import unpack  # Function allowing conversion from C binary data


def parse_binary(raw_data):

    """
    Takes a raw binary string containing data from our oscilloscope.
    Returns the corresponding float vector.
    """

    ins = 4   # Size of int stored in the raw binary string
    cur = 0   # Cursor walking in the string and getting data
    cur + 12  # Skipping the global raw binary string header
    whs = unpack("i", raw_data[cur:cur+ins])[0] # Storing size of the waveform header
    cur += whs # Skipping the waveform header
    dhs = unpack("i", raw_data[cur:cur+ins])[0] # Storing size of the data header
    cur += dhs # Skipping the data header
    bfs = unpack("i", raw_data[cur-ins:cur])[0] # Storing the data size
    sc = bfs/ins # Samples Count - How much samples compose the wave
    dat = unpack("f"*sc, raw_data[cur:cur+bfs])

    return dat