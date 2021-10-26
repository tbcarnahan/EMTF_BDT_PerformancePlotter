#!/usr/bin/env python3

import helpers.fileHelper as fileHelper

import hist
from hist import Hist
import mplhep as hep
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import scipy
import awkward
import sys
import os
import helpers.helper as helper

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] outputDir inputFiles")
    parser.add_option("--emtf-mode", dest="emtf_mode", type="long",
                     help="EMTF Track Mode", default=15)
    parser.add_option("--eta-mins", dest="eta_mins", type="string",
                     help="Array of Minimum Eta (Must be same length as --eta-maxs)", default="[1.25]")
    parser.add_option("--eta-maxs", dest="eta_maxs", type="string",
                     help="Array of Maximum Eta (Must be same length as --eta-mins)", default="[2.5]")
    parser.add_option("--pt-cuts", dest="pt_cuts", type="string",
                     help="Array of EMTF pt Cuts (GeV)", default="[22]")
    parser.add_option("--nEvents", dest="num_events", type="int",
                     help="Number of Events", default=-1)
    parser.add_option("-v","--verbose", dest="verbose",
                     help="Print extra debug info", default=False)
    options, args = parser.parse_args()
    
    options.pt_cuts = [float(pt) for pt in options.pt_cuts[1:-1].split(',')]
    options.eta_mins = [float(eta) for eta in options.eta_mins[1:-1].split(',')]
    options.eta_maxs = [float(eta) for eta in options.eta_maxs[1:-1].split(',')]

    if(len(options.eta_mins) != len(options.eta_maxs)):
        parser.print_help()
        sys.exit(1)

    if(options.verbose):
        print("#######################################################")
        print("#                  EFFICIENCY PLOTTER                 #")
        print("#######################################################")
        print("Loaded Options and Arguments. \n")

    target_file = fileHelper.getFile(args[1], options.verbose)
    
    if(options.verbose):
        print("\nTarget File Loaded\n")
        print("\nCollecting GEN_pt, GEN_eta, and BDTG_AWB_Sq\n")

    branch_GEN_pt = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/GEN_pt", options.verbose)
    branch_BDTG_AWB_Sq = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/BDTG_AWB_Sq", options.verbose)
    branch_GEN_eta = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/GEN_eta", options.verbose)
    unbinned_GEN_pt = branch_GEN_pt.arrays()['GEN_pt']
    unbinned_BDT_pt =  2**branch_BDTG_AWB_Sq.arrays()['BDTG_AWB_Sq']
    unbinned_GEN_eta = branch_GEN_eta.arrays()['GEN_eta']


    if(options.verbose):
        print("\nCreating ETA Mask and PT_cut MASK\n")
        print("Applying:\n   " + str(options.eta_mins) + " < eta < " + str(options.eta_maxs))
        print("   " + str(options.pt_cuts) + "GeV < pT")
    
    import efficiencyPlotter
    from matplotlib.backends.backend_pdf import PdfPages
    file_name_mod = 0
    if(not os.path.isdir(args[0])):
        os.mkdir(args[0])
    while(os.path.isfile(args[0] + "/plots" + str(file_name_mod) + ".pdf")):
        file_name_mod += 1;
    if(options.verbose):
        print("\nOpening PDF:" + args[0] + "/plots" + str(file_name_mod) + ".pdf" + "\n")
    
    pp = PdfPages(args[0] + "/plots" + str(file_name_mod) + ".pdf")

    pt_cuts = options.pt_cuts
    eta_mins = options.eta_mins
    eta_maxs = options.eta_maxs
    
    for pt_cut in pt_cuts:
        for i in range(0, len(eta_mins)):
            if(options.verbose):
                print("##############################################")
            unbinned_GEN_pt_eta_masked, unbinned_GEN_pt_pass_eta_masked = efficiencyPlotter.maskEvents(unbinned_GEN_pt, unbinned_BDT_pt, unbinned_GEN_eta, eta_mins[i], eta_maxs[i], pt_cut, options.verbose)
            fig = efficiencyPlotter.makeEfficiencyPlot(unbinned_GEN_pt_pass_eta_masked, unbinned_GEN_pt_eta_masked,
                                              "EMTF BDT Efficiency", "mode: " + str(options.emtf_mode)
                                              + "\n" + str(eta_mins[i]) + " < $\eta$ < " + str(eta_maxs[i])
                                              + "\n $p_T$ > " + str(pt_cut) + "GeV"
                                              + "\n" + "$N_{events}$: "+str(len(unbinned_GEN_pt_eta_masked)), pt_cut, options.verbose)
            fig.set_size_inches(6, 6)
            pp.savefig(fig)
    if(options.verbose):
        print("\nClosing PDF\n")
    pp.close()
    #plt.show()

def maskEvents(unbinned_GEN_pt, unbinned_BDT_pt, unbinned_GEN_eta, eta_min, eta_max, pt_cut,  verbose):
    if(verbose):
        print("\nCreating ETA Mask, BDT Scale Factor, and PT_cut MASK\n")
        print("Applying:\n   " + str(eta_min) + " < eta < " + str(eta_max))
        print("   " + str(pt_cut) + "GeV < pT")
    unbinned_eta_mask = ((eta_min < abs(unbinned_GEN_eta)) & (eta_max > abs(unbinned_GEN_eta)))

    unbinned_BDT_pt_eta_masked = unbinned_BDT_pt[unbinned_eta_mask]
    unbinned_GEN_pt_eta_masked = unbinned_GEN_pt[unbinned_eta_mask]

    unbinned_BDT_pt_eta_mask_scaled = helper.scaleBDTPtRun3(unbinned_BDT_pt_eta_masked)

    unbinned_BDT_pt_mask_eta_masked_scaled = (pt_cut < unbinned_BDT_pt_eta_mask_scaled)
    unbinned_GEN_pt_pass_eta_masked = unbinned_GEN_pt_eta_masked[unbinned_BDT_pt_mask_eta_masked_scaled]
    return unbinned_GEN_pt_eta_masked, unbinned_GEN_pt_pass_eta_masked

def getEfficiciencyHist(num_binned, den_binned):
    efficiency_binned = np.array([])
    efficiency_binned_err = [np.array([]), np.array([])]
    alpha = .32
    for i in range(0, len(den_binned)):
        if(den_binned[i] == 0):
            efficiency_binned = np.append(efficiency_binned, 0)
            efficiency_binned_err[0] = np.append(efficiency_binned_err[0], [0])
            efficiency_binned_err[1] = np.append(efficiency_binned_err[1], [1])
            continue
        efficiency_binned = np.append(efficiency_binned, [num_binned[i]/den_binned[i]])
        efficiency_binned_err[0] = np.append(efficiency_binned_err[0], [(efficiency_binned[i] - scipy.stats.beta.ppf(alpha/2, num_binned[i], den_binned[i]-num_binned[i]+1))/efficiency_binned[i]])
        efficiency_binned_err[1] = np.append(efficiency_binned_err[1], [(scipy.stats.beta.ppf(1 - alpha/2, num_binned[i]+1, den_binned[i]-num_binned[i]) - efficiency_binned[i])/efficiency_binned[i]])# - efficiency_binned[i]])
    return efficiency_binned, efficiency_binned_err

def makeEfficiencyPlot(num_unbinned, den_unbinned, title, textStr, pt_cut, verbose=False):

    if(verbose):
        print("\nInitializing Figures and Binning Histograms")

    #plt.style.use(hep.style.CMS)
    bins = [0,1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,60,70,80,90,100,150,200,250,300,400,500,600,700,800,900,1000]
    den_binned, den_bins = np.histogram(den_unbinned, bins, (0,1000))
    num_binned, num_bins = np.histogram(num_unbinned, bins, (0,1000))

    if(verbose):
        print("Generating Efficiency Plot")
    efficiency_binned, efficiency_binned_err = getEfficiciencyHist(num_binned, den_binned)

    fig2, ax = plt.subplots(2)
    fig2.suptitle(title)
    ax[0].errorbar([den_bins[i]+(den_bins[i+1]-den_bins[i])/2 for i in range(0, len(den_bins)-1)], efficiency_binned, yerr=efficiency_binned_err, xerr=[(bins[i+1] - bins[i])/2 for i in range(0, len(bins)-1)], linestyle="", marker=".", markersize=3, elinewidth = .5)#efficiency_binned_err
    ax[0].set_ylabel("Efficiency")
    ax[0].set_xlabel("$p_T$(GeV)")
    ax[0].axhline(linewidth=.1)        
    ax[0].axvline(linewidth=.1)
    ax[0].grid(color='lightgray', linestyle='--', linewidth=.25)
    ax[0].axhline(y=0.9, color='r', linewidth=.5, linestyle='--')
    ax[0].axvline(x=pt_cut, color='r', linewidth=.5, linestyle='--')
    props = dict(boxstyle='square', facecolor='white', alpha=1.0)
    # place a text box in upper left in axes coords
    ax[0].text(0.95, 0.05, textStr, transform=ax[0].transAxes, fontsize=10, verticalalignment='bottom', horizontalalignment='right', bbox=props)
    ax[0].set_ylim([0,1.2])
    ax[0].set_xlim([0,max(2*pt_cut,50)])
    for item in ([ax[0].title, ax[0].xaxis.label, ax[0].yaxis.label] + ax[0].get_xticklabels() + ax[0].get_yticklabels()):
        item.set_fontsize(8)

    ax[1].errorbar([den_bins[i]+(den_bins[i+1]-den_bins[i])/2 for i in range(0, len(den_bins)-1)], efficiency_binned, yerr=efficiency_binned_err, xerr=[(bins[i+1] - bins[i])/2 for i in range(0, len(bins)-1)], linestyle="", marker=".", markersize=3, elinewidth = .5)#efficiency_binned_err
    ax[1].set_ylabel("Efficiency")
    ax[1].set_xlabel("$p_T$(GeV)")
    ax[1].axhline(linewidth=.1)
    ax[1].axvline(linewidth=.1)
    ax[1].grid(color='lightgray', linestyle='--', linewidth=.25)
    ax[1].axhline(y=0.9, color='r', linewidth=.5, linestyle='--')
    ax[1].axvline(x=pt_cut, color='r', linewidth=.5, linestyle='--')
    props = dict(boxstyle='square', facecolor='white', alpha=1.0)
    # place a text box in upper left in axes coords
    ax[1].text(0.95, 0.05, textStr, transform=ax[1].transAxes, fontsize=10, verticalalignment='bottom', horizontalalignment='right', bbox=props)
    ax[1].set_ylim([0,1.2])
    for item in ([ax[1].title, ax[1].xaxis.label, ax[1].yaxis.label] + ax[1].get_xticklabels() + ax[1].get_yticklabels()):
        item.set_fontsize(8)

    if(verbose):
        print("Finished Creating Figures\n")
    return fig2

def makeEfficiencyPlotWithHistograms(num_unbinned, den_unbinned, title, verbose=False):

    if(verbose):
        print("\nInitializing Figures and Binning Histograms")

    #plt.style.use(hep.style.CMS)
    fig2 = plt.figure(constrained_layout=True)
    spec2 = gridspec.GridSpec(ncols=2, nrows=3, figure=fig2)
    
    f2_ax1 = fig2.add_subplot(spec2[:-1, :])
    den_binned, den_bins, den_bar_container = f2_ax1.hist(den_unbinned, 250, (0,1000), label="GEN_Pt")
    num_binned, num_bins, num_bar_container = f2_ax1.hist(num_unbinned, 250, (0,1000), label="GEN_Pt_pass",)
    f2_ax1.tick_params(labelbottom = False, bottom = False)
    f2_ax1.set_ylabel("Counts / 4GeV")
    f2_ax1.set_title(title)


    if(verbose):
        print("Generating Efficiency Plot")
    efficiency_binned, efficiency_binned_err = getEfficiciencyHist(num_binned, den_binned)
    f2_ax2 = fig2.add_subplot(spec2[2, :])
  
    #f2_ax2.plot(den_bins[0:-1], efficiency_binned)
    f2_ax2.errorbar(den_bins[0:-1], efficiency_binned, yerr=efficiency_binned_err, xerr=None, capsize=3, linestyle="", marker=".")#efficiency_binned_err
    f2_ax2.set_ylabel("Efficiency")
    f2_ax2.set_xlabel("$p_T$(GeV)")
    if(verbose):
        print("Finished Creating Figures\n")
    
