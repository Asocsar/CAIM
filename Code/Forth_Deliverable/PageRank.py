#!/usr/bin/python

from collections import namedtuple
import time
import sys
import re
import numpy as np
from fractions import Fraction


class Airport:
    def __init__ (self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []
        self.routeHash = dict()
        self.outweight =  0.0

    #def __repr__(self):
    #    return f"{self.code}\t{self.pageIndex}\t{self.name}"


airportList = [] # list of Airport
airportHash = dict() # hash key IATA code -> Airport
sink_nodes = 0
L = 0.85
dumping_factors = np.linspace(0.8, 0.9, 10)
outp = open('output.txt', 'w')
times_out = open('times.txt', 'w')

def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r", encoding='utf8')
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5 :
                raise Exception('not an IATA code')
            a.name=temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code=temp[4][1:-1]
        except Exception as inst:
            pass
        else:
            cont += 1
            airportList.append(a)
            airportHash[a.code] = a
    airportsTxt.close()
    print(f"There were {cont} Airports with IATA code")


def readRoutes(fd):
    print("Reading Routes file from", fd)
    routesTxt = open(fd, "r", encoding='utf8')
    cont = 0
    invalid = 0
    for line in routesTxt.readlines():
        line_splited = line.split(',')
        
        origin = line_splited[2]
        destin = line_splited[4]

        #in case some missing or invalid IATA code is found
        if not (re.match('[A-Z]{3}', origin) and re.match('[A-Z]{3}', destin)):
            continue

        airport_orig = None
        airport_dest = None
        
        if origin in airportHash and destin in airportHash:
            airport_orig = airportHash[origin]
            airport_dest = airportHash[destin]

            routes = airport_dest.routeHash

            if origin in routes:
                routes[origin] += 1
            else:
                routes[origin] = 1.0
            
            airport_orig.outweight += 1

        else:
            invalid += 1
        
        cont += 1
    
    routesTxt.close()

    global sink_nodes
    sink_nodes = len([x for x in airportList if x.outweight == 0])
    print(f"There were {cont} routes with IATA code and {invalid} invalid ammount of routes and {sink_nodes} sink_nodes")




def computePageRanks():
    
    N = len(airportHash)
    P = {K:1/N for K in airportHash}
    global L

    stop_condition = False
    iterations = 0

    nout = L/float(N)*sink_nodes
    out_prob = 1.0/(N)
    while not stop_condition:
        Q = {K:0 for K in airportHash}
        for name in airportHash:
            all_destinations = airportHash[name].routeHash
            suma = sum([(P[ID]*all_destinations[ID])/(airportHash[ID].outweight) for ID in all_destinations])
            Q[name] = L * suma + (1-L)/N + nout*out_prob
        

        out_prob = (1-L)/N + nout*out_prob
        stop_condition = all([abs(X-Y) <= 1*10**(-12) for (X,Y) in zip(list(P.values()), list(Q.values()))])
        P = Q
        iterations += 1

    return (P, iterations)
    

def outputPageRanks(pagerank):
    global L
    outp.write('Dumping Factor {}\n\n'.format(L))
    outp.write('*------------------------------*\n')
    outp.write('*------------------------------*\n')
    outp.write('*------------------------------*\n')
    for City in pagerank:
        print("The final score for {} is {}".format(City, pagerank[City]))
        outp.write("The final score for {} is {}\n".format(City, pagerank[City]))
    print(len(pagerank))
    print("Total probability {}".format( sum(list(pagerank.values()))))
    outp.write('*------------------------------*\n')
    outp.write("\n\nTotal probability {}\n\n".format( sum(list(pagerank.values()))))
    outp.write('*------------------------------*\n')

def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")
    global L
    for L_in in dumping_factors:
        L = L_in
        time1 = time.time()
        (pagerank, iterations) = computePageRanks()
        time2 = time.time()
        outputPageRanks(pagerank)
        print("#Iterations:", iterations)
        print("Time of computePageRanks():", time2-time1)
        times_out.write("Time of computePageRanks(): {}\n".format(time2-time1))
    
    times_out.close()
    outp.close()




if __name__ == "__main__":
    sys.exit(main())
