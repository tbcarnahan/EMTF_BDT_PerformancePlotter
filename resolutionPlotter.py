#!/usr/bin/env python3

#using efficiencyPlotter.py and macros_Rice2020/resolutionPlots.py
#to solve: 1) what is resolution
#2) generate unbinned res (Gen_pT - BDT_pT)/GEN_pT --> make a hist by binning this (gaussian around 0) with x = res binned and y = # events in bin
#^resolve

import helpers.fileHelper as fileHelper

import hist
from hist import Hist
import mplhep as hep
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import numpy as np #to plot the histogram and the Gaussian together, add below:
#from scipy.stats import norm

#from array import *
#from termcolor import colored
#from optparse import OptionParser,OptionGroup

import scipy
import awkward
import sys
import os
import helpers.helper as helper ##keep?? (or keep line 5)

if __name__ == "__main__":
    # This code will run if called from command line directly
    # python3 resolutionPlotter.py [options] outputDir inputFiles

    # Get input options from command line
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
    
    # Convert string arrays to float values
    options.pt_cuts = [float(pt) for pt in options.pt_cuts[1:-1].split(',')]
    options.eta_mins = [float(eta) for eta in options.eta_mins[1:-1].split(',')] #do we need to include these?
    options.eta_maxs = [float(eta) for eta in options.eta_maxs[1:-1].split(',')]

    # Check to make sure inputs match and if not print help
    if(len(options.eta_mins) != len(options.eta_maxs)):
        parser.print_help()
        sys.exit(1)

    if(options.verbose):
        print("#######################################################")
        print("#                  RESOLUTION PLOTTER                 #")
        print("#######################################################")
        print("Loaded Options and Arguments. \n")

    # Get input file using fileHelper
    target_file = fileHelper.getFile(args[1], options.verbose)
    
    if(options.verbose):
        print("\nTarget File Loaded\n")
        print("\nCollecting GEN_pt, GEN_eta, BDTG_AWB_Sq, and TRK_hit_ids\n")

    # Collect branch using fileHelper
    branch_GEN_pt = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/GEN_pt", options.verbose)
    branch_BDTG_AWB_Sq = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/BDTG_AWB_Sq", options.verbose)
    branch_GEN_eta = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/GEN_eta", options.verbose)
    branch_TRK_hit_ids = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/TRK_hit_ids", options.verbose)
    branch_resolution = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/resolution", options.verbose)
    
    # Group branches into dictionary for reference
    unbinned_EVT_data = {}
    unbinned_EVT_data['GEN_pt'] = branch_GEN_pt.arrays()['GEN_pt']
    unbinned_EVT_data['BDT_pt'] = 2**branch_BDTG_AWB_Sq.arrays()['BDTG_AWB_Sq']
    unbinned_EVT_data['GEN_eta'] = branch_GEN_eta.arrays()['GEN_eta']
    unbinned_EVT_data['TRK_hit_ids'] = branch_TRK_hit_ids.arrays()['TRK_hit_ids']
    unbinned_EVT_data['resolution'] = branch_resolution.arrays()['resolution']
    
    # Open a matplotlib PDF Pages file
    pp = fileHelper.openPdfPages(args[0], "plots", options.verbose)

    if(options.verbose):
        print("\nCreating ETA Mask and PT_cut MASK\n")
        print("Applying:\n   " + str(options.eta_mins) + " < eta < " + str(options.eta_maxs))
        print("   " + str(options.pt_cuts) + "GeV < pT\n")    

    # Import resolutionPlotter to access its functions
    import resolutionPlotter
    pt_cuts = options.pt_cuts
    eta_mins = options.eta_mins
    eta_maxs = options.eta_maxs
    

    # Go through each PT Cut and Eta Cuts and generate figures to save to pdf
    for pt_cut in pt_cuts:
        for i in range(0, len(eta_mins)):
            if(options.verbose):
                print("###################   New Cuts   ###################")

            # Apply ETA Mask
            unbinned_EVT_data_eta_masked = helper.applyMaskToEVTData(
                                            unbinned_EVT_data,
                                            ["GEN_pt", "BDT_pt", "GEN_eta", "TRK_hit_ids"], 
                                            ((eta_mins[i] < abs(unbinned_EVT_data["GEN_eta"])) & (eta_maxs[i] > abs(unbinned_EVT_data["GEN_eta"]))),
                                            "ETA CUT: " + str(eta_mins[i]) + " < eta < " + str(eta_maxs[i]), options.verbose)
            
            # Apply PT Cut mask
            unbinned_EVT_data_eta_masked_pt_pass = helper.applyMaskToEVTData(
                                            unbinned_EVT_data_eta_masked,
                                            ["GEN_pt", "GEN_eta"],
                                            (pt_cut < unbinned_EVT_data_eta_masked["BDT_pt"]),
                                            "PT CUT: " + str(pt_cut) + " < pT", options.verbose)

            # Generate resolution vs eta plot
            eta_res = resolutionPlotter.makeResolutionVsEtaPlot(unbinned_EVT_data_eta_masked_pt_pass["GEN_eta"], unbinned_EVT_data_eta_masked["GEN_eta"],
                                               "EMTF BDT Resolution", "mode: " + str(options.emtf_mode)
                                              + "\n" + str(eta_mins[i]) + " < $\eta$ < " + str(eta_maxs[i])
                                              + "\n $p_T$ > " + str(pt_cut) + "GeV"
                                              + "\n" + "$N_{events}$: "+str(len(unbinned_EVT_data_eta_masked["GEN_eta"])), pt_cut, options.verbose)

            # Generate resolution vs pt plot
            pt_res = resolutionPlotter.makeResolutionVsPtPlot(unbinned_EVT_data_eta_masked_pt_pass["GEN_pt"], unbinned_EVT_data_eta_masked["GEN_pt"],
                                              "EMTF BDT Resolution", "mode: " + str(options.emtf_mode)
                                              + "\n" + str(eta_mins[i]) + " < $\eta$ < " + str(eta_maxs[i])
                                              + "\n $p_T$ > " + str(pt_cut) + "GeV"
                                              + "\n" + "$N_{events}$: "+str(len(unbinned_EVT_data_eta_masked["GEN_pt"])), pt_cut, options.verbose)
            # Increase size to square 6in x 6in on PDF
            pt_res.set_size_inches(6, 6)
            eta_res.set_size_inches(6,6)
            plt.close(pt_res)
            plt.close(eta_res)
            # Save figures to PDF
            pp.savefig(pt_res)
            pp.savefig(eta_res)
    if(options.verbose):
        print("\nClosing PDF\n")
    #Close PDF
    pp.close()
    if(options.verbose):
        print("\nPDF has been closed\n")

    if(options.verbose):
        print("------------------------------------------------")
        print("DONE.\n")



# This code will run if this file is imported
# import resolutionPlotter


## L145 in efficiencyPlotter as a reference:
def getResolutionHist(res_binned): #what are my inputs? binned x-axis and y = number events
    """
       getResolutionHist creates a binned histogram for (GEN_pT - BDT_pT)/GEN_pT and (1/GEN_pT - 1/BDT_pT)/(1/GEN_pT) for bending resolution (since pT is indirectly proportional to bending).
       Uses a Gaussian distribution to find how well we're tagging pT; the data closest to the mean is the most likely event distribution (we want a Gaussian central around 0).

       NOTE: resolution_binned_err[0] is lower error bar and resolution_binned_err[1] is upper error bar

       INPUT:
             res_binned - TYPE: numpy array-like
             
       OUTPUT:
             resolution_binned - TYPE: numpy array-like
             resolution_binned_err - TYPE: [numpy array-like, numpy array-like]
       
       
    """

#start here:

    # Initializing binned data
    resolution_binned = np.array([])
    resolution_binned_err = [np.array([]), np.array([])]

    # Iterating through each bin 
    for i in range(0, len(res_binned)):
        # Catching division by 0 error
        if(res_binned[i] == 0):
            resolution_binned = np.append(resolution_binned, 0)
            resolution_binned_err[0] = np.append(resolution_binned_err[0], [0])
            resolution_binned_err[1] = np.append(resolution_binned_err[1], [0])
           #continue

        # Filling resolution bins
        resolution_binned = np.append(resolution_binned) #, [res_binned[i]) #nix num/denom
       
     #Calculating Clopper-Pearson confidence interval
      #nsuccess = res_binned[i]
        #ntrial = den_binned[i]
        #conf = 95.0
    
        #if nsuccess == 0:
            #alpha = 1 - conf / 100
            #plo = 0.
            #phi = scipy.stats.beta.ppf(1 - alpha, nsuccess + 1, ntrial - nsuccess)
        #elif nsuccess == ntrial:
            #alpha = 1 - conf / 100
            #plo = scipy.stats.beta.ppf(alpha, nsuccess, ntrial - nsuccess + 1)
            #phi = 1.
        #else:
            #alpha = 0.5 * (1 - conf / 100)
            #plo = scipy.stats.beta.ppf(alpha, nsuccess + 1, ntrial - nsuccess)
            #phi = scipy.stats.beta.ppf(1 - alpha, nsuccess, ntrial - nsuccess)
        #Filling resolution error bins - from Clopper-Pearson
        #resolution_binned_err[0] = np.append(resolution_binned_err[0], [(resolution_binned[i] - plo)]) #plo no longer used; define Gaussian
        #resolution_binned_err[1] = np.append(resolution_binned_err[1], [(phi - resolution_binned[i])])# - resolution_binned[i]])

    return resolution_binned, resolution_binned_err #, resolution_binned_err ?

# Also need definition of Gaussian distribution code from numpy

def makeResolutionVsPtPlot(res_binned, title, textStr, verbose=False): #num_unbinned, den_unbinned, xvline (horizontal line) = nix
    """
       makeResolutionVsPtPlot creates a binned histogram plot of the resolution vs pT
       and calls getResolutionHist. Resolution vs pT is meant to give a probability distribution of what pT will occur near the mean.

       INPUT:
             res_unbinned - TYPE: numpy array-like
             title - TYPE: String (Plot Title)
             textStr - TYPE: String (Text Box info)

        OUTPUT:
             fig - TYPE: MatPlotLib PyPlot Figure containing resolution vs pt plot
    """

    if(verbose):
        print("\nInitializing Figures and Binning Pt Histograms")

    # Initializing bins and binning histograms from unbinned entries
    # Bins start small and get larger toward larger pT
    #bins = [0,1,2,3,4,5,6,7,8,9,10,12,14,16,18,
     #      20,22,24,26,28,30,32,34,36,38,40,42,
      #     44,46,48,50,60,70,80,90,100,150,200,
       #    250,300,400,500,600,700,800,900,1000]
    res_binned = np.histogram(res_unbinned, 50, (-256,256)) #res_unbinned, bins=50, range
                                                            
    # Define resolution:
                                                            
    res = numpy.divide(numpy.subtract(GEN_pt, BDT_pt), GEN_pt)
                                                            
    print(res) #or should this command be something more like plt.show(res)?

    if(verbose):
        print("Generating Resolution vs pT Plot")

    # Calling getResolutionHist to get Resolution with Gaussian and errors
    resolution_binned, resolution_binned_err = getResolutionHist(res_binned) #inputs here

    fig2, ax = plt.subplots(1) #no subplots for resolution
    fig2.suptitle(title) #change to CMSSW_12_1_0_pre3 IIRC Res Sample


    # Plotting errors
    ax.errorbar([bins[i]+(bins[i+1]-bins[i])/2 for i in range(0, len(bins)-1)],
                    resolution_binned, xerr=[(bins[i+1] - bins[i])/2 for i in range(0, len(bins)-1)], #xerr = 10.24
                    linestyle="", marker=".", markersize=3, elinewidth = .5)
   
    #Define Gaussian distribution:
    
    #Attempt 1:
    #generate unbinned res (Gen_pT - BDT_pT)/GEN_pT --> make a hist by binning this as a variable in x (gaussian around 0) with x = res binned and y = # events in bin
    #x_axis = np.arange(-50,50,0.1) #need to define the variable here
    #mean = statistics.mean(x_axis)
    #sd = statistics.stdev(x_axis)
    #ax.plot(x_axis, norm.pdf(x_axis, mean, sd))
    #ax.show()
    
    #Attempt 2: above seems archaic so try something like:
    #draw_res_axis_label = ["('GEN_pT' - 'BDT_pT') / 'GEN_pT'", "Number of events"]
    #draw_res_option = [""] #??
    #draw_res_label = ["Gaussian distribution"]
    #res_type = ["mu", "sigma"]
    ##define mu and sigma'''
    
    #3
    #Fit a normal distribution to the res data:
    mu, std = norm.fit(res)
    
    #use ax.hist or plt.hist?
    plt.hist(res, bins=50, density=True, alpha=0.6, color='g')
    xmin, xmax = plt.xlim()
    x = np.linspace(-256, 256) #xmin, xmax, num: int, optional (# samples to generate; default 50)
    p = norm.pdf(x, mu, std)
    #mu, sigma = 0, 0.1 #mean and std dev
    #s = np.random.default_rng().normal(mu, sigma, 1000)
    #plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bines - mu)**2/ (2 * sigma**2) ), linewidth=2, color='r')
    plt.plot(x, p, 'k', linewidth=2)
    title = "CMSSW_12_1_0_pre3 IIRC Res Fit results: mu = %.2f, std = %.2f" % (mu, std)
    plt.title(title)
    plt.show()
    
    # Setting Labels, vertical lines, horizontal line at 90% efficiency, and plot configs
    ax.set_ylabel("Number of events") #y-axis = number of events
    ax.set_xlabel("$p_T$(GeV)") #x-axis = binned resolution
    ax.grid(color='lightgray', linestyle='--', linewidth=.25)
    
    # Adding a text box to bottom right
    props = dict(boxstyle='square', facecolor='white', alpha=1.0)
    ax.text(0.95, 0.05, textStr, transform=ax[0].transAxes, fontsize=10, verticalalignment='bottom', horizontalalignment='right', bbox=props)
    # Setting axes limits to view turn on region
     #ax.set_ylim([0,1000]) #how many events? = leave out to maximize y
    ax.set_xlim([-256,256])
    # Setting all font sizes to be small (Less distracting)
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(8)


    if(verbose):
        print("Finished Creating Pt Figures\n")
    # Returning the final figure with both plots drawn
    return fig2

def makeResolutionVsInversepTPlot(res_unbinned, title, textStr, verbose=False):
    """
       makeResolutionVsInversepTPlot creates a binned histogram plot of the resolution vs 1/pT (or bending resolution)
       and calls getResolutionHist. The resolution is a marker of what distribution of bending will probably occur for a set mean of events.

       INPUT:
             res_unbinned - TYPE: numpy array-like
             title - TYPE: String (Plot Title)
             textStr - TYPE: String (Text Box Info)
             
       OUTPUT:
             fig - TYPE: MatPlotLib PyPlot Figure containing resolution vs bending plot
    """

    if(verbose):
        print("\nInitializing Figures and Binning eta Histograms")

    # Binning unbinned entries with 50 bins from inverse (-256,256)
    res_binned, bins = np.histogram(res_unbinned, 50, (-1/256,1/256))
    # num_binned, num_bins = np.histogram(num_unbinned, 50, (-2.5,2.5))

    if(verbose):
        print("Generating Resolution vs inverse pT Plot")

    # Calling getResolutionHist to get binned resolution and Gaussian and error
    resolution_binned, resolution_binned_err = getResolutionHist(res_binned)

    fig2, ax = plt.subplots(1)
    fig2.suptitle("CMSSW_12_1_0_pre3 IIRC Res Sample (1/pT)")

    # Define resolution:
                                                            
    res = numpy.divide(numpy.subtract(1/GEN_pt, 1/BDT_pt), 1/GEN_pt)
                                                            
    print(res)
                 
    # Plot the resolution and errors on the axes
    ax.errorbar([den_bins[i]+(den_bins[i+1]-den_bins[i])/2 for i in range(0, len(den_bins)-1)],
                 resolution_binned, yerr=resolution_binned_err, xerr=[(den_bins[i+1] - den_bins[i])/2 for i in range(0, len(den_bins)-1)],
                 linestyle="", marker=".", markersize=3, elinewidth = .5)
    
    # Setting Labels, vertical lines, and plot configs
    ax.set_ylabel("Number of events")
    ax.set_xlabel("Bending (1/pT) distribution") #binned resolution
    ax.grid(color='lightgray', linestyle='--', linewidth=.25)
    # Add text box in the bottom right
    props = dict(boxstyle='square', facecolor='white', alpha=1.0)
    ax.text(0.95, 0.05, textStr, transform=ax.transAxes, fontsize=10, verticalalignment='bottom', horizontalalignment='right', bbox=props)
    # Set x and y limits
    ax.set_xlim([-256,256])
    # Setting all font sizes to be small (Less distracting)
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(8)


    if(verbose):
        print("Finished Creating Inverse pT Figures\n")
    # Returning the final figure with both plots drawn
    return fig2

