#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: hotroutes.py
Author: zlamberty
Created: 2015-05-06

Description:
    Calculate "hot routes," routes specifically designed to be favorable for
    users who are lazy as fuck

Usage:
    <usage>

"""

import argparse
import csv
import numpy
import pandas
import random


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

# lat / long constants
ALPHA = 111.2
BETA = 84.2
AB = numpy.array([ALPHA, BETA])

# data files
FNAME = './rides.csv'
ONAME = './hotroutes.csv'
FIELDNAMES = ['start_lat', 'start_lng', 'end_lat', 'end_lng']

# rand
SEED = 17
NROUTES = 10000
NRIDES = 10000


# ----------------------------- #
#   utility functions           #
# ----------------------------- #

def load_data(fname=FNAME):
    #return pandas.read_csv(fname)
    # I don't care about most of the columns..
    return pandas.read_csv(fname)[['start_lat', 'start_lng', 'end_lat', 'end_lng']]


def manhattan(a, B, coeffs = AB):
    """ take a singular pair of coordinates and a pandas dataframe of input
        values (col 0 is x coord, col 1 is y coord), and return a dataframe of
        manhattan distances

    """
    x = AB * (B - a).abs()
    return x.lat + x.lng


def f(H, p, d):
    P, D = H
    return numpy.exp(
        -(manhattan(P, p) + manhattan(D, d))
    )


def fAvg(H, r):
    """ average of hotroute H given distribution of rides r """
    p = r[['start_lat', 'start_lng']]
    p.columns = ['lat', 'lng']
    d = r[['end_lat', 'end_lng']]
    d.columns = ['lat', 'lng']

    return f(H, p, d).sum()


# ----------------------------- #
#   hotroute calculation        #
# ----------------------------- #

def main(fname=FNAME, nRoutes=NROUTES, nRides=NRIDES, keepBest=5, randSeed=SEED,
         oname=ONAME):
    bestyet = find_hot_routes(
        fname=fname,
        nRoutes=nRoutes,
        nRides=nRides,
        keepBest=keepBest,
        randSeed=randSeed,
    )

    # write that ish to file as requested
    with open(oname, 'w') as fOut:
        c = csv.DictWriter(fOut, fieldnames=FIELDNAMES)
        c.writeheader()
        c.writerows([
            {
                'start_lat': H[0][0],
                'start_lng': H[0][1],
                'end_lat': H[1][0],
                'end_lng': H[1][1],
            }
            for (fa, H) in bestyet.items()
        ])


def find_hot_routes(fname=FNAME, nRoutes=NROUTES, nRides=NRIDES, keepBest=5,
                    randSeed=SEED, oname=ONAME):
    """ Find the 5 best combos of pickup / dropoff locales in the data """
    df = load_data(fname)
    bestyet = {}

    for route in routes(df, nRoutes):
        sampleRides = sample_rides(df, nRides)
        fa = fAvg(route, sampleRides)
        bestyet = best_yet(bestyet, fa, route, keepBest)

    return bestyet


def routes(df, nRoutes=NROUTES):
    i = 0
    onePerCent = (nRoutes // 100)
    #for route in product_route(df):
    for route in random_route(df):
        # just a stupid progress bar
        if i % onePerCent == 0:
            print '{:2d}% done'.format(i // onePerCent)

        yield route

        i += 1
        if i == nRoutes:
            break


def random_route(df):
    """ randomly choose a start and end point H. Use properties of df """
    L = df.shape[0]
    i = 0
    while i < L:
        route = df.iloc[numpy.random.randint(0, L)]
        yield [[route.start_lat, route.start_lng], [route.end_lat, route.end_lng]]
        i += 1


def product_route(df):
    """ return an iterator which is merely the cartesian product of all
        pickup and dropoff points in df

    """
    L = df.shape[0]
    for i in xrange(L):
        # pickup location for ride i
        s = df.iloc[i]
        slat = s.start_lat
        slng = s.start_lng
        for j in xrange(L):
            # dropoff location for ride j
            e = df.iloc[j]
            elat = e.end_lat
            elng = e.end_lng
            yield [[slat, slng], [elat, elng]]


def sample_rides(df, nSample):
    """ given a data frame, return nSample random rows from it """
    return df.iloc[numpy.random.choice(df.index.values, nSample)]


def best_yet(bestyet, probNow, H, keepBest):
    """ if the average probability of a ride for route H is among the keepBest
        best values in bestyet, add it and drop the lesser of them

    """
    if len(bestyet) < keepBest:
        bestyet[probNow] = H
    else:
        minProb = min(bestyet.keys())
        if probNow > minProb:
            del bestyet[minProb]
            bestyet[probNow] = H

    return bestyet


# ----------------------------- #
#   Command line                #
# ----------------------------- #

def parse_args():
    """ Take a log file from the commmand line """
    parser = argparse.ArgumentParser()
    parser.add_argument("-x", "--xample", help="An Example", action='store_true')

    args = parser.parse_args()

    logger.debug("arguments set to {}".format(vars(args)))

    return args


if __name__ == '__main__':

    args = parse_args()

    main()
