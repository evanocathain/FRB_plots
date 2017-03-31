#/usr/bin/python

import argparse
import sys

# Parse command line arguments
parser = argparse.ArgumentParser()
#parser.add_argument('-i', dest='input_file', help='set the input file name (default: file)', default="file")
#parser.add_argument('-p1', type=float, dest='p1', help='set the lowest period (default: 0.1 seconds)', default=0.100)
#parser.add_argument('-p2', type=float, dest='p2', help='set the lowest period (default: 10.0 seconds)', default=10.0)
#parser.add_argument('-maxdiff', type=float, dest='maxdiff', help='maximum time difference to use (default: 3600.0 seconds)', default=3600.0)
parser.add_argument('-id', dest='id', help='label plot with FRB idents (default: false)', action="store_true",default=False)
parser.add_argument('-update', dest='update', help='update to current FRBCAT sources (default: false)', action="store_true",default=False)
parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
args = parser.parse_args()

# Get the most up to date information from FRBCAT
if args.update:
    import os
    os.system('wget -O frbcat.csv "http://www.astronomy.swin.edu.au/pulsar/frbcat/table.php?format=text&amp;sep=comma"')
#wget -O frbcat.csv "http://www.astronomy.swin.edu.au/pulsar/frbcat/table.php?format=text&amp;sep=comma"

# Read the CSV file from FRBCAT
import numpy as np
frbs = np.zeros((56,3), dtype=object)
i = 0
import csv, sys
file = open("frbcat.csv", 'rb')
try:
    reader = csv.DictReader(file)
    for row in reader: 
        array = row['Name'],row['RAJ'], row['DECJ']           
        frbs[i]=array
        i = i +1
finally:
    file.close()  

import ephem as e
import math as m
deg2rad=m.pi/180.0
rad2deg=1.0/deg2rad
ids = np.zeros(56,dtype=object) # FRB names
gl = np.zeros(56)
gb = np.zeros(56)
for i in range(0,56):
    ids[i] = frbs[i][0]
    radec = e.Equatorial(frbs[i][1],frbs[i][2], epoch='2000')
    g = e.Galactic(radec)
    if (g.lon > m.pi):
        gl[i] = g.lon - m.pi*2.0
    else:
        gl[i] = g.lon
    gb[i] = g.lat
    #print('%.2f %.2f' % (g.lon,g.lat))
    #print('%s %s' % (g.lon,g.lat))
#    print('%s %s' % (g.lon*rad2deg,g.lat*rad2deg))

print gl*rad2deg,gb*rad2deg
import matplotlib.pyplot as plt
plt.figure()
plt.subplot(111, projection="aitoff")
#plt.title("FRB Galactic Coordinate Distribution - Aitoff Projection")
plt.grid(True)
plt.plot(gl,gb, 'o')
# Optional plotting features
if args.id:
    for i in range(0,56):
        plt.text(gl[i],gb[i],ids[i],fontsize=10) # Obviously this can be tweaked
plt.show()
