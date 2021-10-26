

def scaleBDTFunction(unbinned_BDT_pT, pt_scaling_A, pt_scaling_B):
  return (pt_scaling_A * unbinned_BDT_pT)/(1 - (pt_scaling_B * unbinned_BDT_pT))

def scaleBDTPtRun2(unbinned_BDT_pT):
  return scaleBDTFunction(unbinned_BDT_pT, 1.2, 0.015)

def scaleBDTPtRun3(unbinned_BDT_pT):
  return scaleBDTFunction(unbinned_BDT_pT, 1.3, 0.004)
