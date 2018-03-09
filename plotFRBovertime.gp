#!/bin/csh

# 05/03/2018
# Evan Keane
# A script to plot FRBs as a function of time 
# for all telescopes that have found an FRB
#
# Current up to date list of all FRBs includes
# unpublished FRBs so this file is in .gitignore

set term x11
#set term postscript enhanced color solid
#set output "FRBovertime.ps"

set key top left

set title "FRB Discoveries over Time"

set ylabel "Number of FRBs"
set xlabel "Year"

set style data histogram
set style histogram rowstacked
set style fill solid 0.5
set boxwidth 1.0

set xtics 1

# Add some updated labels for when this plot was made
num_frbs=system("awk '{for (i=2; i<=NF; i++) s+=$i}END{print s}' all_FRBs")
set label sprintf("{/Symbol S} FRBs %s", num_frbs) front at -0.5, 13 font ", 20"
timestamp=system("date -u \"+%Y-%m-%d UTC\"")
set label timestamp front at -0.5, 12 font ", 10"
set label "\\\@evanocathain" front at -0.5, 11.5 font ", 10" textcolor rgb '#1DCAFF'

set yrange[0:17.5]
plot "all_FRBs" using 2:xtic(1) title 'Parkes', '' u 3 title 'UTMOST', '' u 4 title 'GBT', '' u 5 title 'Arecibo', '' u 6 title 'ASKAP', '' u 7 title 'DSA-10'
