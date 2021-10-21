#!/usr/bin/env python3

import helpers.fileHelper as fileHelper

import hist
from hist import Hist
import mplhep as hep
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import awkward

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] outputDir inputFiles")
    parser.add_option("--emtf-mode", dest="emtf_mode", type="long",
                     help="EMTF Track Mode", default=15)
    parser.add_option("--eta-min", dest="eta_min", type="float",
                     help="Minimum Eta", default=1.25)
    parser.add_option("--eta-max", dest="eta_max", type="float",
                     help="Maximum Eta", default=2.5)
    parser.add_option("--pt-cut", dest="pt_cut", type="float",
                     help="EMTF pt Cut (GeV)", default=22)
    parser.add_option("--nEvents", dest="num_events", type="int",
                     help="Number of Events", default=-1)
    parser.add_option("-v","--verbose", dest="verbose",
                     help="Print extra debug info", default=False)
    options, args = parser.parse_args()

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
        print("Applying:\n   " + str(options.eta_min) + " < eta < " + str(options.eta_max))
        print("   " + str(options.pt_cut) + "GeV < pT")
    
    unbinned_eta_mask = ((options.eta_min < abs(unbinned_GEN_eta)) & (options.eta_max > abs(unbinned_GEN_eta)) )

    unbinned_BDT_pt = unbinned_BDT_pt[unbinned_eta_mask]
    unbinned_GEN_pt = unbinned_GEN_pt[unbinned_eta_mask]

    unbinned_BDT_pt_mask = (options.pt_cut < unbinned_BDT_pt)
    unbinned_GEN_pt_pass = unbinned_GEN_pt[unbinned_BDT_pt_mask]
    
    import efficiencyPlotter
    efficiencyPlotter.makeEfficiencyPlot(unbinned_GEN_pt_pass, unbinned_GEN_pt,
                                              "EMTF BDT Efficiency| mode:" + str(options.emtf_mode)
                                              + " | " + str(options.eta_min) + " < $\eta$ < " + str(options.eta_max)
                                              + " | " + str(options.pt_cut) + "GeV < $p_T$", options.verbose)

    if(options.verbose):
        print("\nDisplaying Plot\n")

    plt.show()

def getEfficiciencyHist(num_binned, den_binned):
    efficiency_binned = np.array([])
    for i in range(0, len(den_binned)):
        if(den_binned[i] == 0):
            efficiency_binned = np.append(efficiency_binned, 0)
            continue
        efficiency_binned = np.append(efficiency_binned, [num_binned[i]/den_binned[i]])
    return efficiency_binned

def makeEfficiencyPlot(num_unbinned, den_unbinned, title, verbose=False):

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

    efficiency_binned = getEfficiciencyHist(num_binned, den_binned)
    f2_ax2 = fig2.add_subplot(spec2[2, :])
    f2_ax2.plot(den_bins[0:-1], efficiency_binned)
    f2_ax2.set_ylabel("Efficiency")
    f2_ax2.set_xlabel("$p_T$(GeV)")

    if(verbose):
        print("Finished Creating Figures\n")
    
