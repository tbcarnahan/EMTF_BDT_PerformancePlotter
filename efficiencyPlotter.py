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
    parser.add_option("--emtf-mode", dest="emtf_mode", type="int",
                     help="EMTF Track Mode", default=15)
    parser.add_option("--eta-mins", dest="eta_mins", type="string",
                     help="Array of Minimum Eta (Must be same length as --eta-maxs)", default="[1.25]")
    parser.add_option("--eta-maxs", dest="eta_maxs", type="string",
                     help="Array of Maximum Eta (Must be same length as --eta-mins)", default="[2.5]")
    parser.add_option("--pt-cuts", dest="pt_cuts", type="string",
                     help="Array of EMTF pt Cuts (GeV)", default="[22]")
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
        print("\nCollecting GEN_pt, GEN_eta, BDTG_AWB_Sq, and TRK_hit_ids\n")

    branch_GEN_pt = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/GEN_pt", options.verbose)
    branch_BDTG_AWB_Sq = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/BDTG_AWB_Sq", options.verbose)
    branch_GEN_eta = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/GEN_eta", options.verbose)
    branch_TRK_hit_ids = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/TRK_hit_ids", options.verbose)

    unbinned_EVT_data = {}

    unbinned_EVT_data['GEN_pt'] = branch_GEN_pt.arrays()['GEN_pt']
    unbinned_EVT_data['BDT_pt'] = 2**branch_BDTG_AWB_Sq.arrays()['BDTG_AWB_Sq']
    unbinned_EVT_data['GEN_eta'] = branch_GEN_eta.arrays()['GEN_eta']
    unbinned_EVT_data['TRK_hit_ids'] = branch_TRK_hit_ids.arrays()['TRK_hit_ids']


    unbinned_GEN_pt = branch_GEN_pt.arrays()['GEN_pt']
    unbinned_BDT_pt = helper.scaleBDTPtRun3(2**branch_BDTG_AWB_Sq.arrays()['BDTG_AWB_Sq'])
    unbinned_GEN_eta = branch_GEN_eta.arrays()['GEN_eta']
    unbinned_TRK_hit_ids = branch_TRK_hit_ids.arrays()['TRK_hit_ids']

    pp = fileHelper.openPdfPages(args[0], "plots", options.verbose)

    if(options.verbose):
        print("\nCreating ETA Mask and PT_cut MASK\n")
        print("Applying:\n   " + str(options.eta_mins) + " < eta < " + str(options.eta_maxs))
        print("   " + str(options.pt_cuts) + "GeV < pT\n")    

    import efficiencyPlotter

    pt_cuts = options.pt_cuts
    eta_mins = options.eta_mins
    eta_maxs = options.eta_maxs
    
    for pt_cut in pt_cuts:
        for i in range(0, len(eta_mins)):
            if(options.verbose):
                print("###################   New Cuts   ###################")

            unbinned_EVT_data_eta_masked = helper.applyMaskToEVTData(
                                            unbinned_EVT_data,
                                            ["GEN_pt", "BDT_pt", "GEN_eta", "TRK_hit_ids"], 
                                            ((eta_mins[i] < abs(unbinned_EVT_data["GEN_eta"])) & (eta_maxs[i] > abs(unbinned_EVT_data["GEN_eta"]))),
                                            "ETA CUT: " + str(eta_mins[i]) + " < eta < " + str(eta_maxs[i]), options.verbose)
            
            unbinned_EVT_data_eta_masked_pt_pass = helper.applyMaskToEVTData(
                                            unbinned_EVT_data_eta_masked,
                                            ["GEN_pt", "GEN_eta"],
                                            (pt_cut < unbinned_EVT_data_eta_masked["BDT_pt"]),
                                            "PT CUT: " + str(pt_cut) + " < pT", options.verbose)

            eta_fig = efficiencyPlotter.makeEfficiencyVsEtaPlot(unbinned_EVT_data_eta_masked_pt_pass["GEN_eta"], unbinned_EVT_data_eta_masked["GEN_eta"],
                                               "EMTF BDT Efficiency", "mode: " + str(options.emtf_mode)
                                              + "\n" + str(eta_mins[i]) + " < $\eta$ < " + str(eta_maxs[i])
                                              + "\n $p_T$ > " + str(pt_cut) + "GeV"
                                              + "\n" + "$N_{events}$: "+str(len(unbinned_EVT_data_eta_masked["GEN_eta"])), pt_cut, options.verbose)

            pt_fig = efficiencyPlotter.makeEfficiencyVsPtPlot(unbinned_EVT_data_eta_masked_pt_pass["GEN_pt"], unbinned_EVT_data_eta_masked["GEN_pt"],
                                              "EMTF BDT Efficiency", "mode: " + str(options.emtf_mode)
                                              + "\n" + str(eta_mins[i]) + " < $\eta$ < " + str(eta_maxs[i])
                                              + "\n $p_T$ > " + str(pt_cut) + "GeV"
                                              + "\n" + "$N_{events}$: "+str(len(unbinned_EVT_data_eta_masked["GEN_pt"])), pt_cut, options.verbose)

            pt_fig.set_size_inches(6, 6)
            eta_fig.set_size_inches(6,6)
            pp.savefig(pt_fig)
            pp.savefig(eta_fig)
    if(options.verbose):
        print("\nClosing PDF\n")
    pp.close()

def getEfficiciencyHist(num_binned, den_binned):
    efficiency_binned = np.array([])
    efficiency_binned_err = [np.array([]), np.array([])]
    for i in range(0, len(den_binned)):
        if(den_binned[i] == 0):
            efficiency_binned = np.append(efficiency_binned, 0)
            efficiency_binned_err[0] = np.append(efficiency_binned_err[0], [0])
            efficiency_binned_err[1] = np.append(efficiency_binned_err[1], [0])
            continue

        efficiency_binned = np.append(efficiency_binned, [num_binned[i]/den_binned[i]])

        nsuccess = num_binned[i]
        ntrial = den_binned[i]
        conf = 95.0
    
        if nsuccess == 0:
            alpha = 1 - conf / 100
            plo = 0.
            phi = scipy.stats.beta.ppf(1 - alpha, nsuccess + 1, ntrial - nsuccess)
        elif nsuccess == ntrial:
            alpha = 1 - conf / 100
            plo = scipy.stats.beta.ppf(alpha, nsuccess, ntrial - nsuccess + 1)
            phi = 1.
        else:
            alpha = 0.5 * (1 - conf / 100)
            plo = scipy.stats.beta.ppf(alpha, nsuccess + 1, ntrial - nsuccess)
            phi = scipy.stats.beta.ppf(1 - alpha, nsuccess, ntrial - nsuccess)

        efficiency_binned_err[0] = np.append(efficiency_binned_err[0], [(efficiency_binned[i] - plo)])
        efficiency_binned_err[1] = np.append(efficiency_binned_err[1], [(phi - efficiency_binned[i])])# - efficiency_binned[i]])

    return efficiency_binned, efficiency_binned_err

def makeEfficiencyVsPtPlot(num_unbinned, den_unbinned, title, textStr, xvline, verbose=False):

    if(verbose):
        print("\nInitializing Figures and Binning Pt Histograms")

    bins = [0,1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,60,70,80,90,100,150,200,250,300,400,500,600,700,800,900,1000]
    den_binned, den_bins = np.histogram(den_unbinned, bins, (0,1000))
    num_binned, num_bins = np.histogram(num_unbinned, bins, (0,1000))

    if(verbose):
        print("Generating Efficiency vs Pt Plot")
    efficiency_binned, efficiency_binned_err = getEfficiciencyHist(num_binned, den_binned)

    fig2, ax = plt.subplots(2)
    fig2.suptitle(title)
    ax[0].errorbar([den_bins[i]+(den_bins[i+1]-den_bins[i])/2 for i in range(0, len(den_bins)-1)], efficiency_binned, yerr=efficiency_binned_err, xerr=[(bins[i+1] - bins[i])/2 for i in range(0, len(bins)-1)], linestyle="", marker=".", markersize=3, elinewidth = .5)
    ax[0].set_ylabel("Efficiency")
    ax[0].set_xlabel("$p_T$(GeV)")
    ax[0].axhline(linewidth=.1)        
    ax[0].axvline(linewidth=.1)
    ax[0].grid(color='lightgray', linestyle='--', linewidth=.25)
    ax[0].axhline(y=0.9, color='r', linewidth=.5, linestyle='--')
    ax[0].axvline(x=xvline, color='r', linewidth=.5, linestyle='--')
    props = dict(boxstyle='square', facecolor='white', alpha=1.0)
    ax[0].text(0.95, 0.05, textStr, transform=ax[0].transAxes, fontsize=10, verticalalignment='bottom', horizontalalignment='right', bbox=props)
    ax[0].set_ylim([0,1.2])
    ax[0].set_xlim([0,max(2*xvline,50)])
    for item in ([ax[0].title, ax[0].xaxis.label, ax[0].yaxis.label] + ax[0].get_xticklabels() + ax[0].get_yticklabels()):
        item.set_fontsize(8)

    ax[1].errorbar([den_bins[i]+(den_bins[i+1]-den_bins[i])/2 for i in range(0, len(den_bins)-1)], efficiency_binned, yerr=efficiency_binned_err, xerr=[(bins[i+1] - bins[i])/2 for i in range(0, len(bins)-1)], linestyle="", marker=".", markersize=3, elinewidth = .5)
    ax[1].set_ylabel("Efficiency")
    ax[1].set_xlabel("$p_T$(GeV)")
    ax[1].axhline(linewidth=.1)
    ax[1].axvline(linewidth=.1)
    ax[1].grid(color='lightgray', linestyle='--', linewidth=.25)
    ax[1].axhline(y=0.9, color='r', linewidth=.5, linestyle='--')
    ax[1].axvline(x=xvline, color='r', linewidth=.5, linestyle='--')
    props = dict(boxstyle='square', facecolor='white', alpha=1.0)
    # place a text box in upper left in axes coords
    ax[1].text(0.95, 0.05, textStr, transform=ax[1].transAxes, fontsize=10, verticalalignment='bottom', horizontalalignment='right', bbox=props)
    ax[1].set_ylim([0,1.2])
    for item in ([ax[1].title, ax[1].xaxis.label, ax[1].yaxis.label] + ax[1].get_xticklabels() + ax[1].get_yticklabels()):
        item.set_fontsize(8)

    if(verbose):
        print("Finished Creating Pt Figures\n")
    return fig2

def makeEfficiencyVsEtaPlot(num_unbinned, den_unbinned, title, textStr, xvline, verbose=False):

    if(verbose):
        print("\nInitializing Figures and Binning eta Histograms")

    #plt.style.use(hep.style.CMS)
    den_binned, den_bins = np.histogram(den_unbinned, 50, (-2.5,2.5))
    num_binned, num_bins = np.histogram(num_unbinned, 50, (-2.5,2.5))

    if(verbose):
        print("Generating Efficiency vs eta Plot")
    efficiency_binned, efficiency_binned_err = getEfficiciencyHist(num_binned, den_binned)
    fig2, ax = plt.subplots(1)
    fig2.suptitle(title)
    ax.errorbar([den_bins[i]+(den_bins[i+1]-den_bins[i])/2 for i in range(0, len(den_bins)-1)], efficiency_binned, yerr=efficiency_binned_err, xerr=[(den_bins[i+1] - den_bins[i])/2 for i in range(0, len(den_bins)-1)], linestyle="", marker=".", markersize=3, elinewidth = .5)#efficiency_binned_err
    ax.set_ylabel("Efficiency")
    ax.set_xlabel("$\eta$")
    ax.axhline(linewidth=.1)
    ax.axvline(linewidth=.1)
    ax.grid(color='lightgray', linestyle='--', linewidth=.25)
    ax.axhline(y=0.9, color='r', linewidth=.5, linestyle='--')
    ax.axvline(x=xvline, color='r', linewidth=.5, linestyle='--')
    props = dict(boxstyle='square', facecolor='white', alpha=1.0)
    ax.text(0.95, 0.05, textStr, transform=ax.transAxes, fontsize=10, verticalalignment='bottom', horizontalalignment='right', bbox=props)
    ax.set_ylim([0,1.2])
    ax.set_xlim([-2.5,2.5])
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(8)
    if(verbose):
        print("Finished Creating Eta Figures\n")
    return fig2

