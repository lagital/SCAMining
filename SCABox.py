from TracesFilesystem import *
import time
import math
from Database import Database
import matplotlib.pyplot as plt
import scipy.cluster.vq as sp
import numpy as np


def nicv2(parallels, timing, db, idList, kind, block_size):
    # create a list for each component class:
    classes = [[[] for n in range(256)] for m in range(parallels)]
    # count traces in db:
    ntraces = len(idList)
    # create a list for total variance calculating
    total = [[] for n in range(parallels)]
    # initialize list of bad traces
    bad = []
    for i in idList:
        try:
            cmd = "SELECT message, data FROM trace WHERE id = '" + str(i) + "'"
            db.cur.execute(cmd)
            one = db.cur.fetchone()
            msg, raw_data = one
            ttrace = parse_binary(raw_data)
            break
        except:
            print("WARNING: Trace", str(i), "was not processed.")
            bad.append(i)
    # initialize ncomponents which will contain number of components
    ncomponents = len(ttrace)
    div_ncomponents = ncomponents // parallels
    div_nlist = len(idList) // block_size
    print('# Traces :', len(idList))
    print('# Components :', ncomponents)
    print('# Cycle steps :', div_ncomponents)
    # initialize a sum of inter-class variances and total variance for one component
    svar = [0.0] * parallels
    tvar = [0.0] * parallels
    # initialize nicv array
    nicv_list = [0.0] * div_ncomponents * parallels
    for i in range(div_ncomponents):
        if timing: start_time = time.time()                                                             # TIMING - START
        for f in range(div_nlist):
            block = str(idList[f * block_size: f * block_size + block_size])
            cmd = "SELECT message, data FROM trace WHERE id in " + block.replace('[', '(').replace(']', ')') + ""
            db.cur.execute(cmd)
            msg_raw_data = list(db.cur.fetchall())
            for c in range(block_size):
                try:
                    trace = parse_binary(msg_raw_data[c][1])
                    msg_p = int(msg_raw_data[c][0][0:2], 16)
                    for j in range(parallels):
                        classes[j][msg_p].append(trace[i * parallels + j])
                        total[j].append(trace[i * parallels + j])
                except:
                    print("WARNING: One trace was not processed.")
        print(parallels, ' components were processed.')
        if timing: nicv_time = time.time()                                                         # NICV_TIMING - START
        for k in range(parallels):
            for c in range(256):
                if len(classes[k][c]) >= 2:
                    svar[k] = svar[k] + np.var(classes[k][c])
        for p in range(parallels):
            tvar[p] = np.var(total[p])
            nicv_list[i * parallels + p] = math.sqrt(svar[p] / tvar[p])
        if i != 0:
            print("NICV was calculated for ", parallels, "components ...")
        if timing:                                                                                  # NICV_TIMING - STOP
                t = time.time() - nicv_time
                print("NICV CALC TIME: ", t)
        classes = [[[] for n in range(256)] for m in range(parallels)]
        total = [[] for n in range(parallels)]
        svar = [0.0] * parallels
        tvar = [0.0] * parallels
        if timing:                                                                                       # TIMING - STOP
            t = time.time() - start_time
            print("ITERATION TIME: ", t)
            print("ESTIMATED TOTAL: ", (t * div_ncomponents / 60), "min.")
            time.sleep(7)
            timing = False

    print("NICV was calculated for all components!")
    print(nicv_list)
    t = open("nicv", "w")
    for i in range(div_ncomponents):
        t.write(str(nicv_list[i]) + ' ')
    t.close()
    plt.bar(range(0, div_ncomponents * parallels), nicv_list, color='g')
    plt.ylabel('NICV')
    plt.xlabel('samples')
    plt.colors()
    plt.show()


def kmeans(db, idList, nicvList, isTest, kind, timing):
    # INITIALIZATION
    vectors = [('', [])] * len(idList)
    features = np.argsort(nicvList)[::-1][:5]
    keys = []
    print('Stat was loaded.')
    if isinstance(isTest, int):
        mode = 'prod'
        print('Clusterization for', kind, '...')
        print('Clusters:', str(isTest))
        for i in range(isTest):
            keys.append(i)
        print(str(isTest), 'phantom keys are created.')
        time.sleep(5)
    elif isTest == True:
        mode = 'test'
        cmd = "SELECT DISTINCT key FROM trace WHERE kind = '" + kind + "'"
        db.cur.execute(cmd)
        keys = db.cur.fetchall()
        nclusters = len(keys)
        ncomponents = 0
        print('Test clusterization for', kind, '...')
        print('Clusters:', str(nclusters))
        print('Keys:', keys)
        time.sleep(5)
    for i in idList:
        try:
            cmd = "SELECT message, data FROM trace WHERE id = '" + str(i) + "'"
            db.cur.execute(cmd)
            one = db.cur.fetchone()
            msg, raw_data = one
            ncomponents = len(parse_binary(raw_data))
            print("OK!")
            break
        except:
            print("WARNING: Trace", str(i), "was not processed.")

    # VECTORS GENERATION
    for i in range(len(idList)):
        try:
            cmd = "SELECT key, data FROM trace WHERE id = '" + str(idList[i]) + "'"
            db.cur.execute(cmd)
            one = db.cur.fetchone()
            key, raw_data = one
            tmp = []
            for j in features:
                tmp.append(parse_binary(raw_data)[j])
            vectors[i] = tuple((key.rstrip().lstrip(), tmp))
        except:
            print("WARNING: Trace", str(i), "was not processed.")
    # CLUSTERS GENERATION
    data = np.array([x[1] for x in vectors])
    centroids, positions = sp.kmeans2(data, 3, 1, 'warn', 'random')

    # CLUSTERS LINKING
    if mode == 'prod':
        for i in range(len(keys)):
            for j in positions:
                if j == i:
                    keys[i] = tuple

def test(TEST):
    db = Database()
    db.connect()
    kind = 'des_first'
    idList = db.get_trace_idlist(kind)
    if TEST == 0:
        nicv2(20, True, db, idList[0:10000], kind, 1)
    elif TEST == 1:
        nicvList = [0.95, 0.7, 0, 0.4, 0.3, 0.2, 0.1, 0.34]
        kmeans(db, idList[0:100], nicvList, 2, kind, False)
    elif TEST == 2:
        nicvList = nicv2(20, True, db, idList[0:100], kind, 2)
        kmeans(db, idList[0:100], nicvList, True, kind, False)
if __name__ == "__main__":
    TEST = 1
    test(TEST)