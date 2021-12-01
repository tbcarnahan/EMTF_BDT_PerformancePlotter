#!/usr/bin/env python3
#=====================
#adapted from EMTF_BDT_PerformancePlotter/efficiencyPlotter.py for Fall 2021
#using CMSSW_12_1_0_pre3 IIRC samples

import helpers.fileHelper as fileHelper

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
#import matplotlib.mlab as mlab
import numpy as np

import scipy
from scipy.stats import norm
from scipy.optimize import curve_fit #for Gaussian

import awkward
import sys
import os
import helpers.helper as helper

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
    
    # Group branches into dictionary for reference
    unbinned_EVT_data = {}
    unbinned_EVT_data['GEN_pt'] = branch_GEN_pt.arrays()['GEN_pt']
    unbinned_EVT_data['BDT_pt'] = 2**branch_BDTG_AWB_Sq.arrays()['BDTG_AWB_Sq']
    unbinned_EVT_data['GEN_eta'] = branch_GEN_eta.arrays()['GEN_eta']
    unbinned_EVT_data['TRK_hit_ids'] = branch_TRK_hit_ids.arrays()['TRK_hit_ids']
    
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
    GEN_pt_cuts = [[0,10],[10,20],[20,30],[30,40],[40,50],[50,75], [75,100], [100,150],[150,200]]
    for j in range(0, len(GEN_pt_cuts)):
        for i in range(0, len(eta_mins)):
            if(options.verbose):
                print("###################   New Cuts   ###################")
#Future iteration: apply GEN_PT Mask for low, med, high pT muons                                                                 
            unbinned_EVT_data_GEN_pT_pass = helper.applyMaskToEVTData(                                                            
                                            unbinned_EVT_data,                                                                   
                                            ["GEN_pt","BDT_pt", "GEN_eta", "TRK_hit_ids"],                                                  
                                            ((GEN_pt_cuts[j][0] < unbinned_EVT_data["GEN_pt"]) & (unbinned_EVT_data["GEN_pt"] < GEN_pt_cuts[j][1])),
                                            "GEN_PT CUT", options.verbose)                                            


            # Apply ETA Mask
            unbinned_EVT_data_eta_masked = helper.applyMaskToEVTData(
                                            unbinned_EVT_data_GEN_pT_pass,
                                            ["GEN_pt", "BDT_pt", "GEN_eta", "TRK_hit_ids"], 
                                            ((eta_mins[i] < abs(unbinned_EVT_data_GEN_pT_pass["GEN_eta"])) & (eta_maxs[i] > abs(unbinned_EVT_data_GEN_pT_pass["GEN_eta"]))),
                                            "ETA CUT: " + str(eta_mins[i]) + " < eta < " + str(eta_maxs[i]), options.verbose)

            #Future iteration: apply GEN_PT Mask for low, med, high pT muons
            """ unbinned_EVT_data_eta_masked_pt_pass = helper.applyMaskToEVTData(
                                            unbinned_EVT_data_eta_masked,
                                            ["GEN_pt","BDT_pt", "TRK_hit_ids"],
                                            (pt_cut < unbinned_EVT_data_eta_masked["BDT_pt"]),
                                            "PT CUT: " + str(pt_cut) + " < pT", options.verbose)
            """

            # Generate resolution with eta input plot
            res_plot = resolutionPlotter.makeResolutionPlot(unbinned_EVT_data_eta_masked["GEN_pt"], unbinned_EVT_data_eta_masked["BDT_pt"],
                                               "EMTF BDT Resolution \n Emulation in CMSSW_12_1_0_pre3", "mode: " + str(options.emtf_mode)
                                              + "\n" + str(eta_mins[i]) + " < $\eta$ < " + str(eta_maxs[i])
                                              + "\n" + str(GEN_pt_cuts[j][0]) + " < $p_T^{GEN}$ < " + str(GEN_pt_cuts[j][1]) + "GeV"
                                              + "\n" + "$N_{events}$: "+str(len(unbinned_EVT_data_eta_masked["GEN_pt"])), options.verbose)
            
            # Increase size to square 6in x 6in on PDF
            res_plot.set_size_inches(6,6)

            # Save figures to PDF
            pp.savefig(res_plot)

    if(options.verbose):
        print("\nClosing PDF\n")
    #Close PDF
    pp.close()
    if(options.verbose):
        print("\nPDF has been closed\n")

    if(options.verbose):
        print("------------------------------------------------")
        print("Plots Complete! View them @ $cd resolutionPlots \n")



# This code will run if this file is imported
# import resolutionPlotter

def getResolutionHist(res_binned): #want binned x-axis of bending resolution and y = number events
    """
       getResolutionHist creates a binned histogram for (GEN_pT - BDT_pT)/GEN_pT and (1/GEN_pT - 1/BDT_pT)/(1/GEN_pT) for bending resolution (since pT is indirectly proportional to bending).
       Uses a Gaussian distribution to find how well we're tagging pT; the data closest to the mean is the most likely event distribution (we want a Gaussian central around 0).

       NOTE: resolution_binned_err[0] is lower error bar and resolution_binned_err[1] is upper error bar

       INPUT:
             res_binned - TYPE: numpy array-like
             
       OUTPUT:
             resolution_binned - TYPE: numpy array-like
             resolution_binned_err - TYPE: [numpy array-like, numpy array-like]
       

# Start code here:

# Introduce Error Scheme

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
        resolution_binned = np.append(resolution_binned) #, [res_binned[i])
       
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
    """
    pass

# Define Plotter here:

def makeResolutionPlot(unbinned_GEN_pt, unbinned_BDT_pt, title, textStr, verbose=False): #inputs = GEN and BDT pT (match L110)
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
    #for x in range(0,100):
        #print(unbinned_GEN_pt[x], unbinned_BDT_pt[x], 1-unbinned_GEN_pt[x]/unbinned_BDT_pt[x])
    # Define resolution (unbinned)
    res_unbinned = 1 - np.divide(unbinned_GEN_pt, unbinned_BDT_pt) #inverse pT relationship proportional to bending res
    res_unbinned_masked = res_unbinned[((res_unbinned < .4) & (res_unbinned > -.4))]
    # Initializing bins and binning histograms from unbinned entries
    res_binned, res_bins = np.histogram(res_unbinned, 51, (-2,2), density=True) #res_unbinned, bins=50, range (min - max pT), density=True means normalize data at bins (np.histogram(res_unbinned,500,(-256,256),density=True))
                                                            
    if(verbose):
        print("Generating Resolution Plot")
    fig2, ax = plt.subplots(1) #no subplots for resolution
    fig2.suptitle(title) #change to CMSSW_12_1_0_pre3 IIRC Res Sample


    # Plotting errors
    ax.errorbar([res_bins[i]+(res_bins[i+1]-res_bins[i])/2 for i in range(0, len(res_bins)-1)],
                    res_binned, xerr=[(res_bins[i+1] - res_bins[i])/2 for i in range(0, len(res_bins)-1)], #xerr = 10.24
                    linestyle="", marker=".", markersize=3, elinewidth = .5)

#Gaussian Attempts:

#++++++++++++++++++++++++++++++++++++ (Lessons learned)

#+++++++++++++++++++++++++++++ mlab doesn't work as well as scipy.stats.norm.pdf
   #best fit of data
    #(mu,sigma) = norm.fit(res_unbinned)
   #histo
    #n, bins, patches = plt.hist(res_unbinned, 50, normed=1, facecolor='blue', alpha=0.7)
   #best fit line
    #y = mlab.normpdf(50, mu, sigma)
    #l = plt.plot(50, y, 'r--', linewidth=2)
    #plt.show()
#+++++++++++++++++++++++++++++++++++ Need to define Gaussian distribution:

#
    #x_axis = np.arange(-50,50,0.1) #need to define the variable here
    #mean = statistics.mean(x_axis)
    #sd = statistics.stdev(x_axis)
    #ax.plot(x_axis, norm.pdf(x_axis, mean, sd))
    #ax.show()

#+++++++++++++++++++++++++++++++ Make sure indentations match above functions
#Keep for future: This one actually gives us something but is matching the wrong data set...

    #Fit a normal distribution to the res data:
    mu, std = norm.fit(res_unbinned_masked)
    #print(np.mean(res_unbinned), np.std(res_unbinned))
    #print(norm.fit(res_unbinned))
    #fit_line = scipy.stats.norm.pdf(50, mu, sigma)#print(mu,sigma)
    #plt.plot(50, fit_line)
    print(mu,std)

    #plt.hist(res_unbinned, bins=500, density=True, alpha=0.6, color='b')
    #xmin, xmax = plt.xlim()
    x = np.linspace(-0.4, 0.4)#plot fit #xmin, xmax, num:  int, optional (# samples to generate; default 50)
    p = norm.pdf(x, mu, std)
#    p = p*np.max(res_binned)#scale up to peak
    ax.plot(x,p) #was ax.plot(x,p)
    
    
    #attempt at defining gaussian
    def Gauss(x, A, B, C):
        y = A*np.exp(-1*(x-B)**2/C**2)
        return y
    parameters, covariance = curve_fit(Gauss, res_bins[0:-1], res_binned)#curve_fit(model f(x), xdata, ydata, p0=None, sigma #add ydata = Num of events

    fit_A = parameters[0]
    fit_B = parameters[1]
    fit_C = parameters[2]

    print(fit_A, fit_B, fit_C)

    fit_y = Gauss(res_unbinned, fit_A, fit_B, fit_C)
    #ax.plot(res_unbinned, fit_y, '-', label='fit')

#++++++++++++++++++++++ python3 tutorial: https://www.geeksforgeeks.org/python-gaussian-fit/

    #Extraneous info addendum for above "Keep for future":
    #title = "Fit results: mu = %.2f, std = %.2f" % (mu,std)
    #plt.title(title)
    #plt.show()
    #mu, sigma = 0, 0.1 #mean and std dev
    #s = np.default_rng().normal(mu, sigma, 1000)
    
    #plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - mu)**2/ (2 * sigma**2) ), linewidth=2, color='r')
    #plt.plot(x, p, 'k', linewidth=2)
    #title = "CMSSW_12_1_0_pre3 IIRC Res Fit results: mu = %.2f, std = %.2f" % (mu, std)
    #plt.title(title)
    #plt.show()

    # Setting labels and plot configs
    ax.set_ylabel("a.u.") #y-axis = number of events
    ax.set_xlabel("$(1/p_T^{GEN} - 1/p_T^{BDT})/(1/p_T^{GEN})$") #x-axis = binned resolution
    ax.grid(color='lightgray', linestyle='--', linewidth=.25)
    
    # Adding a text box to bottom right
    props = dict(boxstyle='square', facecolor='white', alpha=1.0)
    ax.text(0.95, 0.95, textStr + "\n $\mu$ = " + str(mu) + "\n $\sigma$ = " + str(std), transform=ax.transAxes, fontsize=10, verticalalignment='top', horizontalalignment='right', bbox=props)
    ax.set_xlim([-2.5,2.5])
    # Setting all font sizes to be small (Less distracting)
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(8)


    if(verbose):
        print("Finished Creating Res Figures\n")
    # Returning the final figure with both plots drawn
    return fig2
