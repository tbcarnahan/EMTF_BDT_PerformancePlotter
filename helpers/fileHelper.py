#!/usr/bin/env python3

import uproot
from matplotlib.backends.backend_pdf import PdfPages
import os

def getFile(file_path = "", verbose = False):
    if(verbose):
        print("Attempting to Fetch " + file_path)

    # Trying locally
    try:
        target_file  = uproot.open(file_path)
    except:
        if(verbose):
            print("Not Found Locally")
        target_file = None

    # If found locally then Return, else try FNAL EOS
    if(target_file):
        if(verbose):
            print("Found Locally. Loaded File using UpRoot")
        return target_file
    else:
        try:
            target_file = uproot.open('root://cmseos.fnal.gov/'+file_path)
        except:
            if(verbose):
                print("Not Found On FNAL EOS")
            target_file = None;

    if(target_file):
        if(verbose):
            print("Found on FNAL EOS. Loaded File using UpRoot")
        return target_file
    else:
        try:
            target_file = uproot.open('root://cms-xrd-global.cern.ch/'+file_path)
        except:
            if(verbose):
                print("Not Found Globally")
            target_file = None;

    if(target_file):
        if(verbose):
            print("Found on Globally. Loaded File using UpRoot")
        return target_file
    else:
        raise Exception("File " + file_path + " Not Found.")


def getBranch(target_file, path_to_branch, verbose):
    if(verbose):
        print("Trying to find " + path_to_branch + " in file.")
    
    keys = path_to_branch.split("/")

    if(verbose):
        print("Sperated into UpRoot Directory Keys " + str(keys)) 

    target = target_file
    for k in keys:
        target = target[k]

    if(verbose):
        print("Found branch: " + target.name + "\n") 

    return target


def openPdfPages(directory, file_name, verbose):
    file_name_mod = ""
    file_name_index = 0
    if(not os.path.isdir(directory)):
        os.mkdir(directory)
    while(os.path.isfile(directory + "/" + file_name + str(file_name_mod) + ".pdf")):
        file_name_mod = str(file_name_index)
        file_name_index += 1

    if(verbose):
        print("\nOpening PDF:" + directory + "/plots" + str(file_name_mod) + ".pdf" + "\n")

    pdf_pages = PdfPages(directory + "/" + file_name + str(file_name_mod) + ".pdf")
    return pdf_pages


