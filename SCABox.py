from TracesFilesystem import *
import time
import math
from Database import Database
import numpy
import matplotlib.pyplot as plt
import re
import heapq
import numpy as np


def nicv(db, idList):
    start_time = time.time()
    idListLen = len(idList)
    errList = []
    meanList = []
    varList = []

    cmd = "SELECT message, cipher, data FROM trace WHERE id = '" + str(idList[2]) + "'"
    db.cur.execute(cmd)
    one = db.cur.fetchone()
    tmsg, tcrypt, traw_data = one

    parse_data = parse_binary(traw_data)
    points = len(parse_data)
    print("Points in trace:", points)

    print("Calculating ...")

    tclassList = [0.0] * points
    tMeanList = [0.0] * points
    tPowerMeanList = [0.0] * points
    parallels = 20
    tGlobalVarlist = [[] for i in range(parallels)]
    classList = [] * 256
    globalVarlist = []
    byteList = []

    collected = 0
    classCalcCount = 0
    classCountNotIncluded = 0
    tracesInClass = 0

    for i in range(points // parallels):
        start_time = time.time()
        # idListPack = idList[i * parallels:i * parallels + parallels]
        # cmd = "SELECT message FROM trace WHERE id in " + str(idListPack).replace('[', '(').replace(']', ')') + ""
        # db.cur.execute(cmd)
        # list_msg = db.cur.fetchall()
        # cmd = "SELECT data FROM trace WHERE id in " + str(idListPack).replace('[', '(').replace(']', ')') + ""
        # db.cur.execute(cmd)
        # list_raw_data = db.cur.fetchall()
        if collected == 0:
            for j in range(idListLen):
                err = 0
                cmd = "SELECT message, data FROM trace WHERE id = '" + str(idList[j]) + "'"
                db.cur.execute(cmd)
                one = db.cur.fetchone()
                msg, raw_data = one
                try:
                    parse_data = parse_binary(raw_data)
                except:
                    err = 1
                    errList.append(idList[j])
                if err == 0:
                    for k in range(parallels):
                        tGlobalVarlist[k].append(parse_data[i * parallels + k])
                    parse_data = None
                    byteList.append((int(msg[0:2], 16), idList[j]))
                if j % parallels == 0 and j != 0:
                    print(j, "traces were processed.")
            for m in range(parallels):
                globalVarlist.append(numpy.var(numpy.array(tGlobalVarlist[m])))
            tGlobalVarlist = [[] for m in range(parallels)]
            collected = 1
        else:
            for j in range(idListLen):
                err = 0
                cmd = "SELECT message, data FROM trace WHERE id = '" + str(idList[j]) + "'"
                db.cur.execute(cmd)
                msg, raw_data = db.cur.fetchone()
                msg = None
                try:
                    parse_data = parse_binary(str(raw_data))
                except:
                    err = 1
                if err == 0:
                    for k in range(parallels):
                        tGlobalVarlist[k].append(parse_data[i*parallels+k])
                    parse_data = None
                if j % 20000 == 0:
                    print(j, "traces were processed.")
            for m in range(parallels):
                globalVarlist.append(numpy.var(numpy.array(tGlobalVarlist[m])))
            print("TEST:", len(globalVarlist))
            tGlobalVarlist = None
            tGlobalVarlist = [[] for m in range(parallels)]
    lenn = len(byteList)
    for i in range(256):
        tracesInClass = 0
        for j in range(lenn):
            byte, id = byteList[j]
            if byte == i:
                cmd = "SELECT message, data FROM trace WHERE id = '" + str(id) + "'"
                db.cur.execute(cmd)
                msg, raw_data = db.cur.fetchone()
                msg = None
                parse_data = parse_binary(str(raw_data))
                for d in range(points):
                    tMeanList[d] = tMeanList[d] + parse_data[d]
                    tPowerMeanList[d] = tPowerMeanList[d] + parse_data[d]**2
                    tracesInClass = tracesInClass + 1
                parse_data = None
        if tracesInClass > 0:
            for m in range(points):
                tPowerMeanList[m] = tPowerMeanList[m]/tracesInClass - (tMeanList[m]/tracesInClass)**2
            print("Var[E(Y|X)] for class", i, "was calculated")
            classList.append(tPowerMeanList)
        else:
            classCountNotIncluded = classCountNotIncluded + 1
            print("Class was empty!")
        tMeanList = [0.0] * points
        tPowerMeanList = [0.0] * points
    print("Classes:", 256 - classCountNotIncluded)
    for i in range(256 - classCountNotIncluded):
        for j in range(points):
            if i != 0:
                classList[0][j] = classList[0][j] + classList[i][j]
    print("Total Var[E(Y|X)] for all classes was calculated!")
    lenn = points//parallels*parallels
    for i in range(lenn):
        globalVarlist[i] = math.sqrt(classList[0][i]/globalVarlist[i]/lenn)
    print("NICV function was calculated!")
    print('Execution time:', time.time() - start_time)
    t = open("nicv", "w")
    for i in range(lenn):
        t.write(str(globalVarlist[i]) + ' ')
    t.close()
    plt.bar(range(0, lenn), globalVarlist, color='g')
    plt.ylabel('NICV')
    plt.xlabel('samples')
    plt.colors()
    plt.show()


def nicv2(parallels, timing, db, idList):
    # create a list for each component class:
    classes = [[[] for n in range(256)] for m in range(parallels)]
    # count traces in db:
    ntraces = len(idList)
    # create a list for total variance calculating
    total = [[] for n in range(parallels)]
    # initialize list of bad traces
    bad = []
    ttrace = None
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
    print('# Components :', ncomponents)
    print('# Cycle steps :', div_ncomponents)
    # initialize a sum of inter-class variances and total variance for one component
    svar = [0.0] * parallels
    tvar = [0.0] * parallels
    # initialize nicv array
    nicv_list = [0.0] * div_ncomponents*parallels
    for i in range(div_ncomponents):
        if timing: start_time = time.time()                                                             # TIMING - START
        try:
            cmd = "SELECT message, data FROM trace WHERE id = '" + str(idList[i]) + "'"
            db.cur.execute(cmd)
            one = db.cur.fetchone()
            msg, raw_data = one
            trace = parse_binary(raw_data)
            for j in range(parallels):
                classes[j][int(msg[0:2], 16)].append(trace[i * parallels + j])
                total[j].append(trace[i * parallels + j])
        except:
            print("WARNING: Trace", i, "was not processed.")
            bad.append(i)
            msg = 'bad'
            continue
        for k in range(parallels):
            for c in range(256):
                if len(classes[k][c]) >= 2:
                    svar[k] = svar[k] + np.var(classes[k][c])
        for p in range(parallels):
            tvar[p] = np.var(total[p])
            nicv_list[i * parallels + p] = math.sqrt(svar[p] / tvar[p])
        if i % parallels == 0 and i != 0:
            print("NICV was calculated for the next", parallels, "components ...")

        classes = [[[] for n in range(256)] for m in range(parallels)]
        total = [[] for n in range(parallels)]
        svar = [0.0] * parallels
        tvar = [0.0] * parallels
        if timing:                                                                                   # TIMING - STOP
            t = time.time() - start_time
            print("ITERATION TIME: ", t)
            print("ESTIMATED TOTAL: ", (t * div_ncomponents / 60 / 60), "h.")
            timing = False

    print("NICV was calculated for all components!")
    print(nicv_list)
    t = open("nicv", "w")
    for i in range(div_ncomponents):
        t.write(str(nicv_list[i]) + ' ')
    t.close()
    plt.bar(range(0, div_ncomponents), nicv_list, color='g')
    plt.ylabel('NICV')
    plt.xlabel('samples')
    plt.colors()
    plt.show()

def kmeans(indir, pattern, outdir, nicv_fpath, nfeatures, timing):
    ntraces = len(os.listdir(indir))
    vectors = []*ntraces
    nicv_list = []
    # INITIALIZATION
    if not os.path.isdir(indir):
        print(indir + " does not exist !!")
        sys.exit(1)
    elif len(os.listdir(indir)) == 0:
        print(indir + " is empty !!")
        sys.exit(1)
    else:
        tdb = TracesFilesystem(indir)
    if not os.path.isdir(outdir):
        print(outdir + " does not exist !!")
        sys.exit(1)
    try:
        re.match(pattern, '')
    except: # pattern is incorrect
        print('Pattern ', pattern, ' is incorrect!')
        sys.exit(1)
    if not os.path.isfile(nicv_fpath):
        print('Features stat file does not exist !!')
        sys.exit(1)
    else:
        print('Founded stst file ' + nicv_fpath)
    with open(nicv_fpath, 'r') as f:
        nicv_list = list(f)

    print(nicv_list)
    features = heapq.nlargest(5, nicv_list)
    print('Stat was loaded.')

    tdb = TracesFilesystem(indir)
    for i in range(ntraces):
        try:
            msg, crypt, trace = tdb.get_trace()
            ttrace = trace
            break
        except:
            pass
    ncomponents = len(ttrace)
    tdb.set_counter(0)
    # VECTORS GENERATION
    # TODO: re.search('(?<=k=)(.*)(?=_m)', fileName).group(0)
    for i in range(ntraces):
        try:
            msg, crypt, trace = tdb.get_trace()
            print(ncomponents, features)
            for j in range(ncomponents):
                if j in (features):
                    vectors[i].append(trace[j])
        except:
            print("WARNING: Trace", i, "was not processed.")


def test():
    db = Database()
    db.connect()
    idList = db.get_trace_idlist('des_first')
    nicv2(50, False, db, idList)

if __name__ == "__main__":
    test()