import awkward
import numpy as np
from tqdm import tqdm

def getNumpyFromAwkward(awkward_array, verbose=False):
    if(verbose):
        print("\nConverting Awkward Array to Numpy Array\n")
    numpy_array = np.zeros(awkward.count(awkward_array))
    for i in tqdm(range(0, awkward.count(awkward_array))):
        numpy_array[i] = list(awkward_array[i].tolist().values())[0]

    return numpy_array

def getPtFromTrainingArray(training_var=np.ones(1), verbose=False):
    if(verbose):
        print("\nConverting from Traning Variable to Pt.")
        print("SCHEME: BDTG_AWB_SQ, Pt = 2^training_var\n")
    for i in range(0, len(training_var)):
        print(training_var[i][0], type(training_var[i]))
        training_var[i] = 2**(training_var[i])

def getMaskedAndConvertedArrays(awk_unbinned_GEN_pt, awk_unbinned_BDTG_AWB_Sq, awk_unbinned_GEN_eta, eta_min, eta_max, pt_cut, verbose=False):
    if(verbose):
        print("Converting from Awkward Array to Numpy Array and Applying Cuts:")
        print("     |" + str(eta_min) + " <= |eta| <= " + str(eta_max))
        print("     |" + str(pt_cut) + " < EMTF_pt")
    unbinned_GEN_pt = np.array([])
    unbinned_EMTF_pt = np.array([])
    unbinned_GEN_eta_mask = np.full(awkward.count(awk_unbinned_GEN_pt), True, dtype=bool)
    for i in tqdm(range(0, awkward.count(awk_unbinned_GEN_pt))):
        eta = getValueFromAwkward(awk_unbinned_GEN_eta, i)
        if(Math.abs(eta) >= eta_min and Math.abs(eta) <= eta_max):
            
            unbinned_GEN_pt = np.append(unbinned_GEN_pt, getValueFromAwkward(awk_unbinned_GEN_pt, i))
            EMTF_pt_value = getPtFromTrainingVar(getValueFromAwkward(awk_unbinned_BDTG_AWB_Sq, i))
            if(EMTF_pt_value > pt_cut):
                EMTF_pt_value = np.append(unbinned_EMTF_pt, EMTF_pt_value)
            unbinned_GEN_eta_mask[i] = True
        else:
            unbinned_GEN_eta_mask[i] = False
    if(verbose):
        print("Completed Converting and Cutting, Generated unbinned_GEN_pt, unbinned_EMTF_pt, unbinned_GEN_eta_mask")

    return unbinned_GEN_pt, unbinned_EMTF_pt, unbinned_GEN_eta_mask


def getValueFromAwkward(awkward_array, index):
    return list(awkward_array[index].tolist().values())[0]

def getPtFromTrainingVar(variable):
    return 2**variable



