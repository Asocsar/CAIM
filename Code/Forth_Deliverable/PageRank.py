#!/usr/bin/python

from collections import namedtuple
import time
import sys
import re

class Edge:
    def __init__ (self, origin, dest):
        self.origin = origin 
        self.dest = [dest]
        self.weight = 1

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)
        
    ## write rest of code that you need for this class

class Airport:
    def __init__ (self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []
        self.routeHash = dict()
        self.outweight =  0 

    def __repr__(self):
        return f"{self.code}\t{self.pageIndex}\t{self.name}"

edgeList = [] # list of Edge
edgeHash = dict() # hash of edge to ease the match
airportList = [] # list of Airport
airportHash = dict() # hash key IATA code -> Airport

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

        if origin in edgeHash:
            edgeHash[origin].weight += 1
            if not destin in edgeHash[origin].dest:
                edgeHash[origin].dest.append(destin)
        else:
            E = Edge(origin, destin)
            edgeHash[origin] = E
        
        try:
            if destin not in airportHash[origin].routeHash:
                airportHash[origin].routeHash[destin] = 0

            airportHash[origin].routeHash[destin] += 1
            airportHash[origin].outweight += 1

        except Exception:
            invalid += 1
            continue
        
        
        cont += 1
    
    routesTxt.close()
    print(f"There were {cont} routes with IATA code and {invalid} invalid ammount of routes")

def computePageRanks():
    print('ho')
    return 'po'
    # write your code

def outputPageRanks():
    print('hy')
    # write your code

def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")
    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    outputPageRanks()
    print("#Iterations:", iterations)
    print("Time of computePageRanks():", time2-time1)


if __name__ == "__main__":
    sys.exit(main())
