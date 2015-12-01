from TracesFilesystem import *
from time import time
import math
from Database import Database
import numpy
import matplotlib.pyplot as plt


def nicv(self, db, idList):

        start_time = time.time()
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
        print("Points in trace:", points)

        print("Calculating ...")

        tclassList = [0.0] * points
        tMeanList = [0.0] * points
        tPowerMeanList = [0.0] * points
        parallels = 20
        tGlobalVarlist = [[] for i in range(parallels)]
        classList = []*256
        globalVarlist = []
        byteList = []

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

                    if err == 0:
                        for k in range(parallels):
                            tGlobalVarlist[k].append(parse_data[i*parallels+k])

                        parse_data = None
                        byteList.append((int(msg[0:2], 16), idList[j]))

                    if j%parallels == 0 and j != 0:
                        print(j, "traces were processed.")

                for m in range(parallels):
                    globalVarlist.append(numpy.var(numpy.array(tGlobalVarlist[m])))

                tGlobalVarlist = [[] for m in range(parallels)]

                collected = 1

            else:

                for j in range (idListLen):
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

                    if j%20000 == 0:
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


def test():
    db = Database()
    db.connect()
    idList = db.get_trace_idlist('des_first')
    nicv(db, idList)

if __name__ == "__main__":
    print("Using ", "C:\PB_HOME\SECMATV\test")
    test()