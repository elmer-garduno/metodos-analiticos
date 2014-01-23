from collections import defaultdict
import hashlib
import random as pyrand
import pyhash
import sys
import math

# The following two methods where adapted from
# https://github.com/twitter/algebird/blob/master/algebird-core/src/main/scala/com/twitter/algebird/MinHasher.scala
# Numerically solve the inverse of threshold, given numBands*numRows

def pick_bands(threshold, hashes):
    target = hashes * -1 * math.log(threshold)
    bands = 1
    while bands * math.log(bands) < target:
        bands += 1
    return bands

def pick_hashes_and_bands(threshold, max_hashes):
    bands = pick_bands(threshold, max_hashes)
    hashes = (max_hashes / bands) * bands
    return (hashes, bands)

def jaccard(c1, c2):
    num = len(c1.intersection(c2))
    den = len(c1.union(c2))
    return num / float(den)

def get_conf(threshold):
    hashes, bands = pick_hashes_and_bands(threshold, 100)
    rnd = pyrand.Random(11)
    return  {
        'hashes': hashes,
        'b': bands,
        'r': hashes / bands,
        'band_seed': rnd.randint(0,100000),
        'seeds': [rnd.randint(0,100000) for _ in range(hashes)]
    }

class LSH(object):

    def __init__(self, conf):
        self.hashes = conf['hashes']
        self.b = conf['b']
        self.r = conf['r']
        self.band_seed = conf['band_seed']
        self.seeds = conf['seeds']

        self.hasher = pyhash.murmur3_32()

    def signature(self, col):
        minhashes = [sys.maxint] * self.hashes
        for i in range(self.hashes):
            hashes = [self.hasher(_, seed=self.seeds[i]) for _ in col]
            minhashes[i] = min(hashes)
        return minhashes

    def lsh(self, col):
        minhashes = self.signature(col)
        bands = [] 
        for i in xrange(0, len(minhashes), self.r):
            band = str(minhashes[i:i + self.r]) 
            h = str(i) + '-' + str(self.hasher(band, seed=self.band_seed)) 
            bands.append(h)
        return bands
