#!/usr/bin/env python3

import helpers.fileHelper as fileHelper
import helpers.helper as helper

import hist
from hist import Hist
import mplhep
import matplotlib.pyplot as plt
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
    parser.add_option("-v","--verbose", dest="verbose",
                     help="Print extra debug info", default=False)
    parser.add_option("--tree-name", dest="tree_name", default = "f_logPtTarg_invPtWgt/TestTree")
    options, args = parser.parse_args()

    if(options.verbose):
        print("#######################################################")
        print("#                  EFFICIENCY PLOTTER                 #")
        print("#######################################################")
        print("Loaded Options and Arguments. \n")

    target_file = fileHelper.getFile(args[1], options.verbose)
    
    if(options.verbose):
        print("\nTarget File Loaded\n")
        print("\nCollecting GEN_pt and BDTG_AWB_Sq\n")

    branch_GEN_pt = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/GEN_pt", options.verbose)
    branch_BDTG_AWB_Sq = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/BDTG_AWB_Sq", options.verbose)
    awk_unbinned_GEN_pt = branch_GEN_pt.arrays()
    awk_unbinned_BDTG_AWB_Sq =  branch_BDTG_AWB_Sq.arrays()

    if(options.verbose):
        print("\nCollecting GEN_eta\n")

    branch_GEN_eta = fileHelper.getBranch(target_file,"f_logPtTarg_invPtWgt/TestTree/GEN_eta", options.verbose)
    awk_unbinned_GEN_eta = branch_GEN_eta.arrays()

    unbinned_GEN_pt, unbinned_EMTF_pt, unbinned_GEN_eta_mask = helper.getMaskedAndConvertedArrays(awk_unbinned_GEN_pt, awk_unbinned_BDTG_AWB_Sq,
                                                                                       awk_unbinned_GEN_eta, options.eta_min, options.eta_max,options.pt_cut, options.verbose)
    
    if(options.verbose):
        print("\nInitializing Histograms and Binning\n")

    GEN_pt = Hist(hist.axis.Regular(bins=256, start=0, stop=256, name="gen_pt"))
    EMTF_pt = Hist(hist.axis.Regular(bins=256, start=0, stop=256, name="emtf_pt"))
    GEN_pt.fill(unbinned_GEN_pt)
    EMTF_pt.fill(unbinned_EMTF_pt)

    fig = plt.figure(figsize=(10, 8))
    main_ax_artists, sublot_ax_arists = EMTF_pt.plot_ratio(
        GEN_pt,
        rp_num_label="GEN_pt",
        rp_denom_label="EMTF_pt",
        rp_uncert_draw_type="line",
        rp_uncertainty_type="efficiency",
    )


    if(options.verbose):
        print("\nDisplaying Plot\n")

    plt.show()


    



