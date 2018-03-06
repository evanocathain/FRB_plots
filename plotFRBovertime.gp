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

set label "{/Symbol S} FRBs = 53" at 2001.5, 6 font ",20"

set yrange[0:17.5]
plot "all_FRBs" using 2:xtic(1) title 'Parkes', '' u 3 title 'UTMOST', '' u 4 title 'GBT', '' u 5 title 'Arecibo', '' u 6 title 'ASKAP', '' u 7 title 'DSA-10'
