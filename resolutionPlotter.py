#!/usr/bin/env python3
#=====================
#adapted from EMTF_BDT_PerformancePlotter/efficiencyPlotter.py for Fall 2021
#using CMSSW_12_1_0_pre3 IIRC samples

import helpers.fileHelper as fileHelper

import warnings
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np #to plot the histogram and the Gaussian together, add below:
import scipy
from scipy.optimize import curve_fit
from scipy.optimize import OptimizeWarning
import awkward
import sys
import os
import helpers.helper as helper

if __name__ == "__main__":
    # This code will run if called from command line directly
    # python3 resolutionPlotter.py [options] outputDir inputFiles

    # Get input options from command line
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] outputDir outputFileName inputFile")
    parser.add_option("--emtf-mode", dest="emtf_mode", type="int",
                     help="EMTF Track Mode", default=15)
    parser.add_option("--cmssw-rel", dest="cmssw_rel", type="string",
                     help="USED FOR LABELS - CMSSW Release used in training preperation", default="CMSSW_12_1_0_pre3")
    parser.add_option("--eta-mins", dest="eta_mins", type="string",
                     help="Array of Minimum Eta (Must be same length as --eta-maxs)", default="[1.25]")
    parser.add_option("--eta-maxs", dest="eta_maxs", type="string",
                     help="Array of Maximum Eta (Must be same length as --eta-mins)", default="[2.5]")
    parser.add_option("--pt-ranges", dest="pt_ranges", type="string",
                     help="Array of EMTF pt ranges 0th to 1st, 1st to 2nd, 2nd to 3rd ... (in GeV)", default="[22]")
    parser.add_option("-v","--verbose", dest="verbose",
                     help="Print extra debug info", default=False)
    options, args = parser.parse_args()
    
    # Convert string arrays to float values
    options.pt_ranges = [float(pt) for pt in options.pt_ranges[1:-1].split(',')]
    if(len(options.pt_ranges) == 1):
        options.pt_ranges = [x*options.pt_ranges[0] for x in range(0, int(1000/options.pt_ranges[0]))]
    options.eta_mins = [float(eta) for eta in options.eta_mins[1:-1].split(',')] #do we need to include these?
    options.eta_maxs = [float(eta) for eta in options.eta_maxs[1:-1].split(',')]

    # Check to make sure inputs match and if not print help
    if(len(options.eta_mins) != len(options.eta_maxs)):
        parser.print_help()
        sys.exit(1)

    if(len(args) < 3):
        print("\n######### MUST INCLUDE ARGS: outputDir outputFileName inputFile #########\n")
        parser.print_help()
        sys.exit(1)
    if(len(args[1].split('.')) > 0):
        args[1] = args[1].split('.')[0]

    if(options.verbose):
        print("#######################################################")
        print("#                  RESOLUTION PLOTTER                 #")
        print("#######################################################")
        print("Loaded Options and Arguments. \n")

    # Get input file using fileHelper
    target_file = fileHelper.getFile(args[2], options.verbose)
    
    if(options.verbose):
        print("\nTarget File Loaded\n")
        print("\nCollecting GEN_pt, GEN_eta, BDTG_AWB_Sq, and TRK_hit_ids\n")

    # Collect branch using fileHelper
    branch_GEN_pt = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/GEN_pt", options.verbose)
    branch_BDTG_AWB_Sq = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/BDTG_AWB_Sq", options.verbose)
    branch_GEN_eta = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/GEN_eta", options.verbose)
    branch_TRK_hit_ids = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/TRK_hit_ids", options.verbose)
    
    # Group branches into dictionary for reference
    unbinned_EVT_data = {}
    unbinned_EVT_data['GEN_pt'] = branch_GEN_pt.arrays()['GEN_pt']
    unbinned_EVT_data['BDT_pt'] = 2**branch_BDTG_AWB_Sq.arrays()['BDTG_AWB_Sq']
    unbinned_EVT_data['GEN_eta'] = branch_GEN_eta.arrays()['GEN_eta']
    unbinned_EVT_data['TRK_hit_ids'] = branch_TRK_hit_ids.arrays()['TRK_hit_ids']
    
    # Open a matplotlib PDF Pages file
    pp = fileHelper.openPdfPages(args[0], args[1], options.verbose)

    if(options.verbose):
        print("\nCreating ETA Mask and PT_cut MASK\n")
        print("Applying:\n   " + str(options.eta_mins) + " < eta < " + str(options.eta_maxs))
        print("   " + str(options.pt_ranges) + "GeV < pT\n")    

    # Import resolutionPlotter to access its functions
    import resolutionPlotter
    pt_ranges = options.pt_ranges
    eta_mins = options.eta_mins
    eta_maxs = options.eta_maxs

    eta_value = [] #initial: pt_value, need eta_value
    means_inv_pt = []
    std_inv_pt = []
    means_pt = []
    std_pt = []

    # Go through each PT Cut and Eta Cuts and generate figures to save to pdf
    for j in range(0, len(pt_ranges)-1):
        for i in range(0, len(eta_mins)):
            if(options.verbose):
                print("###################   New Cuts   ###################")

            # Applying GEN_PT Mask for pt ranges
            unbinned_EVT_data_gen_pt_mask = helper.applyMaskToEVTData(
                                            unbinned_EVT_data,
                                            ["GEN_pt", "BDT_pt", "GEN_eta", "TRK_hit_ids"],
                                            ((pt_ranges[j] < abs(unbinned_EVT_data["GEN_pt"])) & (pt_ranges[j+1] > abs(unbinned_EVT_data["GEN_pt"]))),
                                            "GEN_pt CUT: " + str(pt_ranges[j]) + " < pT < " + str(pt_ranges[j+1]), options.verbose)

            # Apply ETA Mask
            unbinned_EVT_data_eta_masked = helper.applyMaskToEVTData(
                                            unbinned_EVT_data_gen_pt_mask,
                                            ["GEN_pt", "BDT_pt", "GEN_eta", "TRK_hit_ids"], 
                                            ((eta_mins[i] < abs(unbinned_EVT_data_gen_pt_mask["GEN_eta"])) & (eta_maxs[i] > abs(unbinned_EVT_data_gen_pt_mask["GEN_eta"]))),
                                            "ETA CUT: " + str(eta_mins[i]) + " < eta < " + str(eta_maxs[i]), options.verbose)

            # Generate resolution with eta input plot
            res_plot, means_inv_pt_elem, std_inv_pt_elem = resolutionPlotter.makeResolutionPlot(unbinned_EVT_data_eta_masked["GEN_pt"], unbinned_EVT_data_eta_masked["BDT_pt"],
                                               "EMTF BDT 1/pT Resolution \n Emulation in " + options.cmssw_rel, "mode: " + str(options.emtf_mode)
                                              + "\n" + str(eta_mins[i]) + " < $\eta$ < " + str(eta_maxs[i])
                                              + "\n" + str(pt_ranges[j]) + " < $p_T^{GEN}$ < " + str(pt_ranges[j+1]) + "GeV"
                                              + "\n" + "$N_{events}$: "+str(len(unbinned_EVT_data_eta_masked["GEN_pt"])), "1/pT", options.verbose)

            # Generate resolution with eta input plot
            res_plot_pt, means_pt_elem, std_pt_elem = resolutionPlotter.makeResolutionPlot(unbinned_EVT_data_eta_masked["GEN_pt"], unbinned_EVT_data_eta_masked["BDT_pt"],
                                               "EMTF BDT pT Resolution \n Emulation in " + options.cmssw_rel, "mode: " + str(options.emtf_mode)
                                              + "\n" + str(eta_mins[i]) + " < $\eta$ < " + str(eta_maxs[i])
                                              + "\n" + str(pt_ranges[j]) + " < $p_T^{GEN}$ < " + str(pt_ranges[j+1]) + "GeV"
                                              + "\n" + "$N_{events}$: "+str(len(unbinned_EVT_data_eta_masked["GEN_pt"])), "pT", options.verbose)

            eta_value.append((eta_mins[i] + eta_maxs[i])/2)#was pt_value.append((pt_ranges[j]+ pt_ranges[j+1])/2)
            means_inv_pt.append(means_inv_pt_elem)
            std_inv_pt.append(std_inv_pt_elem)
            means_pt.append(means_pt_elem)
            std_pt.append(std_pt_elem)

            # Increase size to square 6in x 6in on PDF
            res_plot.set_size_inches(6,6)
            res_plot_pt.set_size_inches(6,6)

            # Save figures to PDF
            pp.savefig(res_plot)
            pp.savefig(res_plot_pt)

    if(options.verbose):
        print("\n Creating resolution vs pt plots")
    fig_std, ax = plt.subplots(1)    
    ax.plot(eta_value, std_inv_pt,  linestyle="", marker=".", color="r", label="1/pT")#was (pt_value, ...)
    ax.plot(eta_value, std_pt,  linestyle="",  marker=".", color="b", label="pT")#was (pt_value, ...)
    ax.set_title("1/$p_T$ Resolution vs $\eta$")
    ax.set_xlabel("$\eta$")
    ax.set_ylabel("1/$p_T$ Resolution (as % $p_T$)")
    ax.set_ylim([0, 2])
    ax.grid(color='lightgray', linestyle='--', linewidth=.25)
    ax.legend()
    fig_mu, ax = plt.subplots(1)
    ax.plot(eta_value, means_inv_pt,  linestyle="",  marker=".", color="r", label="1/$p_T$")#was (pt_value, ...)
    ax.plot(eta_value, means_pt,  linestyle="", marker=".", color="b", label="$p_T$")#was (pt_value, ...)
    ax.set_title("$p_T$ Bias vs $\eta$")
    ax.set_xlabel("$\eta$")
    ax.set_ylabel("Bias")
    ax.set_ylim([-4, 4])
    ax.grid(color='lightgray', linestyle='--', linewidth=.25)
    ax.legend()
    fig_std.set_size_inches(6,6)
    fig_mu.set_size_inches(6,6)
    pp.savefig(fig_std)
    pp.savefig(fig_mu)
    plt.close('all')
    if(options.verbose):
        print("\nClosing PDF\n")
    #Close PDF
    pp.close()
    if(options.verbose):
        print("\nPDF has been closed\n")

    if(options.verbose):
        print("------------------------------------------------")
        print("Plots Complete! View them @ $cd " + args[0]  + " \n")



# This code will run if this file is imported
# import resolutionPlotter

def guassian(x, A, mu, sigma):
    return A * np.exp(-1.0 * (x - mu)**2 / (2 * sigma**2))

# Define Plotter here:
def makeResolutionPlot(unbinned_GEN_pt, unbinned_BDT_pt, title, textStr, resType, verbose=False):
    """
       makeResolutionVsPtPlot creates a binned histogram plot of the pseudo-bend resolution (1-GEN/BDT)
       and calls getResolutionHist. ResolutionHist will inform the scaling factor for the efficiency plots (2*sigma = scaling factor).
       INPUT:
             unbinned_GEN_pt - TYPE: numpy array-like
             unbinned_BDT_pt - TYPE: numpy array-like
             title - TYPE: String (Plot Title)
             textStr - TYPE: String (Text Box info)
        OUTPUT:
             fig - TYPE: MatPlotLib PyPlot Figure containing resolution plot
    """

    if(verbose):
        print("\nInitializing Figures and Binning Pt Histograms")

    # Define resolution (unbinned)
    res_unbinned = 1 - np.divide(unbinned_GEN_pt, unbinned_BDT_pt) #inverse pT relationship proportional to bending res

    if(resType == "pT"):
         res_unbinned = 1 - np.divide(unbinned_BDT_pt, unbinned_GEN_pt) 

    # Initializing bins and binning histograms from unbinned entries
    res_binned, res_bins = np.histogram(res_unbinned, 127, (-10,10)) #res_unbinned, bins=50, range (min - max pT)
 
    popt = [0,10,-1] # Randomly chosen so it will be off axes if no good fit was made
    with warnings.catch_warnings():
        warnings.simplefilter("error", OptimizeWarning)
        try:
            # Fit a the distribution to a guassian
            popt, pcov = curve_fit(guassian, xdata=[res_bins[i]+(res_bins[i+1]-res_bins[i])/2 for i in range(0, len(res_bins)-1)], ydata=res_binned,  p0=[80000, 0, .18])
            print(popt)
        except OptimizeWarning:
            print("Curve Fit Failed")
            popt = [0,10,-1]  # Randomly chosen so it will be off axes if no good fit was made

    x_fit = np.linspace(-10, 10, num=1000)
    y_fit = guassian(x_fit, popt[0], popt[1], popt[2])

    if(verbose):
        print("Generating Resolution Plot")
    fig2, ax = plt.subplots(1) #no subplots for resolution
    fig2.suptitle(title) #change to CMSSW_12_1_0_pre3 IIRC Res Sample
    ax.plot(x_fit, y_fit, label="Fit", linewidth=.25)

    # Plotting errors
    ax.errorbar([res_bins[i]+(res_bins[i+1]-res_bins[i])/2 for i in range(0, len(res_bins)-1)],
                    res_binned, xerr=[(res_bins[i+1] - res_bins[i])/2 for i in range(0, len(res_bins)-1)], #xerr = 10.24
                    linestyle="", marker=".", markersize=3, elinewidth = .5)

    # Setting labels and plot configs
    ax.set_ylabel("$N_{events}$") #y-axis = number of events
    ax.set_xlabel("$\eta$")#("$(1/p_T^{GEN} - 1/p_T^{BDT})/(1/p_T^{GEN})$") #x-axis = binned resolution
    if(resType == "pT"):
        ax.set_xlabel("$\eta$")#("$(p_T^{GEN} - p_T^{BDT})/(p_T^{GEN})$")
    ax.grid(color='lightgray', linestyle='--', linewidth=.25)
    
    # Adding a text box to bottom right
    props = dict(boxstyle='square', facecolor='white', alpha=1.0)
    ax.text(0.95, 0.95, textStr + "\n \n A=" + str(round(popt[0],4)) + "\n $\mu$=" + str(round(popt[1],4)) +"\n $\sigma$ = " + str(round(popt[2],5)), transform=ax.transAxes, fontsize=10, verticalalignment='top', horizontalalignment='right', bbox=props)
    ax.set_xlim([-12,12])
    # Setting all font sizes to be small (Less distracting)
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(8)


    if(verbose):
        print("Finished Creating Res Figures\n")
    # Returning the final figure with both plots drawn
    return fig2, popt[1], popt[2]
