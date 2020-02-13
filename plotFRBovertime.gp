#!/bin/csh

# 05/03/2018
# Evan Keane
# A script to plot FRBs as a function of time 
# for all telescopes that have found an FRB
#
# Published (on FRBCAT) FRBs list shown, full list
# including unpublished FRBs is in .gitignore

#set term x11
set term postscript enhanced color solid
set output "FRBovertime.ps"

set key top left

#set title "FRB Discoveries over Time" font ", 20"

set ylabel "FRBs per year" font ", 20"
set xlabel "Year" font ",20"

set style data histogram
set style histogram rowstacked
set style fill solid 0.5
set boxwidth 1.0

set xtics 1 font ", 10"
set mytics 5

# Add some updated labels for when this plot was made
num_frbs=system("awk '{for (i=2; i<=NF; i++) s+=$i}END{print s}' all_FRBs")
set label sprintf("{/Symbol S} FRBs %s", num_frbs) front at -0.5, 27 font ", 20"
#set label sprintf("{/Symbol S} FRBs %s", num_frbs) front at -0.5, 13 font ", 20"
timestamp=system("date -u \"+%Y-%m-%d UTC\"")
set label timestamp front at -0.5, 25 font ", 10"
set label "\\\@evanocathain" front at -0.5, 24 font ", 10" textcolor rgb '#1DCAFF'

# Do a H1-2018 note
#set label sprintf("(Jan-Jun)") front at 16.4, -1.4 font ", 10"

set yrange[0:44.5]
plot "all_FRBs" using 2:xtic(1) title 'Parkes', '' u 3 title 'UTMOST', '' u 4 title 'GBT', '' u 5 title 'Arecibo', '' u 6 title 'ASKAP', '' u 7 title 'CHIME' lt 8, '' u 8 title 'DSA-10' lt 7, '' u 9 title 'WSRT' lt rgb '#7FFFD4'
