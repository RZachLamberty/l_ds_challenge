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
NSIM = 1000
NSAMP = 10000


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
#   simulation version          #
# ----------------------------- #

def main(fname=FNAME, nSimul=NSIM, nSamp=NSAMP, numRoutes=5,
         randSeed=SEED, oname=ONAME):
    bestyet = find_hot_routes(
        fname=fname,
        nSimul=nSimul,
        nSamp=nSamp,
        numRoutes=numRoutes,
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


def find_hot_routes(fname=FNAME, nSimul=NSIM, nSamp=NSAMP, numRoutes=5,
                    randSeed=SEED, oname=ONAME):
    """ docstring """
    df = load_data(fname)
    numpy.random.seed(seed=randSeed)
    bestyet = {}

    coordBounds = coordinate_bounds(df)

    for (i, H) in random_routes(coordBounds, nSimul):
        if i % (nSimul // 100) == 0:
            print '{:2d}% done'.format(i // (nSimul // 100))
        fa = fAvg(H, random_ride_sample(df, nSamp))
        bestyet = best_yet(bestyet, fa, H, numRoutes)

    return bestyet


def coordinate_bounds(df):
    """ find the bounding values for the df """
    return [
        df.start_lat.min(),
        df.start_lat.max(),
        df.start_lng.min(),
        df.start_lng.max(),
        df.end_lat.min(),
        df.end_lat.max(),
        df.end_lng.min(),
        df.end_lng.max(),
    ]


def random_routes(coordBounds, nSimul=NSIM):
    """ randomly choose a start and end point H. Use properties of df """
    x0Min, x0Max, y0Min, y0Max, x1Min, x1Max, y1Min, y1Max = coordBounds
    i = 0
    while i < nSimul:
        yield (
            i,
            [
                [
                    numpy.random.uniform(x0Min, x0Max),
                    numpy.random.uniform(y0Min, y0Max)
                ],
                [
                    numpy.random.uniform(x1Min, x1Max),
                    numpy.random.uniform(y1Min, y1Max)
                ],
            ]
        )
        i += 1


def random_ride_sample(df, nSamp=NSAMP):
    """ return a random sample of nSamp rows from df"""
    return df.iloc[random.sample(df.index, nSamp)]


def best_yet(bestyet, probNow, H, numRoutes):
    """ if the average probability of a ride for route H is among the numRoutes
        best values in bestyet, add it and drop the lesser of them

    """
    if len(bestyet) < numRoutes:
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
