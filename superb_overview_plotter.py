#!/usr/bin/python

# Name: Heimdall Overview Plotter
#
# Description: Creates overview plots of candidates found by Heimdall. It distinguishes 
# between noise, RFI, erroneous candidates, and valid candidates, plotting them all in different ways.
# Output is an overview plot called overview.png in the directory of the program.
#
# History: 2010: created by Ben Barsdell
#          2012: edited by Emily Petroff
#          2017: edited by Evan Keane

import numpy as np

class Classifier(object):
    def __init__(self):
        self.nbeams      = 13
        self.snr_cut     = 7
        self.members_cut = 3
        self.nbeams_cut  = 3
        self.dm_cut      = 1.5
        self.filter_cut  = 10
        self.beam_mask   = (1<<13) - 1
        self.filter_max  = 12
        
    def is_masked(self, beam):
        return ((1<<beam) & self.beam_mask) == 0
    
    def is_hidden(self, cand):
        return ( (cand['snr'] < self.snr_cut) |
                 (cand['filter'] > self.filter_cut) |
                 self.is_masked(cand['beam']) |
                 ((self.is_masked(cand['beam']) != True) &
                  (cand['beam'] != cand['prim_beam'])) )
    
    def is_noise(self, cand):
        return cand['members'] < self.members_cut

    def is_fat(self, cand):
        return cand['filter'] >= self.filter_max
    
    def count_nbeams(self, mask):
        n = 0
        for i in range(self.nbeams):
            n += (mask & (1<<i)) > 0
        return n
            
    def is_coinc_rfi(self, cand):
        nbeams = self.count_nbeams(cand['beam_mask'] & self.beam_mask)
        return nbeams > self.nbeams_cut
    
    def is_lowdm_rfi(self, cand):
        return cand['dm'] < self.dm_cut

class TimeDMPlot(object):
    def __init__(self, g):
        self.g = g
        self.dm_base = 1.0
        self.snr_min = 6.0
        
    def plot(self, data):
        self.g.reset()
        self.g('set tmargin at screen 0.6')
        self.g('set bmargin at screen 0.0')
        self.g('set rmargin at screen 1.0')
        self.g('set lmargin at screen 0.0')
        self.g('set size 1.0,0.6')
        self.g('set origin 0.0,0.0')
        self.g('unset key')
        self.g('set autoscale x')
        self.g('set logscale y')
        self.g('set logscale y2')
        self.g('set yrange[1.0:10000]')
        self.g('set y2range[1.0:10000]')
        self.g('set cbrange[-0.5:12.5]')
        self.g('set palette positive nops_allcF maxcolors 13 gamma 1.5 color model RGB')
        self.g("set palette defined ( 0 'green', 1 'cyan', 2 'magenta', 3 'orange' )")
        self.g('unset colorbox')
        self.g("set style line 12 lc 'grey'")
        self.g('set grid noxtics nomxtics ytics mytics lt 9 lw 0.2, ls 12')
        self.g('set ytics 10')
        self.g('set mytics 10')
        self.g('set y2tics 10 mirror format ""')
        self.g('set my2tics 10')
	self.g('set xtics 60')
        self.g('set x2tics 60 mirror format ""')
        self.g('set mxtics 4')
        self.g('set mx2tics 4')
        self.g('set xlabel "Time [s]"')
        self.g('set ylabel "DM + 1 [pc cm^{-3}]"')
        self.g('set format y "10^{%T}"')
        self.g('min(x,y) = x<=y?x:y')
        self.g('max(x,y) = x>=y?x:y')

        categories = []

        if len(data['lowdm']) > 0:
            lowdm = Gnuplot.Data(data['lowdm']['snr'],
                                 data['lowdm']['time'],
                                 data['lowdm']['filter'],
                                 data['lowdm']['dm'],
                                 using="2:($4+%f):(min(($1-%f)/2.0+0.9,5)):3" \
                                     % (self.dm_base,self.snr_min),
                                 with_="p pt 6 lt palette ps variable")
            categories.append(lowdm)
            
            lowdmlabels = Gnuplot.Data(data['lowdm']['beam'],
                                       data['lowdm']['time'],
                                       data['lowdm']['dm'],
                                       using='2:($3+%f):(sprintf("%%d",$1+1))' \
                                           % (self.dm_base),
                                       with_='labels center font ",7" offset 0,0.05 textcolor rgbcolor "black"')
            categories.append(lowdmlabels)

        if len(data['valid']) > 0:
            valid = Gnuplot.Data(data['valid']['snr'],
                                 data['valid']['time'],
                                 data['valid']['filter'],
                                 data['valid']['dm'],
                                 using="2:($4+%f):(min(($1-%f)/2.0+0.9,5)):3" \
                                     % (self.dm_base,self.snr_min),
                                 with_="p pt 7 lt palette ps variable")
            categories.append(valid)
            
            validlabels = Gnuplot.Data(data['valid']['beam'],
                                       data['valid']['time'],
                                       data['valid']['dm'],
                                       using='2:($3+%f):(sprintf("%%d",$1+1))' \
                                           % (self.dm_base),
                                       with_='labels center font ",7" offset 0,0.05 textcolor rgbcolor "black"')
            categories.append(validlabels)

        """
        self.g.plot(noise, coinc,
                    fat, fatlabels,
                    lowdm, lowdmlabels,
                    valid, validlabels)
        """
        self.g.plot(*categories)

class DMSNRPlot(object):
    def __init__(self, g):
        self.g = g
        self.dm_base = 1.0
        self.snr_base = 5.9
        self.max_filter = 12
        self.dt = 64e-6
    def plot(self, data):
        self.g.reset()
        # define the plotting region
        self.g('set tmargin at screen 1.0')
        self.g('set bmargin at screen 0.65')
        self.g('set rmargin at screen 0.84')
        self.g('set lmargin at screen 0.56')
        self.g('set size 0.28,0.35')
        self.g('set origin 0.54,0.65')
        # define the plot labelling, axes, ranges, format etc.
        self.g('unset key')
        self.g('set xrange[1.0:10000]')
        self.g('set x2range[1.0:10000]')
        self.g('set logscale x')
        self.g('set logscale x2')
        self.g('set ytics 10')
        self.g('set mytics 10')
        self.g('set y2tics 10 mirror format ""')
        self.g('set x2tics 10 mirror format ""')
        self.g('set my2tics 10')
        self.g('set ytics mirror')
        self.g('set format y ""')
        self.g("set style line 12 lc 'grey'")
        self.g('set pointsize 5')
        self.g('set grid xtics mxtics noytics nomytics lt 9 lw 0.2 ls 12')
        self.g('set logscale y')
        self.g('set logscale y2')
        self.g('set yrange[1:100]') # arbitrary!
        self.g('set y2range[1:100]') # arbitrary!
        self.g('set yrange[6.0:25]') # arbitrary! but at least makes sense for my purposes for SUPERB Paper 1 -> to do: fix later
        self.g('set y2range[6.0:25]') # arbitrary! but at least makes sense for my purposes for SUPERB Paper 1 -> to do: fix later
        self.g('set cbrange[-0.5:12.5]')
        self.g('set palette positive nops_allcF maxcolors 13 gamma 1.5 color model RGB')
        self.g("set palette defined ( 0 'green', 1 'cyan', 2 'magenta', 3 'orange' )")
        self.g('set colorbox vertical user origin 0.9,0.65 size 0.025,0.35')
        self.g('snr_min = %f' % self.snr_base)
        self.g('set cbtics 1 format ""')
        filter_tics = [2000*self.dt * 2**i for i in range(self.max_filter+1)]
        self.g('set cbtics add ('+', '.join(['"%.4g" %i'%(x,i) for i,x in enumerate(filter_tics)])+')')
        self.g('set x2label "DM+1 [pc cm^{-3}]"')
        self.g('set ylabel "SNR"')
        self.g('set ylabel ""')
        self.g('set y2label "S/N" offset screen -0.03,0.03 rotate by 270')
        self.g('set format y ""')
        self.g('set format y2 "10^{%T}"')
        self.g('set format x ""')
        self.g('set format x2 "10^{%T}"')
#        self.g('set cblabel "Boxcar width [ms]"')
        self.g('set label "Width [ms]" at screen 0.9,1.025 front')

        categories = []

        if len(data['valid']) > 0:
            valid = Gnuplot.Data(data['valid']['snr'],
                                 data['valid']['dm'],
                                 data['valid']['filter'],
                                 using="($2+%f):($1):3" \
                                     % (self.dm_base),
                                 with_="p pt 7 ps 0.8 lt palette")
            categories.append(valid)
            
        self.g.plot(*categories)

class DMHistogram(object):
    def __init__(self, cands=None):
        self.dm_min   = 0.10
        self.dm_max   = 1010.0
        self.dm_max   = 10010.0
        self.min_bins = 30
        self.hist     = None
        if cands is not None:
            self.build(cands)
            
    def build(self, cands):
        import math
        cands = cands[cands['filter'] <= 10]
        N = len(cands)
        log_dm_min = math.log10(self.dm_min)
        log_dm_max = math.log10(self.dm_max)
        nbins    = max(self.min_bins, 2*int(math.sqrt(N)))
        binwidth = (log_dm_max - log_dm_min) / nbins
        bins_    = 10**(log_dm_min + (np.arange(nbins)+0.5)*binwidth)
        dms      = np.maximum(cands['dm'], self.dm_min)
        log_dms  = np.log10(dms)
        vals, edges = np.histogram(log_dms, bins=nbins,
                                   range=(log_dm_min,log_dm_max))
        self.hist = np.rec.fromrecords(np.column_stack((bins_, vals)),
                                       names=('bins', 'vals'))
class SNRHistogram(object):
    def __init__(self, cands=None):
        self.snr_min   = 6.0
        self.snr_max   = 100.0
        self.min_bins = 50
        self.hist     = None
        if cands is not None:
            self.build(cands)
            
    def build(self, cands):
        import math
        cands = cands[cands['filter'] <= 13]
        N = len(cands)
        log_snr_min = math.log10(self.snr_min)
        log_snr_max = math.log10(self.snr_max)
#	nbins	= self.min_bins
        nbins    = max(self.min_bins, 2*int(math.sqrt(N)))
        binwidth = (self.snr_max - self.snr_min) / nbins
        bins_    = self.snr_min + (np.arange(nbins)+0.5)*binwidth
        snrs      = np.maximum(cands['snr'], self.snr_min)
        log_snrs  = np.log10(snrs)
        vals, edges = np.histogram(snrs, bins=bins_,
                                   range=(self.snr_min,self.snr_max))
        vals_n = np.append(vals, 0)
        self.hist = np.rec.fromrecords(np.column_stack((bins_, vals_n)),
                                       names=('bins', 'vals'))


class NSNRPlot(object):
    def __init__(self, g):
        self.g = g
        self.n_base = 1.0
        self.snr_base = 5.9
        self.max_filter = 12
        self.dt = 64e-6
    def plot(self, data):
        self.g.reset()
        self.g('set tmargin at screen 1.0')
        self.g('set bmargin at screen 0.65')
        self.g('set rmargin at screen 0.56')
        self.g('set lmargin at screen 0.28')
        self.g('set size 0.28,0.35')
        self.g('set origin 0.28,0.65')
        self.g('unset ylabel')
        self.g('set format y ""')
        self.g('unset key')
        self.g('set xrange[6.0:100]')
        self.g('set x2range[6.0:100]')
        self.g('set xrange[6.0:25]') # hack
        self.g('set x2range[6.0:25]') # hack
        self.g('set xtics 10')
        self.g('set mxtics 10')
	self.g('set x2tics 10 mirror format ""')
        self.g('set logscale x')
        self.g('set logscale x2')
        self.g('set ytics 10')
        self.g('set mytics 10')
        self.g('set y2tics 10 mirror format ""')
        self.g('set my2tics 10')
        self.g('set ytics mirror')
        self.g("set style line 12 lc 'grey'")
        self.g('set grid noytics nomytics xtics mxtics lt 9 lw 0.2, ls 12')
        self.g('set logscale y')
        self.g('set logscale y2')
        self.g('set yrange[0.5:2000]')
        self.g('set y2range[0.5:2000]')
        self.g('set cbrange[-0.5:12.5]')
        self.g('set palette positive nops_allcF maxcolors 13 gamma 1.5 color model RGB')
        self.g("set palette defined ( 0 'green', 1 'cyan', 2 'magenta', 3 'orange' )")
        self.g('snr_min = %f' % self.snr_base)

        self.g('set x2label "S/N"')
#        self.g('set ylabel "Candidate count"')
        self.g('set ylabel ""')
        self.g('set format x ""')
        self.g('set format x2 "10^{%T}"')

	beams = []
	for b,snr_hist in enumerate(data):
            beams.append( Gnuplot.Data(snr_hist['bins'],
                                       snr_hist['vals'],
                                       with_='histeps lw %i lt 1 lc %i' \
                                           % (1+(b+1<8),b+1),
                                       title=str(b+1)) )
        self.g.plot(*beams)

class DMHistPlot(object):
    def __init__(self, g):
        self.g = g
        self.dm_base = 1.0
        self.snr_base = 5.9
        self.max_filter = 12
        self.dt = 64e-6
    def plot(self, data):
        self.g.reset()
        self.g('set tmargin at screen 1.0')
        self.g('set bmargin at screen 0.65')
        self.g('set rmargin at screen 0.28')
        self.g('set lmargin at screen 0.0')
        self.g('set size 0.28,0.35')
        self.g('set origin 0.0,0.65')
        self.g('unset key')
        self.g('set logscale x')
        self.g('set xrange[1:10000]')
        self.g('set logscale x2')
        self.g('set x2range[1:10000]')
        self.g('set logscale y')
        self.g('set logscale y2')
        self.g('set yrange [0.5:2000]')
        self.g('set y2range [0.5:2000]')
        self.g('set xtics 10')
        self.g('set mxtics 10')
        self.g('set x2tics 10 mirror format ""')
        self.g('set mx2tics 10')
        self.g('set ytics 10')
        self.g('set y2tics 10 mirror format ""')
        self.g('set mytics 10')
        self.g('set my2tics 10')
        self.g("set style line 12 lc 'grey'")
        self.g('set grid noxtics nomytics xtics mxtics lt 9 lw 0.2, ls 12')
        #self.g('set key inside top center horizontal samplen 2 maxcols 2')
        self.g('set key box top right horizontal samplen 2')
        self.g('set key spacing 0.9')
        self.g('set x2label "DM+1 [pc cm^{-3}]')
        self.g('set ylabel "Candidate count"')
        self.g('set format y "10^{%T}"')
        self.g('set format x ""')
        self.g('set format x2 "10^{%T}"')

        beams = []
        for b,dm_hist in enumerate(data):
            beams.append( Gnuplot.Data(dm_hist['bins'],
                                       dm_hist['vals'],
                                       using="($1+%f):2" \
                                           % (self.dm_base),
                                       with_='histeps lw %i lt 1 lc %i' \
                                           % (1+(b+1<8),b+1),
                                       title=str(b+1)) )
        self.g.plot(*beams)

if __name__ == "__main__":
    import argparse
#    import Gnuplot    
    import Gnuplot, Gnuplot.funcutils
    Gnuplot.GnuplotOpts.default_term = 'x11' # stops gnuplot-py freaking out if it fails to find Aqua terminal on osx

    parser = argparse.ArgumentParser(description="Generates data for Heimdall overview plots.")
    parser.add_argument('-f', default="candidates_all.cand")
    #parser.add_argument('-p', default="2014-10-30-13:29:21")
    parser.add_argument('-nbeams', type=int, default=13)
    parser.add_argument('-snr_cut', type=float)
    parser.add_argument('-beam_mask', type=int, default=(1<<13)-1)
    parser.add_argument('-nbeams_cut', type=int, default=2)
    parser.add_argument('-members_cut', type=int, default=3)
    parser.add_argument('-dm_cut', type=float, default=1.5)
    parser.add_argument('-filter_cut', type=int, default=99)
    parser.add_argument('-filter_max', type=int, default=12)
    parser.add_argument('-min_bins', type=int, default=30)
    parser.add_argument('-g', default="ps")
    parser.add_argument('-interactive', action="store_true")
    args = parser.parse_args()
    
    filename = args.f
    nbeams = args.nbeams
    interactive = args.interactive
    plotdevice = args.g

    # Load candidates from all_candidates file
    all_cands = \
        np.loadtxt(filename,
                   dtype={'names': ('snr','samp_idx','time','filter',
                                    'dm_trial','dm','members','begin','end',
                                    'nbeams','beam_mask','prim_beam',
                                    'max_snr','beam'),
                          'formats': ('f4', 'i4', 'f4', 'i4',
                                      'i4', 'f4', 'i4', 'i4', 'i4',
                                      'i4', 'i4', 'i4',
                                      'f4', 'i4')})
    # Adjust for 0-based indexing in python
    all_cands['prim_beam'] -= 1
    all_cands['beam'] -= 1
    
    print "Loaded %i candidates" % len(all_cands)
  
    print all_cands['snr'][0]
 
    classifier = Classifier()
    classifier.nbeams = args.nbeams
    classifier.snr_cut = args.snr_cut
    classifier.beam_mask = args.beam_mask
    classifier.nbeams_cut = args.nbeams_cut
    classifier.members_cut = args.members_cut
    classifier.dm_cut = args.dm_cut
    classifier.filter_cut = args.filter_cut
    classifier.filter_max = args.filter_max
    
    # Filter candidates based on classifications
    print "Classifying candidates..."
    categories = {}
    is_hidden = classifier.is_hidden(all_cands)
    is_noise  = (is_hidden==False) & classifier.is_noise(all_cands)
    is_coinc  = (is_hidden==False) & (is_noise ==False) & classifier.is_coinc_rfi(all_cands)
    is_fat    = (is_hidden==False) & (is_noise ==False) & (is_coinc ==False) & classifier.is_fat(all_cands)
    is_lowdm  = (is_hidden==False) & (is_noise ==False) & (is_fat   ==False) & (is_coinc ==False) & classifier.is_lowdm_rfi(all_cands)
    is_valid  = (is_hidden==False) & (is_noise ==False) & (is_fat   ==False) & (is_coinc ==False) & (is_lowdm ==False)
    categories["hidden"] = all_cands[is_hidden]
    categories["noise"]  = all_cands[is_noise]
    categories["coinc"]  = all_cands[is_coinc]
    categories["fat"]    = all_cands[is_fat]
    categories["lowdm"]  = all_cands[is_lowdm]
    categories["valid"]  = all_cands[is_valid]
    
    print "Classified %i as hidden," % len(categories["hidden"])
    print "           %i as noise spikes," % len(categories["noise"])
    print "           %i as coincident RFI," % len(categories["coinc"])
    print "           %i as fat RFI, and" % len(categories["fat"])
    print "           %i as low-DM RFI, and" % len(categories["lowdm"])
    print "           %i as valid candidates." % len(categories["valid"])
    
    print "Building histograms..."
    dm_hists = []
    for beam in range(nbeams):
        cands = all_cands[all_cands['beam'] == beam]
        dm_hists.append(DMHistogram(cands).hist)
    
    snr_hists = []
    for beam in range(nbeams):
         cands = all_cands[all_cands['beam'] == beam]
         snr_hists.append(SNRHistogram(cands).hist)

    # Generate plots
    print "Generating plots..."
    g = Gnuplot.Gnuplot(debug=0)
    if not interactive:
        if plotdevice == "ps":
            g('set terminal postscript enhanced color solid')
            g('set output "overview.ps"')
            print "Writing plots to overview.ps"
        elif plotdevice == "png":
            g('set terminal png enhanced font "arial,10" size 1280, 960')
            g('set output "overview.png"')
            print "Writing plots to overview.png"
    g('set size 1,1')
    g('set origin 0,0')
    g('set multiplot')
    timedm_plot = TimeDMPlot(g)
    dmsnr_plot  = DMSNRPlot(g)
    dmhist_plot = DMHistPlot(g)
    nsnr_plot = NSNRPlot(g)
    timedm_plot.plot(categories)
    dmsnr_plot.plot(categories)
    nsnr_plot.plot(snr_hists)
    dmhist_plot.plot(dm_hists)
#    g('plot "superb.jpg" binary filetype=jpg with rgbimage')
    g('unset multiplot')

    if interactive:
        raw_input('Please press return to close...\n')
        
    print "Done"
