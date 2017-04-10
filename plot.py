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
frbs = np.zeros((100,5), dtype=object)
i = 0
import csv, sys
file = open("frbcat.csv", 'rb')
try:
    reader = csv.DictReader(file)
    for row in reader: 
        array = row['Name'],row['RAJ'],row['DECJ'],row['UTC'],row['Telescope']
        frbs[i]=array
        i = i +1
finally:
    file.close()  
gl = np.zeros(i)
gb = np.zeros(i)
ids = frbs[:,0]
utc = frbs[:,3]
tel = frbs[:,4]

# Convert RA & DEC to gl & gb
import ephem as e
import math as m
deg2rad=m.pi/180.0
rad2deg=1.0/deg2rad
for i in range(0,56):
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

az = np.zeros(56)
alt = np.zeros(56)
# Convert RA, DEC & UTC to alt & az
for i in range(0,56):
    frb = e.FixedBody()
    frb._ra = frbs[i][1]
    frb._dec = frbs[i][2]
    site=e.Observer()
    if (tel[i]=="parkes"):
        site.long = '148:15:44.3'
        site.lat = '-32:59:59.8'
        site.elevation = 0
        place = "Parkes Observatory"
    elif (tel[i]=="GBT"):
        site.long = '-79:50:23'
        site.lat = '38:25:59'
        site.elevation = 0
        place = "Green Bank Telescope"
    elif (tel[i]=="arecibo"):
        site.long = '-66:45:10'
        site.lat = '18:20:39'
        site.elevation = 0
        place = "Arecibo"
    elif (tel[i]=="UTMOST"):
        site.long = '149.4241'
        site.lat = '35.3707'
        site.elevation = 0
        place = "Molonglo"
    site.date = utc[i]
    frb.compute(site)
    if (place == "Parkes Observatory"):
        az[i]=frb.az
        alt[i]=frb.alt
#        print ids[i],frb.az,frb.alt

#print gl*rad2deg,gb*rad2deg
# Plot things
# Aitoff projection
import matplotlib.pyplot as plt
plt.figure()
plt.subplot(111, projection="aitoff")
plt.title("FRB Galactic Coordinate Distribution - Aitoff Projection")
plt.grid(True)
plt.plot(gl,gb, 'o')
# Optional plotting features
if args.id:
    for i in range(0,56):
        plt.text(gl[i],gb[i],ids[i],fontsize=10) # Obviously this can be tweaked
plt.show()

print az*rad2deg,alt*rad2deg
# Alt-az plot
plt.clf()
sp = plt.subplot(111, projection="polar")
plt.title("Parkes FRB Zen-Az Distribution")
plt.grid(True)
#plt.plot(az*rad2deg,90.0-alt*rad2deg, 'o')
sp.set_theta_zero_location("N")
plt.plot(az,(0.5*m.pi-alt)*rad2deg, 'o')
plt.show()
