from TracesFilesystem import *
import sys
import os
import statistics
#import matplotlib.pyplot as plt


def nicv(indir, outdir):

        tdb = TracesFilesystem(indir)
        # create a list for each component class:
        classes = [[0.0]]*255
        # count traces in directory:
        ntraces = len(os.listdir(indir))
        # create a list for total variance calculating
        total = []
        # initialize list of bad traces
        bad = []
        for i in range(ntraces):
            try:
                msg, crypt, trace = tdb.get_trace()
            except:
                print("WARNING: Trace", i, "was not processed.")
                bad.append(i)
                i = i + 1

        # initialize ncomponents which will contain number of components
        ncomponents = len(trace)
        # initialize a sum of inter-class variances and total variance for one component
        svar = 0
        tvar = 0
        # initialize nicv array
        nicv = [0.0]*ncomponents

        for i in range(ncomponents):
            tdb = TracesFilesystem(dir)
            while(1):
                if i not in (bad):
                    try:
                        msg, crypt, trace = tdb.get_trace()
                    except:
                        print("WARNING: Trace", i, "was not processed.")
                        bad.append(i)
                        ntraces = ntraces - 1
                        msg = 'err'
                if not msg: # At the end of the database
                    print("WARNING: All files used!!")
                    sys.exit(1)
                if msg != 'err':
                    classes[int(msg[0:2], 16)].append(trace[i])
                    total.append(trace[i])
            for c in classes:
                svar = svar + statistics.variance(c)
            tvar = statistics.variance(total)

            nicv[i] = svar/tvar
            print("NICV for component", i, "was calculated ...")

            classes = [[0.0]]*255
            total = []

        print("NICV was calculated for all components! Let's draw the graph ...")

        plt.bar(range(0,  ncomponents), nicv, color='g')
        plt.ylabel('NICV')
        plt.xlabel('#components')
        plt.colors()
        plt.show()

        print("Save NICV statistics in NICV.csv ...")

        print("Done!")


def test():
    nicv("C:\PB_HOME\SECMATV\/test", "C:\PB_HOME\SECMATV\/test")

if __name__ == "__main__":
    print("Using ", "C:\PB_HOME\SECMATV\test")
    test()

"""
        idListLen = len(idList)
        errList = []
        meanList = []
        varList = []

        cmd = "SELECT message, cipher, data FROM trace WHERE id = '" + str(idList[0]) + "'"
        db.cur.execute(cmd)
        one = db.cur.fetchone()
        tmsg, tcrypt, traw_data = one

        parse_data = parse_binary(str(traw_data))
        points = len(parse_data)
        print "Points in trace:", points

        print "Calculating ..."

        #classList = [[0.0] * points]*256
        tclassList = [0.0] * points
        tMeanList = [0.0] * points
        tPowerMeanList = [0.0] * points
        parallels = 500
        #tGlobalVarlist = [[]]*parallels
        tGlobalVarlist = [[] for i in range(parallels)]
        classList = []*256
        #globalVarlist = [0.0] * points
        globalVarlist = []
        byteList = []

        #classList.append([1, 2, 3])
        #classList.append([1, 2, 3])
        #print "Test len:", len(classList[0]), len(classList[1])

        collected = 0
        classCalcCount = 0
        classCountNotIncluded = 0
        tracesInClass = 0

        #for i in range(points):
        for i in range(points//parallels):

            start_time = time.time()
            if collected == 0:
                for j in range (idListLen):
                    err = 0

                    cmd = "SELECT message, data FROM trace WHERE id = '" + str(idList[j]) + "'"
                    db.cur.execute(cmd)
                    one = db.cur.fetchone()
                    msg, raw_data = one

                    try:
                        parse_data = parse_binary(str(raw_data))
                    except:
                        err = 1
                        errList.append(idList[j])
                        #print 'Error. Trace ID: ', idList[j]

                    if err == 0:
                        for k in range(parallels):
                            tGlobalVarlist[k].append(parse_data[i*parallels+k])

                        parse_data = None
                        byteList.append((int(msg[0:2], 16), idList[j]))

                    if j%20000 == 0:
                        print j, "traces were processed."

                for m in range(parallels):
                    globalVarlist.append(numpy.var(numpy.array(tGlobalVarlist[m])))

                tGlobalVarlist = None
                tGlobalVarlist = [[] for m in range(parallels)]

                collected = 1

            else:

                for j in range (idListLen):
                    err = 0

                    cmd = "SELECT message, data FROM trace WHERE id = '" + str(idList[j]) + "'"
                    db.cur.execute(cmd)
                    #one = db.cur.fetchone()
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

                    if j%20000 == 0:
                        print j, "traces were processed."

                for m in range(parallels):
                    globalVarlist.append(numpy.var(numpy.array(tGlobalVarlist[m])))

                print "TEST:", len(globalVarlist)

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
                    #one = db.cur.fetchone()
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
                    #tMeanList[m] = tMeanList[m]/tracesInClass
                    tPowerMeanList[m] = tPowerMeanList[m]/tracesInClass - (tMeanList[m]/tracesInClass)**2
                print "Var[E(Y|X)] for class", i, "was calculated"
                classList.append(tPowerMeanList)
            else:
                classCountNotIncluded = classCountNotIncluded + 1
                print "Class was empty!"

            tMeanList = [0.0] * points
            tPowerMeanList = [0.0] * points

        print "Classes:", 256 - classCountNotIncluded

        for i in range(256 - classCountNotIncluded):
            for j in range(points):
                if i != 0:
                    classList[0][j] = classList[0][j] + classList[i][j]

        print "Total Var[E(Y|X)] for all classes was calculated!"

        lenn = points//parallels*parallels
        for i in range(lenn):
            globalVarlist[i] = classList[0][i]/globalVarlist[i]/lenn

        print "NICV function was calculated!"

        t = open("nicv", "w")
        for i in range(lenn):
            t.write(str(globalVarlist[i]) + ' ')
        t.close()

        plt.bar(range(0, lenn), globalVarlist, color='g')
        plt.ylabel('NICV')
        plt.xlabel('samples')
        plt.colors()
        plt.show()
"""