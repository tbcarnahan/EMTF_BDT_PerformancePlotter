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
    # This code will run if called from command line directly
    # python3 plotter.py [options] outputDir inputFiles


    # Get input options from command line
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] outputDir outputFileName inputFile")
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
    parser.add_option("-e","--eff", dest="makeEfficiency",
                     help="Make efficiency plots", default=False)
    parser.add_option("-r","--res", dest="makeResolution",
                     help="Make resolution plots", default=False)
    options, args = parser.parse_args()

    # Convert string arrays to float values
    options.pt_cuts = [float(pt) for pt in options.pt_cuts[1:-1].split(',')]
    options.eta_mins = [float(eta) for eta in options.eta_mins[1:-1].split(',')]
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
        print("#                 BDT PERFORMANCE PLOTTER             #")
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
    branch_GEN_phi = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/GEN_phi", options.verbose)
    branch_TRK_hit_ids = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/TRK_hit_ids", options.verbose)

    # Group branches into dictionary for reference
    unbinned_EVT_data = {}
    unbinned_EVT_data['GEN_pt'] = branch_GEN_pt.arrays()['GEN_pt']
    unbinned_EVT_data['BDT_pt'] = helper.scaleBDTPtRun2(2**branch_BDTG_AWB_Sq.arrays()['BDTG_AWB_Sq'])
    unbinned_EVT_data['GEN_eta'] = branch_GEN_eta.arrays()['GEN_eta']
    unbinned_EVT_data['GEN_phi'] = branch_GEN_phi.arrays()['GEN_phi']
    unbinned_EVT_data['TRK_hit_ids'] = branch_TRK_hit_ids.arrays()['TRK_hit_ids']

    # Open a matplotlib PDF Pages file
    pp = fileHelper.openPdfPages(args[0], args[1], options.verbose)

    if(options.verbose):
        print("\nCreating ETA Mask and PT_cut MASK\n")
        print("Applying:\n   " + str(options.eta_mins) + " < eta < " + str(options.eta_maxs))
        print("   " + str(options.pt_cuts) + "GeV < pT\n")

    # Import other plotter to access their functions
    import efficiencyPlotter
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
                                            ["GEN_pt", "BDT_pt", "GEN_eta", "GEN_phi", "TRK_hit_ids"],
                                            ((eta_mins[i] < abs(unbinned_EVT_data["GEN_eta"])) & (eta_maxs[i] > abs(unbinned_EVT_data["GEN_eta"]))),
                                            "ETA CUT: " + str(eta_mins[i]) + " < eta < " + str(eta_maxs[i]), options.verbose)

            # Apply PT Cut mask
            unbinned_EVT_data_eta_masked_pt_pass = helper.applyMaskToEVTData(
                                            unbinned_EVT_data_eta_masked,
                                            ["GEN_pt", "GEN_eta", "GEN_phi"],
                                            (pt_cut < unbinned_EVT_data_eta_masked["BDT_pt"]),
                                            "PT CUT: " + str(pt_cut) + " < pT", options.verbose)

            # Apply Plataue Cut
            unbinned_EVT_data_eta_masked_plataue = helper.applyMaskToEVTData(
                                            unbinned_EVT_data_eta_masked,
                                            ["GEN_pt", "BDT_pt", "GEN_eta", "GEN_phi", "TRK_hit_ids"],
                                            (pt_cut+10 < unbinned_EVT_data_eta_masked["GEN_pt"]),
                                            "GEN PT CUT: " + str(pt_cut) + " < pT", options.verbose)
            # Apply PT Cut to Plataue
            unbinned_EVT_data_eta_masked_plataue_pt_pass = helper.applyMaskToEVTData(
                                            unbinned_EVT_data_eta_masked_plataue,
                                            ["GEN_pt", "GEN_eta", "GEN_phi"],
                                            (pt_cut < unbinned_EVT_data_eta_masked_plataue["BDT_pt"]),
                                            "Plataue PT CUT: " + str(pt_cut) + " < pT", options.verbose)
            ### PLOTS WILL BE MADE HERE ###
            if(options.makeEfficiency):
                # Generate efficiency vs eta plot
                eta_fig = efficiencyPlotter.makeEfficiencyVsEtaPlot(unbinned_EVT_data_eta_masked_plataue_pt_pass["GEN_eta"], unbinned_EVT_data_eta_masked_plataue["GEN_eta"],
                                               "EMTF BDT Efficiency \n $\epsilon$ vs $\eta$", "mode: " + str(options.emtf_mode)
                                              + "\n" + str(eta_mins[i]) + " < $\eta$ < " + str(eta_maxs[i])
                                              + "\n $p_T$ > " + str(pt_cut) + "GeV"
                                              + "\n" + "$N_{events}$: "+str(len(unbinned_EVT_data_eta_masked_plataue["GEN_eta"])), pt_cut, options.verbose)
                # Generate efficiency vs phi plot
                phi_fig = efficiencyPlotter.makeEfficiencyVsPhiPlot(unbinned_EVT_data_eta_masked_plataue_pt_pass["GEN_phi"], unbinned_EVT_data_eta_masked_plataue["GEN_phi"],
                                               "EMTF BDT Efficiency \n $\epsilon$ vs $\phi$", "mode: " + str(options.emtf_mode)
                                              + "\n" + str(eta_mins[i]) + " < $\eta$ < " + str(eta_maxs[i])
                                              + "\n $p_T$ > " + str(pt_cut) + "GeV"
                                              + "\n" + "$N_{events}$: "+str(len(unbinned_EVT_data_eta_masked_plataue["GEN_phi"])), pt_cut, options.verbose)

                # Generate efficiency vs pt plot
                pt_fig = efficiencyPlotter.makeEfficiencyVsPtPlot(unbinned_EVT_data_eta_masked_pt_pass["GEN_pt"], unbinned_EVT_data_eta_masked["GEN_pt"],
                                              "EMTF BDT Efficiency \n $\epsilon$ vs $p_T$", "mode: " + str(options.emtf_mode)
                                              + "\n" + str(eta_mins[i]) + " < $\eta$ < " + str(eta_maxs[i])
                                              + "\n $p_T$ > " + str(pt_cut) + "GeV"
                                              + "\n" + "$N_{events}$: "+str(len(unbinned_EVT_data_eta_masked["GEN_pt"])), pt_cut, options.verbose)            

                eta_fig.set_size_inches(6, 6)
                phi_fig.set_size_inches(6, 6)
                pt_fig.set_size_inches(6, 6)
                # Save figures to PDF
                pp.savefig(eta_fig)
                pp.savefig(phi_fig)
                pp.savefig(pt_fig)
            if(options.makeResolution):
                print("RESOLUTION PLOTS WILL BE HERE")
            ###############################


    if(options.verbose):
        print("\nClosing PDF\n")
    #Close PDF
    pp.close()
    if(options.verbose):
        print("\nPDF has been closed\n")

    if(options.verbose):
        print("------------------------------------------------")
        print("DONE.\n")


